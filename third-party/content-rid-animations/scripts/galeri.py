# -*- coding: utf-8 -*-
"""galeri.py - lembar QA: semua ekspresi, pose, dan ikon. Pakai: python3 galeri.py out.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import rid2d as R

out = sys.argv[1] if len(sys.argv) > 1 else "galeri.png"
W, H = 2400, 1700
img = R.latar("abu", W, H).convert("RGBA")
ex = list(R.EKSPRESI)
h = 300
for i, e in enumerate(ex):
    for j, kind in enumerate(("pria", "wanita")):
        s = R.karakter(kind, h, e)
        img.alpha_composite(s, (20 + i * 295 - 20, 10 + j * 330))
        lab = R.teks(e, 28, 300)
        img.alpha_composite(lab, (100 + i * 295, 10 + j * 330 + h - 30))
for i, pose in enumerate(R.POSE):
    for j, kind in enumerate(("pria", "wanita")):
        s = R.karakter(kind, 260, "senang", pose=pose)
        img.alpha_composite(s, (i * 330, 680 + j * 280))
names = list(R.IKON)
for i, n in enumerate(names):
    x, y = 30 + (i % 14) * 168, 1250 + (i // 14) * 220
    img.alpha_composite(R.ikon(n, 130), (x, y))
    img.alpha_composite(R.teks(n, 22, 170, weight="semi"), (x, y + 140))
img.convert("RGB").save(out)
print(out)
