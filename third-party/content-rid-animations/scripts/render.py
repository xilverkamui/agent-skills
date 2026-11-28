# -*- coding: utf-8 -*-
"""
render.py - render video bisu (paralel per potongan) atau stills QC.

Pakai:
  python3 render.py <folder_proyek>                 # render penuh -> out/video_bisu.mp4 + out/events.json
  python3 render.py <folder_proyek> --stills auto   # lembar QC (tengah tiap adegan) -> out/qc/sheet.jpg
  python3 render.py <folder_proyek> --stills 1.5,7,12.2
  python3 render.py <folder_proyek> --jobs 4

<folder_proyek>/proyek.json berisi: judul, ukuran [W,H], fps, vo (path relatif / null), adegan [...]
"""
import os, sys, json, math, time, subprocess, argparse
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import timing
from scenes import Scene, TR


def muat(projdir):
    proj = json.load(open(os.path.join(projdir, "proyek.json")))
    W, H = proj.get("ukuran", [1920, 1080])
    fps = int(proj.get("fps", 30))
    vo = proj.get("vo")
    vo = os.path.join(projdir, vo) if vo and not os.path.isabs(vo) else vo
    if vo and not os.path.exists(vo):
        sys.exit(f"[GAGAL] file VO tidak ditemukan: {vo}")
    ts, total = timing.jadwal(proj["adegan"], vo)
    return proj, W, H, fps, vo, ts, total


class Film:
    def __init__(self, projdir):
        self.proj, self.W, self.H, self.fps, self.vo, self.ts, self.total = muat(projdir)
        self.lv = timing.levels(self.vo, self.fps, self.total) if self.vo else None
        self.scenes = [Scene(dict(sc), self.W, self.H, a, b, self.fps, self.lv, sim_talk=self.vo is None)
                       for sc, (a, b) in zip(self.proj["adegan"], self.ts)]
        self.N = int(math.ceil(self.total * self.fps))

    def frame(self, f):
        T = f / self.fps
        i = 0
        while i + 1 < len(self.scenes) and T >= self.scenes[i + 1].start:
            i += 1
        sc = self.scenes[i]
        img = sc.frame(T - sc.start, f)
        if i > 0 and T - sc.start < TR:
            pv = self.scenes[i - 1]
            a = (T - sc.start) / TR
            img = Image.blend(pv.frame(T - pv.start, f), img, a * a * (3 - 2 * a))
        return img


_FILM = None


def _init(projdir):
    global _FILM
    _FILM = Film(projdir)


def _chunk(args):
    a, b, path = args
    F = _FILM
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{F.W}x{F.H}", "-r", str(F.fps),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(F.fps), path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(F.frame(f).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    return path, b - a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyek")
    ap.add_argument("--stills")
    ap.add_argument("--jobs", type=int, default=max(1, min(8, os.cpu_count() or 2)))
    a = ap.parse_args()
    projdir = os.path.abspath(a.proyek)
    out = os.path.join(projdir, "out"); os.makedirs(out, exist_ok=True)

    if a.stills:
        F = Film(projdir)
        if a.stills == "auto":
            times = [min(s.end - 0.05, s.start + max(0.3, s.dur * 0.75)) for s in F.scenes]
        else:
            times = [float(x) for x in a.stills.split(",")]
        qc = os.path.join(out, "qc"); os.makedirs(qc, exist_ok=True)
        ims = []
        for t in times:
            im = F.frame(int(t * F.fps)).convert("RGB"); ims.append(im)
            im.save(os.path.join(qc, f"t{t:06.2f}.jpg"), quality=88)
        cols = 3 if F.W >= F.H else 4
        tw = 640 if F.W >= F.H else 360
        th = int(tw * F.H / F.W)
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 8, rows * th + (rows + 1) * 8), (30, 30, 40))
        for i, im in enumerate(ims):
            r, c = divmod(i, cols)
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (8 + c * (tw + 8), 8 + r * (th + 8)))
        sheet.save(os.path.join(qc, "sheet.jpg"), quality=88)
        print("STILLS", os.path.join(qc, "sheet.jpg"))
        for s in F.scenes:
            print(f"  adegan {F.scenes.index(s)+1:2d} {s.s.get('tipe'):10s} {s.start:6.2f}-{s.end:6.2f}")
        return

    t0 = time.time()
    F = Film(projdir)
    json.dump({"durasi": F.total, "fps": F.fps, "ukuran": [F.W, F.H], "vo": F.vo,
               "adegan": [{"tipe": s.s.get("tipe"), "mulai": round(s.start, 3), "selesai": round(s.end, 3)} for s in F.scenes]},
              open(os.path.join(out, "timeline.json"), "w"), indent=1)
    ev = sorted(e for s in F.scenes for e in s.events())
    json.dump(ev, open(os.path.join(out, "events.json"), "w"))
    wd = os.path.join(out, "work"); os.makedirs(wd, exist_ok=True)
    n = a.jobs
    step = math.ceil(F.N / n)
    jobs = [(i * step, min(F.N, (i + 1) * step), os.path.join(wd, f"c{i:02d}.mp4")) for i in range(n) if i * step < F.N]
    print(f"render {F.N} frame ({F.total:.1f} dtk) {F.W}x{F.H}@{F.fps} pakai {len(jobs)} proses ...", flush=True)
    del F
    with Pool(len(jobs), initializer=_init, initargs=(projdir,)) as pool:
        for path, k in pool.imap_unordered(_chunk, jobs):
            print("  selesai", os.path.basename(path), k, "frame", flush=True)
    lst = os.path.join(wd, "list.txt")
    open(lst, "w").write("".join(f"file '{j[2]}'\n" for j in jobs))
    dst = os.path.join(out, "video_bisu.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst], check=True)
    print(f"VIDEO_BISU {dst}  ({time.time()-t0:.0f} dtk)")


if __name__ == "__main__":
    main()
