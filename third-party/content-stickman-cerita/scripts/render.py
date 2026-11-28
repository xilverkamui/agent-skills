# -*- coding: utf-8 -*-
"""
render.py - render video bisu (paralel, bisa dilanjutkan) atau stills QC.

  python3 render.py <proyek>                       # video bisu penuh -> out/video_bisu.mp4 + out/events.json
  python3 render.py <proyek> --stills auto         # lembar QC (tiap adegan, awal+tengah+akhir) -> out/qc/sheet.jpg
  python3 render.py <proyek> --stills 1.5,7,12.2   # detik tertentu
  python3 render.py <proyek> --strip 3             # deretan frame adegan ke-3 (cek gerak kamera) -> out/qc/strip_03.jpg
  python3 render.py <proyek> --draft               # kualitas cepat (tanpa supersampling), untuk cek gerak
  python3 render.py <proyek> --jobs 4

Perintah yang terhenti ("BELUM SELESAI") cukup dijalankan ulang persis sama: potongan yang sudah jadi dipakai lagi.
"""
import os, sys, json, math, time, subprocess, argparse
from multiprocessing import get_context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from film import Film
from stik import font

_FILM = None
CHUNK = 90


def _init(projdir, ss):
    global _FILM
    _FILM = Film(projdir, ss=ss)


def _chunk(args):
    a, b, path = args
    F = _FILM
    tmp = path + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{F.W}x{F.H}", "-r", str(F.fps),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(F.fps), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(F.frame(f).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    os.replace(tmp, path)
    return path, b - a


def lembar(F, ims, labels, out, cols=None):
    cols = cols or (3 if F.W >= F.H else 4)
    tw = 640 if F.W >= F.H else 330
    th = int(tw * F.H / F.W)
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 8, rows * (th + 24) + (rows + 1) * 8), (30, 30, 40))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = 8 + c * (tw + 8), 8 + r * (th + 32)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 22))
        d.text((x + 4, y + 2), labels[i], font=font("teks", 18), fill=(255, 255, 255))
    sheet.save(out, quality=88)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyek")
    ap.add_argument("--stills")
    ap.add_argument("--strip", type=int)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(1, min(8, os.cpu_count() or 2)))
    ap.add_argument("--anggaran", type=int, default=0, help="batas detik per perintah (0 = otomatis: 150 di chat, tanpa batas di lokal)")
    ap.add_argument("--ulang", action="store_true", help="hapus potongan lama")
    a = ap.parse_args()
    global _FILM
    projdir = os.path.abspath(a.proyek)
    out = os.path.join(projdir, "out")
    os.makedirs(out, exist_ok=True)
    F = Film(projdir, ss=1 if a.draft else 2)
    for w in F.warnings:
        print("[PERIKSA]", w)

    if a.stills or a.strip:
        qc = os.path.join(out, "qc")
        os.makedirs(qc, exist_ok=True)
        if a.strip:
            s = F.scenes[a.strip - 1]
            n = 9
            ts = [s.start + s.dur * (i / (n - 1)) * 0.97 for i in range(n)]
            ims = [F.frame(int(t * F.fps)) for t in ts]
            lembar(F, ims, [f"adegan {a.strip}  t={t:.2f}" for t in ts], os.path.join(qc, f"strip_{a.strip:02d}.jpg"), 3)
            print("STRIP", os.path.join(qc, f"strip_{a.strip:02d}.jpg"))
            return
        if a.stills == "auto":
            times = []
            for s in F.scenes:
                times += [s.start + 0.25, s.start + s.dur * 0.55, max(s.start, s.end - 0.35)]
        else:
            times = [float(x) for x in a.stills.split(",")]
        ims = [F.frame(min(F.N - 1, int(t * F.fps))) for t in times]
        for t, im in zip(times, ims):
            im.save(os.path.join(qc, f"t{t:06.2f}.jpg"), quality=88)
        lembar(F, ims, [f"{t:.2f}s" for t in times], os.path.join(qc, "sheet.jpg"))
        print("STILLS", os.path.join(qc, "sheet.jpg"))
        for i, s in enumerate(F.scenes):
            print(f"  adegan {i + 1:2d} {s.start:6.2f}-{s.end:6.2f}  {s.s.get('latar', s.s.get('tipe', ''))}")
        return

    t0 = time.time()
    json.dump({"durasi": F.total, "fps": F.fps, "ukuran": [F.W, F.H], "vo": F.vo,
               "adegan": [{"mulai": round(s.start, 3), "selesai": round(s.end, 3), "latar": s.s.get("latar"), "musik": s.s.get("musik")} for s in F.scenes]},
              open(os.path.join(out, "timeline.json"), "w"), indent=1)
    json.dump([[round(t, 3), k, g] for t, k, g in F.events()], open(os.path.join(out, "events.json"), "w"))
    wd = os.path.join(out, "work")
    if a.ulang and os.path.isdir(wd):
        import shutil
        shutil.rmtree(wd)
    os.makedirs(wd, exist_ok=True)
    jobs = []
    for i in range(0, F.N, CHUNK):
        jobs.append((i, min(F.N, i + CHUNK), os.path.join(wd, f"c{i // CHUNK:04d}.mp4")))
    todo = [j for j in jobs if not os.path.exists(j[2])]
    budget = a.anggaran or (150 if os.path.isdir("/mnt/user-data/outputs") else 0)
    print(f"render {F.N} frame ({F.total:.1f} dtk) {F.W}x{F.H}@{F.fps} | sisa {len(todo)}/{len(jobs)} potongan | {a.jobs} proses", flush=True)
    _FILM = F
    if todo:
        ctx = get_context("spawn")
        pool = ctx.Pool(min(a.jobs, len(todo)), initializer=_init, initargs=(projdir, 1 if a.draft else 2))
        it = pool.imap_unordered(_chunk, todo)
        done = 0
        try:
            while done < len(todo):
                if budget and time.time() - t0 > budget:
                    pool.terminate()
                    left = len([j for j in jobs if not os.path.exists(j[2])])
                    pct = int(100 * (len(jobs) - left) / len(jobs))
                    print(f"BELUM SELESAI {pct}% | sisa {left} potongan | jalankan perintah yang sama lagi")
                    sys.exit(2)
                try:
                    path, k = it.next(timeout=5)
                    done += 1
                    print("  selesai", os.path.basename(path), flush=True)
                except Exception as e:
                    if e.__class__.__name__ == "TimeoutError":
                        continue
                    raise
        finally:
            pool.close()
    lst = os.path.join(wd, "list.txt")
    open(lst, "w").write("".join(f"file '{j[2]}'\n" for j in jobs))
    dst = os.path.join(out, "video_bisu.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst], check=True)
    print(f"VIDEO_BISU {dst}  ({time.time() - t0:.0f} dtk)")


if __name__ == "__main__":
    main()
