# -*- coding: utf-8 -*-
"""
timing.py - menyusun jadwal adegan dari voiceover.

- Durasi & jeda (silencedetect) diukur dari file VO asli.
- Batas adegan dibagi menurut panjang "narasi" tiap adegan, lalu di-snap ke jeda terdekat.
- Field "mulai" (detik) di adegan = paksa waktu mulai (untuk koreksi manual).
- Tanpa VO: durasi diperkirakan dari jumlah kata (draf bisu).
- levels(): tingkat buka mulut per frame (0-3) dari energi VO untuk lipsync.
"""
import json, re, subprocess
import numpy as np


def durasi(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def jeda(path, db=-34, min_d=0.18):
    """Daftar (mulai, selesai) bagian hening."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", f"silencedetect=noise={db}dB:d={min_d}", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    D = durasi(path)
    out = []
    for i, s in enumerate(st):
        out.append((s, en[i] if i < len(en) else D))
    return out


def _bobot(sc):
    t = re.sub(r"\[[^\]]*\]", "", sc.get("narasi") or "")
    return max(8, len(t.strip()))


def jadwal(adegan, vo=None, tail=0.8):
    """Kembalikan list (mulai, selesai) per adegan + durasi total."""
    n = len(adegan)
    if not vo:
        ts, t = [], 0.0
        for sc in adegan:
            if "mulai" in sc:
                t = float(sc["mulai"])
            words = len(re.sub(r"\[[^\]]*\]", "", sc.get("narasi") or "").split())
            d = float(sc.get("durasi", max(2.5, words / 2.6 + 0.7)))
            ts.append([t, t + d]); t += d
        for i in range(n - 1):
            ts[i][1] = ts[i + 1][0]
        return [tuple(x) for x in ts], ts[-1][1]
    D = durasi(vo)
    sil = jeda(vo)
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    end_speech = sil[-1][0] if sil and sil[-1][1] >= D - 0.05 else D
    w = np.array([_bobot(s) for s in adegan], float)
    cum = np.concatenate([[0], np.cumsum(w) / w.sum()])
    b = lead + (end_speech - lead) * cum
    mids = [(s + e) / 2 for s, e in sil if lead < (s + e) / 2 < end_speech]
    for i in range(1, n):
        if "mulai" in adegan[i]:
            b[i] = float(adegan[i]["mulai"]); continue
        cand = [m for m in mids if abs(m - b[i]) < 1.6 and m > b[i - 1] + 1.0]
        if cand:
            b[i] = min(cand, key=lambda m: abs(m - b[i]))
        b[i] = max(b[i], b[i - 1] + 1.0)
    b[0] = 0.0
    total = D + tail
    b[n] = total
    return [(float(b[i]), float(b[i + 1])) for i in range(n)], total


def levels(vo, fps, total):
    """Tingkat buka mulut per frame (0..3)."""
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", vo, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    N = int(np.ceil(total * fps))
    hop = sr / fps
    rms = np.zeros(N, np.float32)
    for i in range(N):
        a = int(i * hop); seg = x[a:a + int(hop)]
        if len(seg):
            rms[i] = np.sqrt(np.mean(seg * seg))
    p = np.percentile(rms[rms > 0], 95) if np.any(rms > 0) else 1.0
    r = rms / max(p, 1e-6)
    lv = np.zeros(N, np.int8)
    lv[r > 0.18] = 1; lv[r > 0.42] = 2; lv[r > 0.7] = 3
    return lv


if __name__ == "__main__":
    import sys
    proj = json.load(open(sys.argv[1]))
    vo = sys.argv[2] if len(sys.argv) > 2 else None
    ts, total = jadwal(proj["adegan"], vo)
    for i, (a, b) in enumerate(ts):
        print(f"{i+1:2d}. {a:6.2f} - {b:6.2f}  {proj['adegan'][i].get('tipe')}")
    print("total", round(total, 2))
