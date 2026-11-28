# -*- coding: utf-8 -*-
"""
galeri.py - lembar karakter (ekspresi + pose + semua preset) untuk QA atau ditunjukkan ke user.

  python3 galeri.py <keluar.png>            # lembar Pria + Wanita seperti referensi gaya
  python3 galeri.py <keluar.png> --semua    # semua ekspresi, pose, dan preset tokoh
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from stik import *
import tokoh as TK


def potret(spec, W, H, cam, bg=(255, 255, 255, 0), ss=2, **st):
    c = Canvas(W, H, ss, cam, 1.0)
    c.fill(bg[:3] if len(bg) == 4 else bg)
    TK.Tokoh(spec).draw(c, TK.state(**st))
    return c.finish()


def pil(im, text, xy, size, fg, bgc, d):
    f = font("judul", size)
    b = d.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0], b[3] - b[1]
    pad = size * .45
    d.rounded_rectangle([xy[0] - w / 2 - pad, xy[1] - h / 2 - pad, xy[0] + w / 2 + pad, xy[1] + h / 2 + pad * .9], radius=size * .6, fill=bgc)
    d.text(xy, text, font=f, fill=fg, anchor="mm")


def lembar(out):
    W, H = 1920, 1080
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    cols = [("Karakter Pria", "raka", (46, 112, 214), (232, 241, 255), 0), ("Karakter Wanita", "nadia", (230, 80, 130), (255, 232, 240), 960)]
    eks6 = ["senang", "tenang", "tertawa", "kaget", "marah", "mikir"]
    poses = ["lambai", "tunjuk", "silang", "ide", "jalan"]
    for title, spec, col, light, ox in cols:
        d.ellipse([ox + 30, 90, ox + 400, 460], fill=light)
        im = potret(spec, 420, 520, Cam(0, -230, 1.0), pose="jempol", expr="senang")
        sheet.paste(im, (ox + 10, 40))
        pil(None, title, (ox + 560, 60), 46, (255, 255, 255), col, d)
        d.rounded_rectangle([ox + 400, 120, ox + 930, 540], radius=26, fill=light)
        pil(None, "Ekspresi Wajah", (ox + 665, 150), 26, (40, 40, 60), (255, 255, 255), d)
        for i, e in enumerate(eks6):
            im = potret(spec, 160, 150, Cam(0, -320, 0.82), expr=e, pose="diam")
            sheet.paste(im, (ox + 420 + (i % 3) * 165, 190 + (i // 3) * 170))
        pil(None, "Pose & Gestur", (ox + 480, 600), 26, (40, 40, 60), light, d)
        for i, p in enumerate(poses):
            im = potret(spec, 190, 390, Cam(0, -230, 0.7), pose=p, expr="senang" if p != "silang" else "tenang", t=0.3, amp=1.0 if p == "jalan" else 0, phase=0.9)
            sheet.paste(im, (ox + 10 + i * 185, 640))
    sheet.save(out)
    print("GALERI", out)


def semua(out):
    cols = 6
    names = list(TK.EKSPRESI)
    W = 1920
    cell = 300
    rows_e = math.ceil(len(names) / cols)
    poses = list(TK.POSE)
    rows_p = math.ceil(len(poses) / cols)
    presets = list(TK.PRESET)
    rows_c = math.ceil(len(presets) / cols)
    H = (rows_e + rows_p + rows_c) * cell + 120
    sheet = Image.new("RGB", (W, H), (250, 248, 242))
    d = ImageDraw.Draw(sheet)
    y = 20
    d.text((20, y), "EKSPRESI", font=font("judul", 34), fill=(40, 40, 60)); y += 50
    for i, e in enumerate(names):
        im = potret("raka" if i % 2 == 0 else "nadia", cell, cell - 70, Cam(0, -320, 1.1), expr=e)
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 36), e, font=font("judul", 26), fill=(40, 40, 60), anchor="mm")
    y += rows_e * cell
    d.text((20, y), "POSE", font=font("judul", 34), fill=(40, 40, 60)); y += 50
    for i, p in enumerate(poses):
        im = potret("raka" if i % 2 == 0 else "nadia", cell, cell - 30, Cam(0, -215, 0.62), pose=p, t=0.3, amp=1.0 if "jalan" in p or "lari" in p else 0, phase=0.9,
                    expr="senang", y=-0)
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 20), p, font=font("judul", 24), fill=(40, 40, 60), anchor="mm")
    y += rows_p * cell
    d.text((20, y), "TOKOH BAWAAN", font=font("judul", 34), fill=(40, 40, 60)); y += 50
    for i, p in enumerate(presets):
        im = potret(p, cell, cell - 30, Cam(0, -215, 0.62), pose="diam")
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 20), p, font=font("judul", 24), fill=(40, 40, 60), anchor="mm")
    sheet.save(out)
    print("GALERI", out, sheet.size)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "galeri.png"
    (semua if "--semua" in sys.argv else lembar)(out)
