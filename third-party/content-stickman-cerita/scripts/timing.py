# -*- coding: utf-8 -*-
"""
timing.py - jadwal adegan + perkiraan waktu tiap kata dari voiceover.

* durasi / jeda (silencedetect) diukur dari file VO asli
* batas adegan dibagi menurut panjang "narasi", lalu menempel ke jeda terdekat
* waktu tiap kata: bobot huruf dibagi di bagian yang BERSUARA saja (jeda dilompati);
  bila ada input/words.json (hasil alignment luar) dipakai apa adanya
* levels(): tingkat buka mulut per frame (0..1) dari energi suara
"""
import json, os, re, subprocess
import numpy as np


def durasi(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def jeda(path, db=-34, min_d=0.16):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", f"silencedetect=noise={db}dB:d={min_d}", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    D = durasi(path)
    return [(max(0.0, s), en[i] if i < len(en) else D) for i, s in enumerate(st)]


def bersih(teks):
    return re.sub(r"\[[^\]]*\]", "", teks or "").strip()


def kata_list(teks):
    return [w for w in re.split(r"\s+", bersih(teks)) if w]


def _bobot(sc):
    n = sum(len(w) + 1 + (3 if w[-1:] in ",;:" else 6 if w[-1:] in ".?!" else 0) for w in kata_list(sc.get("narasi")))
    return max(8, n)


def jadwal(adegan, vo=None, tail=0.9):
    n = len(adegan)
    if not vo:
        ts, t = [], 0.0
        for sc in adegan:
            if "mulai" in sc:
                t = float(sc["mulai"])
            words = len(kata_list(sc.get("narasi")))
            d = float(sc.get("durasi", max(3.0, words / 2.7 + 0.8)))
            ts.append([t, t + d])
            t += d
        for i in range(n - 1):
            ts[i][1] = ts[i + 1][0]
        return [tuple(x) for x in ts], ts[-1][1]
    D = durasi(vo)
    sil = jeda(vo)
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    end_speech = sil[-1][0] if sil and sil[-1][1] >= D - 0.05 else D
    w = np.array([_bobot(s) for s in adegan], float)
    cum = np.concatenate([[0], np.cumsum(w) / w.sum()])
    # peta bobot -> waktu bicara (jeda dilompati) supaya batas jatuh di ucapan, bukan di keheningan
    seg, a = [], lead
    for s, e in sil:
        if e <= lead or s >= end_speech:
            continue
        if s > a:
            seg.append((a, min(s, end_speech)))
        a = max(a, e)
    if a < end_speech:
        seg.append((a, end_speech))
    tot = sum(e - s for s, e in seg) or (end_speech - lead)

    def at_speech(frac):
        x = frac * tot
        for s, e in seg:
            if x <= e - s:
                return s + x
            x -= e - s
        return end_speech
    b = np.array([at_speech(c) for c in cum])
    mids = [(s + e) / 2 for s, e in sil if lead < (s + e) / 2 < end_speech]
    for i in range(1, n):
        if "mulai" in adegan[i]:
            b[i] = float(adegan[i]["mulai"])
            continue
        cand = [m for m in mids if abs(m - b[i]) < 1.8 and m > b[i - 1] + 1.0]
        if cand:
            b[i] = min(cand, key=lambda m: abs(m - b[i]))
        b[i] = max(b[i], b[i - 1] + 1.2)
    b[0] = 0.0
    b[n] = D + tail
    return [(float(b[i]), float(b[i + 1])) for i in range(n)], D + tail


def kata_waktu(adegan, ts, vo=None, words_file=None):
    """Per adegan: [(kata, mulai_abs, selesai_abs)]."""
    out = []
    if words_file and os.path.exists(words_file):
        ext = json.load(open(words_file))
        k = 0
        for sc in adegan:
            ws = kata_list(sc.get("narasi"))
            out.append([(w, ext[k + i]["s"], ext[k + i]["e"]) for i, w in enumerate(ws) if k + i < len(ext)])
            k += len(ws)
        return out
    sil = jeda(vo) if vo else []
    for sc, (a, b) in zip(adegan, ts):
        ws = kata_list(sc.get("narasi"))
        if not ws:
            out.append([])
            continue
        # segmen bersuara di [a,b]
        seg, p = [], a
        for s, e in sil:
            if e <= a or s >= b:
                continue
            if s > p:
                seg.append((p, min(s, b)))
            p = max(p, e)
        if p < b:
            seg.append((p, b))
        if not seg:
            seg = [(a, b)]
        # buang ekor hening adegan terakhir
        wts = [len(w) + 1 + (3 if w[-1:] in ",;:" else 6 if w[-1:] in ".?!" else 0) for w in ws]
        tot_w = sum(wts)
        tot_t = sum(e - s for s, e in seg)

        def to_real(x):
            for s, e in seg:
                if x <= e - s + 1e-9:
                    return s + x
                x -= e - s
            return seg[-1][1]
        c = 0.0
        row = []
        for w, wt in zip(ws, wts):
            core = (wt - (3 if w[-1:] in ",;:" else 6 if w[-1:] in ".?!" else 0))
            s0 = to_real(c / tot_w * tot_t)
            e0 = to_real((c + core) / tot_w * tot_t)
            row.append((w, s0, e0))
            c += wt
        out.append(row)
    return out


def levels(vo, fps, total):
    """Tingkat buka mulut per frame, 0..1 (sudah dihaluskan)."""
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", vo, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    N = int(np.ceil(total * fps)) + 2
    hop = sr / fps
    rms = np.zeros(N, np.float32)
    for i in range(N):
        a = int(i * hop)
        seg = x[a:a + int(hop)]
        if len(seg):
            rms[i] = np.sqrt(np.mean(seg * seg))
    p = np.percentile(rms[rms > 0], 92) if np.any(rms > 0) else 1.0
    r = np.clip(rms / max(p, 1e-6), 0, 1.2)
    r = np.where(r < 0.12, 0, r)
    k = np.array([0.25, 0.5, 0.25])
    return np.clip(np.convolve(r, k, "same"), 0, 1)
