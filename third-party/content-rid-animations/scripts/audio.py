# -*- coding: utf-8 -*-
"""
audio.py - musik latar orisinal + SFX + mixing + gabung ke video, lalu verifikasi.

Pakai:
  python3 audio.py <folder_proyek> [--musik auto|none|<file>] [--vol-musik 0.16] [--tanpa-sfx]

Butuh out/video_bisu.mp4 dan out/events.json dari render.py.
Hasil: out/<judul>_vN.mp4 (tidak pernah menimpa versi lama).
Musik "auto" = musik ceria buatan sendiri (marimba + bass + shaker), jadi bebas hak cipta.
"""
import os, sys, json, re, argparse, subprocess, wave
import numpy as np

SR = 44100


def _env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / d)
    return e


def marimba(f, dur, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.05)
    return s * _env(n, 0.003, 0.28) * vel


def musik(total, bpm=100, seed=1):
    rng = np.random.default_rng(seed)
    n = int((total + 1) * SR)
    out = np.zeros(n, np.float32)
    beat = 60 / bpm
    # I - V - vi - IV (C mayor), 1 bar per akor
    chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    bar = 0; t = 0.0
    while t < total:
        ch = chords[bar % 4]
        for k in range(8):  # seperdelapan
            tt = t + k * beat / 2
            if tt >= total:
                break
            m = ch[pat[k]] + 12 + (12 if (bar % 8 >= 4 and k in (3, 7)) else 0)
            s = marimba(hz(m), 0.6, 0.35 if k % 2 else 0.5)
            a = int(tt * SR); out[a:a + len(s)] += s[:max(0, n - a)]
            # shaker
            if k % 2 == 1:
                ln = int(0.05 * SR)
                sh = rng.standard_normal(ln) * _env(ln, 0.002, 0.015) * 0.06
                out[a:a + ln] += sh[:max(0, n - a)]
        for k in (0, 2):  # bass
            tt = t + k * beat; a = int(tt * SR)
            ln = int(beat * 1.6 * SR); tb = np.arange(ln) / SR
            b = np.sin(2 * np.pi * hz(ch[0] - 24) * tb) * _env(ln, 0.01, 0.5) * 0.45
            out[a:a + ln] += b[:max(0, n - a)]
        t += beat * 4; bar += 1
    out = out[:int(total * SR)]
    fade = int(min(2.0, total / 4) * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    return out / (np.abs(out).max() + 1e-6) * 0.8


def sfx(kind):
    if kind == "pop":
        n = int(0.09 * SR); t = np.arange(n) / SR
        f = 500 + 1400 * t / t[-1]
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.03) * 0.7
    if kind == "ding":
        n = int(0.6 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * _env(n, 0.002, 0.18) * 0.4
    if kind == "naik":
        n = int(0.35 * SR); t = np.arange(n) / SR
        f = 400 + 900 * (t / t[-1]) ** 2
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) * 0.35
    if kind == "whoosh":
        n = int(0.35 * SR); rng = np.random.default_rng(3)
        x = rng.standard_normal(n)
        k = 18; x = np.convolve(x, np.ones(k) / k, "same")
        return x * np.sin(np.pi * np.arange(n) / n) ** 2 * 1.4
    return np.zeros(1)


def tulis_wav(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames",
                        "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyek")
    ap.add_argument("--musik", default=None)
    ap.add_argument("--vol-musik", type=float, default=None)
    ap.add_argument("--tanpa-sfx", action="store_true")
    a = ap.parse_args()
    pd = os.path.abspath(a.proyek); out = os.path.join(pd, "out")
    proj = json.load(open(os.path.join(pd, "proyek.json")))
    tl = json.load(open(os.path.join(out, "timeline.json")))
    total = tl["durasi"]; vo = tl["vo"]
    mus = a.musik or proj.get("musik", "auto")
    vm = a.vol_musik if a.vol_musik is not None else float(proj.get("vol_musik", 0.16 if vo else 0.35))

    # musik
    mpath = None
    if mus and mus != "none":
        mpath = os.path.join(out, "musik.wav")
        if mus == "auto":
            tulis_wav(mpath, musik(total, bpm=int(proj.get("bpm", 100))))
        else:
            src = mus if os.path.isabs(mus) else os.path.join(pd, mus)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", src, "-t", f"{total:.3f}",
                            "-af", f"afade=t=out:st={max(0, total-2):.3f}:d=2", "-ar", str(SR), "-ac", "2", mpath], check=True)
    # sfx
    spath = os.path.join(out, "sfx.wav")
    track = np.zeros(int(total * SR) + SR, np.float32)
    if not a.tanpa_sfx and proj.get("sfx", True):
        last = {}
        for t, k in json.load(open(os.path.join(out, "events.json"))):
            if t - last.get(k, -9) < 0.12:
                continue
            last[k] = t
            s = sfx(k); i = int(t * SR)
            track[i:i + len(s)] += s[:max(0, len(track) - i)]
    tulis_wav(spath, track[:int(total * SR)] * 0.5)

    # mixing
    ins = ["-i", os.path.join(out, "video_bisu.mp4")]
    fl = []; mixes = []; idx = 1
    if vo:
        ins += ["-i", vo]; fl.append(f"[{idx}:a]aresample={SR},aformat=channel_layouts=stereo,apad,asplit=2[vo][key]"); vi = idx; idx += 1
    if mpath:
        ins += ["-i", mpath]
        if vo:
            fl.append(f"[{idx}:a]volume={vm}[m0]")
            fl.append("[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[mus]")
        else:
            fl.append(f"[{idx}:a]volume={vm}[mus]")
        mixes.append("[mus]"); idx += 1
    ins += ["-i", spath]; fl.append(f"[{idx}:a]volume=0.55[sx]"); mixes.append("[sx]"); idx += 1
    if vo:
        mixes = ["[vo]"] + mixes
    fl.append("".join(mixes) + f"amix=inputs={len(mixes)}:normalize=0:duration=first,atrim=0:{total:.3f},loudnorm=I=-16:TP=-1.5:LRA=11,aresample={SR}[a]")
    base = re.sub(r"[^A-Za-z0-9_-]+", "-", proj.get("judul", "video")).strip("-") or "video"
    v = 1
    while os.path.exists(os.path.join(out, f"{base}_v{v}.mp4")):
        v += 1
    dst = os.path.join(out, f"{base}_v{v}.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error"] + ins + ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]",
                                                  "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", dst]
    subprocess.run(cmd, check=True)

    # verifikasi
    info = probe(dst)
    dur = float(info["format"]["duration"])
    vs = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    au = [s for s in info["streams"] if s["codec_type"] == "audio"]
    ok = abs(dur - total) < 0.2 and vs["codec_name"] == "h264" and au and au[0]["codec_name"] == "aac"
    if vo:
        from timing import durasi
        ok = ok and dur + 0.05 >= durasi(vo)
    print(f"{'FINAL OK' if ok else 'FINAL PERIKSA'} {dst}")
    if os.path.isdir("/mnt/user-data/outputs"):
        import shutil
        shutil.copy(dst, "/mnt/user-data/outputs/"); print("DELIVER", os.path.join("/mnt/user-data/outputs", os.path.basename(dst)))
    print(f"  durasi {dur:.2f} dtk | {vs['width']}x{vs['height']} {vs['r_frame_rate']} | frame {vs.get('nb_frames')} | video {vs['codec_name']} | audio {au[0]['codec_name'] if au else '-'}"
          + (" | VO utuh" if vo else " | TANPA VO (draf)"))


if __name__ == "__main__":
    main()
