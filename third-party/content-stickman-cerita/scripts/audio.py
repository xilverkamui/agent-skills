# -*- coding: utf-8 -*-
"""
audio.py - musik orisinal per suasana + efek suara otomatis + mixing + gabung ke video + verifikasi.

  python3 audio.py <proyek> [--musik auto|none|<file>] [--vol-musik 0.16] [--tanpa-sfx]

Butuh out/video_bisu.mp4, out/timeline.json, out/events.json dari render.py. Hasil: out/<judul>_vN.mp4 (tak pernah menimpa).
Musik "auto" dibuat dari kode (bebas hak cipta); tiap adegan boleh punya "musik": <suasana>.
Suasana: ceria santai hangat sedih tegang semangat lucu misteri malam
"""
import os, sys, json, re, argparse, subprocess, wave
import numpy as np

SR = 44100
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=0.004, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def tone(f, dur, kind, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == "marimba":
        s = np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / .05); e = env(n, .003, .26)
    elif kind == "epiano":
        s = np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .4); e = env(n, .01, .7)
    elif kind == "musicbox":
        s = np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / .15) + .15 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t / .07); e = env(n, .002, .9)
    elif kind == "piano":
        s = np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .5) + .2 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / .3); e = env(n, .004, 1.0)
    elif kind == "pizz":
        s = np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / .03); e = env(n, .002, .09)
    else:  # pluck
        s = np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .1); e = env(n, .002, .16)
    return s * e * vel


def pad(chord, dur, vel=.14):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * hz(m) * t) + .3 * np.sin(2 * np.pi * hz(m) * 2.003 * t) for m in chord)
    e = np.minimum(1, t / .6) * np.minimum(1, (dur - t) / .6)
    return s * e * vel / len(chord)


MOODS = {
    "ceria":    dict(bpm=112, ch=[[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]], lead="marimba", pat="arp8", bass=1, perc="shaker"),
    "santai":   dict(bpm=84, ch=[[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]], lead="epiano", pat="arp4", bass=1, perc="brush"),
    "hangat":   dict(bpm=76, ch=[[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]], lead="musicbox", pat="slow", pad=1),
    "sedih":    dict(bpm=62, ch=[[57, 60, 64], [53, 57, 60], [48, 52, 55], [52, 56, 59]], lead="piano", pat="sparse", pad=1),
    "tegang":   dict(bpm=104, ch=[[45, 48, 52], [44, 47, 51], [45, 48, 52], [41, 44, 48]], lead="pluck", pat="tick", drone=1),
    "semangat": dict(bpm=128, ch=[[62, 66, 69], [57, 61, 64], [59, 62, 66], [55, 59, 62]], lead="marimba", pat="arp8", bass=1, perc="kick"),
    "lucu":     dict(bpm=120, ch=[[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]], lead="pizz", pat="bounce", bass=1),
    "misteri":  dict(bpm=70, ch=[[57, 60, 63], [56, 59, 62], [57, 60, 63], [53, 56, 59]], lead="musicbox", pat="sparse", drone=1),
    "malam":    dict(bpm=66, ch=[[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]], lead="musicbox", pat="slow", pad=1),
}


def put(out, s, t):
    a = int(t * SR)
    if a < 0 or a >= len(out):
        return
    out[a:a + len(s)] += s[:max(0, len(out) - a)]


def mood_audio(name, dur, seed=1):
    M = MOODS.get(name, MOODS["ceria"])
    rng = np.random.default_rng(seed)
    out = np.zeros(int((dur + 1.5) * SR), np.float32)
    beat = 60 / M["bpm"]
    bar, t = 0, 0.0
    while t < dur + 0.5:
        ch = M["ch"][bar % 4]
        pat = M["pat"]
        steps = {"arp8": [(k * beat / 2, ch[[0, 1, 2, 1, 0, 2, 1, 2][k] % len(ch)] + 12, .5 if k % 2 else .7) for k in range(8)],
                 "arp4": [(k * beat, ch[k % len(ch)] + 12, .6) for k in range(4)],
                 "slow": [(0, ch[2] + 12, .7), (beat * 1.5, ch[1] + 12, .5), (beat * 2.5, ch[0] + 24, .6)],
                 "sparse": [(0, ch[2] + 12, .8), (beat * 2.5, ch[1] + 12, .5)],
                 "tick": [(k * beat / 2, ch[0] + 24 if k % 4 else ch[2] + 12, .35) for k in range(8)],
                 "bounce": [(k * beat / 2, ch[[0, 2, 1, 2][k % 4]] + 12, .6) for k in (0, 1, 2, 3, 5, 7)]}[pat]
        for off, m, v in steps:
            put(out, tone(hz(m), 0.7, M["lead"], v * .45), t + off)
        if M.get("bass"):
            for k in (0, 2):
                n = int(beat * 1.6 * SR); tb = np.arange(n) / SR
                put(out, (np.sin(2 * np.pi * hz(ch[0] - 24) * tb) * env(n, .01, .45) * .42).astype(np.float32), t + k * beat)
        if M.get("pad"):
            put(out, pad([c - 12 for c in ch], beat * 4).astype(np.float32), t)
        if M.get("drone"):
            put(out, pad([ch[0] - 24, ch[0] - 17], beat * 4, .2).astype(np.float32), t)
        perc = M.get("perc")
        for k in range(8):
            tt = t + k * beat / 2
            if perc == "shaker" and k % 2:
                n = int(.05 * SR); put(out, (rng.standard_normal(n) * env(n, .002, .015) * .06).astype(np.float32), tt)
            if perc == "brush" and k % 2 == 0:
                n = int(.12 * SR); put(out, (rng.standard_normal(n) * env(n, .01, .05) * .035).astype(np.float32), tt)
            if perc == "kick" and k % 2 == 0:
                n = int(.2 * SR); tb = np.arange(n) / SR
                put(out, (np.sin(2 * np.pi * (110 - 70 * tb / .2) * tb) * env(n, .002, .09) * .5).astype(np.float32), tt)
        t += beat * 4
        bar += 1
    return out[:int((dur + 1.5) * SR)]


def musik(sections, total):
    out = np.zeros(int((total + 1) * SR), np.float32)
    for i, (a, b, mood) in enumerate(sections):
        dur = b - a
        s = mood_audio(mood, dur + 0.8, seed=i + 3)
        s = s[:int((dur + 0.8) * SR)].copy()
        fi = int(min(.8, dur / 3) * SR)
        s[:fi] *= np.linspace(0, 1, fi)
        fo = int(.8 * SR)
        s[-fo:] *= np.linspace(1, 0, fo)
        put(out, s, a - 0.4 if i else a)
    out = out[:int(total * SR)]
    f = int(min(2.0, total / 4) * SR)
    out[-f:] *= np.linspace(1, 0, f)
    return out / (np.abs(out).max() + 1e-6) * .8


# ------------------------------------------------------------ efek suara
def noise_band(n, f0, f1, seed=3):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((fr - np.linspace(f0, f1, len(fr)) * 0 - (f0 + f1) / 2) / ((f1 - f0) / 2 + 1)) ** 2)
    return np.fft.irfft(X, n)


def sfx(kind):
    def sweep(f0, f1, d, a=.004, dec=None):
        n = int(d * SR); t = np.arange(n) / SR
        f = f0 + (f1 - f0) * t / t[-1]
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, a, dec or d / 3)
    if kind in ("pop", "tik"):
        return sweep(500, 1800, .09, .002, .03) * .7 if kind == "pop" else sweep(1800, 1800, .03, .001, .01) * .4
    if kind == "ding":
        n = int(.6 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1318 * t) + .5 * np.sin(2 * np.pi * 1976 * t)) * env(n, .002, .18) * .45
    if kind == "tanya":
        return np.concatenate([sweep(400, 520, .12), sweep(520, 700, .2)]) * .5
    if kind == "sparkle":
        s = np.zeros(int(.7 * SR))
        for i, m in enumerate((88, 91, 96, 100)):
            x = tone(hz(m), .35, "musicbox", .5); s[int(i * .07 * SR):int(i * .07 * SR) + len(x)] += x[:len(s) - int(i * .07 * SR)]
        return s * .6
    if kind == "zzz":
        return sweep(420, 240, .7, .05, .4) * .22
    if kind == "boing":
        n = int(.5 * SR); t = np.arange(n) / SR
        f = 180 + 260 * np.abs(np.sin(2 * np.pi * 3 * t)) * np.exp(-t / .25)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .003, .22) * .5
    if kind in ("langkah", "step_a"):
        n = int(.06 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 140 * t) * env(n, .001, .02) + noise_band(n, 300, 900) * env(n, .001, .012) * .5) * .35
    if kind in ("whoosh", "whoosh_lembut"):
        d = .38 if kind == "whoosh" else .6
        n = int(d * SR); x = np.random.default_rng(5).standard_normal(n)
        k = 22 if kind == "whoosh" else 40
        x = np.convolve(x, np.ones(k) / k, "same")
        return x * np.sin(np.pi * np.arange(n) / n) ** 2 * (1.5 if kind == "whoosh" else 1.0)
    if kind == "thud":
        n = int(.3 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * (90 - 50 * t / .3) * t) * env(n, .002, .1) * .8 + noise_band(n, 200, 1500, 7) * env(n, .001, .02) * .3)
    if kind == "seru":
        return sweep(420, 160, .22, .003, .09) * .6 + sweep(900, 1400, .1, .002, .04) * .2 if False else np.pad(sweep(420, 160, .22, .003, .09) * .6, (0, 0))
    if kind == "alarm":
        s = np.zeros(int(1.4 * SR))
        for k in range(8):
            x = np.sign(np.sin(2 * np.pi * 2300 * np.arange(int(.08 * SR)) / SR)) * .18 * env(int(.08 * SR), .002, .1)
            a = int((k % 4) * .09 * SR) + int((k // 4) * .6 * SR)
            s[a:a + len(x)] += x
        return s
    if kind == "kilat":
        return sweep(300, 2400, .2, .002, .12) * .35 + noise_band(int(.2 * SR), 2000, 8000, 9) * env(int(.2 * SR), .001, .06) * .2
    if kind == "iris":
        return sweep(300, 1000, .35, .01, .2) * .35
    return np.zeros(1)


def tulis_wav(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames", "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyek"); ap.add_argument("--musik"); ap.add_argument("--vol-musik", type=float); ap.add_argument("--tanpa-sfx", action="store_true")
    a = ap.parse_args()
    pd = os.path.abspath(a.proyek); out = os.path.join(pd, "out")
    proj = json.load(open(os.path.join(pd, "proyek.json"), encoding="utf-8"))
    tl = json.load(open(os.path.join(out, "timeline.json")))
    total, vo = tl["durasi"], tl["vo"]
    mus = a.musik or proj.get("musik", "auto")
    vm = a.vol_musik if a.vol_musik is not None else float(proj.get("vol_musik", .17 if vo else .35))
    mpath = None
    if mus and mus != "none":
        mpath = os.path.join(out, "musik.wav")
        if mus == "auto":
            secs = []
            for s in tl["adegan"]:
                m = s.get("musik") or proj.get("mood_musik", "ceria")
                if secs and secs[-1][2] == m:
                    secs[-1][1] = s["selesai"]
                else:
                    secs.append([s["mulai"], s["selesai"], m])
            secs[-1][1] = total
            tulis_wav(mpath, musik(secs, total))
        else:
            src = mus if os.path.isabs(mus) else os.path.join(pd, mus)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", src, "-t", f"{total:.3f}", "-af", f"afade=t=out:st={max(0, total - 2):.3f}:d=2", "-ar", str(SR), "-ac", "2", mpath], check=True)
    spath = os.path.join(out, "sfx.wav")
    track = np.zeros(int(total * SR) + 2 * SR, np.float32)
    n_sfx = 0
    if not a.tanpa_sfx and proj.get("sfx", True):
        last = {}
        for t, k, g in json.load(open(os.path.join(out, "events.json"))):
            if t < 0 or t - last.get(k, -9) < .1:
                continue
            last[k] = t
            s = sfx(k)
            i = int(t * SR)
            if i < len(track):
                track[i:i + len(s)] += (s * g)[:len(track) - i]; n_sfx += 1
    tulis_wav(spath, track[:int(total * SR)] * .5)
    ins = ["-i", os.path.join(out, "video_bisu.mp4")]
    fl, mixes, idx = [], [], 1
    if vo:
        ins += ["-i", vo]; fl.append(f"[{idx}:a]aresample={SR},aformat=channel_layouts=stereo,apad,asplit=2[vo][key]"); idx += 1
    if mpath:
        ins += ["-i", mpath]
        if vo:
            fl.append(f"[{idx}:a]volume={vm}[m0]"); fl.append("[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[mus]")
        else:
            fl.append(f"[{idx}:a]volume={vm}[mus]")
        mixes.append("[mus]"); idx += 1
    ins += ["-i", spath]; fl.append(f"[{idx}:a]volume=.6[sx]"); mixes.append("[sx]")
    if vo:
        mixes = ["[vo]"] + mixes
    fl.append("".join(mixes) + f"amix=inputs={len(mixes)}:normalize=0:duration=first,atrim=0:{total:.3f},loudnorm=I=-16:TP=-1.5:LRA=11,aresample={SR}[a]")
    base = re.sub(r"[^A-Za-z0-9_-]+", "-", proj.get("judul", "video")).strip("-") or "video"
    v = 1
    while os.path.exists(os.path.join(out, f"{base}_v{v}.mp4")):
        v += 1
    dst = os.path.join(out, f"{base}_v{v}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + ins + ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", dst], check=True)
    info = probe(dst)
    dur = float(info["format"]["duration"])
    vs = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    au = [s for s in info["streams"] if s["codec_type"] == "audio"]
    ok = abs(dur - total) < .2 and vs["codec_name"] == "h264" and au and au[0]["codec_name"] == "aac"
    if vo:
        from timing import durasi
        ok = ok and dur + .05 >= durasi(vo)
    print(f"{'FINAL OK' if ok else 'FINAL PERIKSA'} {dst}")
    if os.path.isdir("/mnt/user-data/outputs"):
        import shutil
        shutil.copy(dst, "/mnt/user-data/outputs/"); print("DELIVER", os.path.join("/mnt/user-data/outputs", os.path.basename(dst)))
    print(f"  durasi {dur:.2f} dtk | {vs['width']}x{vs['height']} {vs['r_frame_rate']} | frame {vs.get('nb_frames')} | video {vs['codec_name']} | audio {au[0]['codec_name'] if au else '-'} | sfx {n_sfx}" + (" | VO utuh" if vo else " | TANPA VO (draf)"))


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
