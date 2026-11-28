# -*- coding: utf-8 -*-
"""
dunia.py - latar (set) gaya stikman: pastel datar + garis tepi hitam, lantai di y=0.

Tiap set = (belakang, depan):
  belakang(c, t, o) digambar SEBELUM tokoh; depan(c, t, o) SESUDAH tokoh (meja, selimut, semak depan).
o = opsi adegan: waktu (pagi|siang|sore|malam), jam, papan, warna, ...
Lapisan: c.set_depth(d) -> d<1 jauh (bergeser lebih sedikit saat kamera bergerak), d>1 dekat (foreground).
"""
import math
from stik import *

OW = 4.0
X0, X1 = -3200, 3200

LANGIT = {
    "pagi":  ((255, 222, 168), (196, 228, 252)),
    "siang": ((122, 192, 250), (206, 234, 254)),
    "sore":  ((255, 142, 108), (255, 216, 156)),
    "malam": ((18, 26, 78), (62, 72, 146)),
}
TINT = {"pagi": ((255, 220, 150), 22), "siang": ((255, 255, 255), 0), "sore": ((255, 140, 80), 46), "malam": ((16, 24, 100), 112)}
TINT_FG = {"pagi": 0.6, "siang": 0, "sore": 0.7, "malam": 0.5}


def waktu_of(o):
    return o.get("waktu", "siang")


def tint(c, o, fg=False):
    w = waktu_of(o)
    col, a = TINT.get(w, TINT["siang"])
    if fg:
        a = int(a * TINT_FG.get(w, 0))
    if a > 0:
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=col + (a,))


def langit(c, o, sun=True, horizon=0.78):
    w = waktu_of(o)
    top, bot = LANGIT.get(w, LANGIT["siang"])
    c.gradient(top, bot, 0, horizon + 0.2)
    c.set_depth(0.15)
    if w == "malam":
        for i in range(34):
            x = ((i * 397) % 2600) - 1300
            y = -((i * 211) % 700) - 380
            r = 3 + (i % 3)
            c.ell(x, y, r, r, (255, 250, 220))
        c.ell(560, -720, 74, 74, (255, 244, 190), OW, OUT)
        c.ell(594, -740, 62, 62, (24, 32, 86))     # sabit bulan
        c.ell(560, -720, 74, 74, None, OW, OUT)
    elif sun:
        sx, sy = {"pagi": (-520, -640), "siang": (560, -860), "sore": (-300, -300)}.get(w, (560, -860))
        col = (255, 206, 60) if w != "sore" else (255, 120, 70)
        c.ell(sx, sy, 150, 150, col + (55,))
        c.ell(sx, sy, 76, 76, col, OW, OUT)
        for i in range(12):
            a = i * math.pi / 6
            c.line([(sx + math.cos(a) * 104, sy + math.sin(a) * 104), (sx + math.cos(a) * 132, sy + math.sin(a) * 132)], OUT, 4)
    c.set_depth(1.0)


def awan(c, x, y, s=1.0, col=(255, 255, 255)):
    for (dx, dy, r) in ((-60, 8, 38), (-10, -14, 54), (52, 4, 42), (10, 14, 40)):
        c.ell(x + dx * s, y + dy * s, r * s, r * s, col)


def awan_set(c, o, n=6):
    w = waktu_of(o)
    if w == "malam":
        return
    c.set_depth(0.2)
    for i in range(n):
        awan(c, -1500 + i * 560 + (i % 2) * 120, -820 - (i * 97 % 260), 0.9 + (i % 3) * .25, (255, 255, 255) if w != "sore" else (255, 226, 200))
    c.set_depth(1.0)


def lantai(c, col, y1=1400, garis=None, step=0):
    c.rect(X0, 0, X1, y1, col)
    c.line([(X0, 0), (X1, 0)], OUT, OW)
    if garis:
        for i in range(1, 14):
            yy = i * i * 6 + 14
            if yy < y1:
                c.line([(X0, yy), (X1, yy)], garis, 2.4, False)


def dinding(c, col, atas=-1700):
    c.rect(X0, atas, X1, 0, col)


def papan_nama(c, x, y, w, h, teks, col=(255, 226, 130), size=64):
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, col, OW, OUT, r=10)
    c.text(x, y + 2, teks, size, (54, 60, 86), "judul")


def pohon(c, x, s=1.0, warna=HIJAU, batang=COKLAT, tinggi=300):
    h = tinggi * s
    c.poly([(x - 22 * s, 0), (x + 22 * s, 0), (x + 14 * s, -h), (x - 14 * s, -h)], batang, OW * s, OUT)
    for (dx, dy, r) in ((-86, -h - 10, 92), (88, -h - 6, 86), (0, -h - 84, 108), (-10, -h + 30, 80)):
        c.ell(x + dx * s, dy * 1.0, r * s, r * s, gelap(warna, .05) if dx < 0 else warna, OW * s, OUT)
    for (dx, dy, r) in ((-86, -h - 10, 92), (88, -h - 6, 86), (0, -h - 84, 108)):
        pass
    c.ell(x - 20 * s, -h - 84, 108 * s - OW, 108 * s - OW, warna)
    c.ell(x - 30 * s, -h - 110, 26 * s, 18 * s, terang(warna, .3))


def semak(c, x, w=220, h=110, warna=HIJAU_TUA, y=0):
    for i, (dx, r) in enumerate(((-.3, .62), (.0, .85), (.3, .62))):
        c.ell(x + dx * w, y - h * .3, w * r * .5, h * r * .7, warna, OW, OUT)
    c.ell(x, y - h * .35, w * .36, h * .5, warna)


def rumput(c, y1=1400, warna=HIJAU_MUDA):
    c.rect(X0, 0, X1, y1, warna)
    c.line([(X0, 0), (X1, 0)], OUT, OW)


def jendela(c, x, y, w, h, o, tirai=False):
    wk = waktu_of(o)
    top, bot = LANGIT.get(wk, LANGIT["siang"])
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, KAYU_TUA, OW * 1.4, OUT, r=8)
    x0, x1, y0, y1 = x - w / 2 + 16, x + w / 2 - 16, y - h / 2 + 16, y + h / 2 - 16
    c.rect(x0, y0, x1, y1, mix(top, bot, .5), OW, OUT)
    if wk == "malam":
        c.ell(x + w * .18, y - h * .12, w * .12, w * .12, (255, 244, 190), 3, OUT)
        for i in range(5):
            c.ell(x - w * .3 + i * w * .13, y - h * .3 + (i % 2) * 30, 3, 3, (255, 250, 220))
    else:
        c.ell(x + w * .16, y - h * .1, w * .13, w * .13, (255, 206, 60) if wk != "sore" else (255, 120, 70), 3, OUT)
        for i in range(8):
            a = i * math.pi / 4
            c.line([(x + w * .16 + math.cos(a) * w * .19, y - h * .1 + math.sin(a) * w * .19), (x + w * .16 + math.cos(a) * w * .24, y - h * .1 + math.sin(a) * w * .24)], OUT, 3)
        awan(c, x - w * .2, y + h * .18, w / 460, (255, 255, 255))
    c.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], OUT, OW)
    c.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], OUT, OW)
    c.rect(x0 - 12, y1 + 6, x1 + 12, y1 + 24, KAYU, OW, OUT, r=6)


def tanaman(c, x, y=0, s=1.0, pot=ORANYE):
    c.poly([(x - 34 * s, y - 70 * s), (x + 34 * s, y - 70 * s), (x + 26 * s, y), (x - 26 * s, y)], pot, OW * s, OUT)
    for a, l in ((-42, 120), (-16, 150), (14, 140), (40, 112), (0, 170)):
        r = math.radians(a - 90)
        tx, ty = x + math.cos(r) * l * s, y - 70 * s + math.sin(r) * l * s
        c.blob([(x, y - 70 * s), (x + math.cos(r + .45) * l * .5 * s, y - 70 * s + math.sin(r + .45) * l * .5 * s), (tx, ty),
                (x + math.cos(r - .45) * l * .5 * s, y - 70 * s + math.sin(r - .45) * l * .5 * s)], HIJAU, OW * .8 * s, OUT, n=5)


def rak_buku(c, x, y, w=300, h=520, rows=4, seed=0):
    c.rect(x - w / 2, y - h, x + w / 2, y, KAYU_TUA, OW, OUT, r=6)
    c.rect(x - w / 2 + 14, y - h + 14, x + w / 2 - 14, y - 14, (206, 156, 108), 0)
    cols = [MERAH, BIRU, KUNING, HIJAU, UNGU, ORANYE, PINK, (80, 150, 170)]
    rh = (h - 28) / rows
    for r in range(rows):
        by = y - 14 - r * rh
        c.line([(x - w / 2 + 14, by), (x + w / 2 - 14, by)], OUT, 4)
        xx = x - w / 2 + 24
        i = 0
        while xx < x + w / 2 - 40:
            bw = 22 + ((i + r + seed) * 7 % 3) * 7
            bh = rh * (.6 + ((i * 5 + r + seed) % 4) * .09)
            col = cols[(i * 3 + r * 5 + seed) % len(cols)]
            c.rect(xx, by - bh, xx + bw, by - 3, col, 3, OUT)
            xx += bw + 6
            i += 1


def lukisan(c, x, y, w=150, h=110, col=BIRU_MUDA):
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, KAYU, OW, OUT)
    c.rect(x - w / 2 + 12, y - h / 2 + 12, x + w / 2 - 12, y + h / 2 - 12, col, 0)
    c.poly([(x - w / 2 + 12, y + h / 2 - 12), (x - 14, y - 6), (x + 18, y + h / 2 - 12)], HIJAU, 3, OUT)
    c.ell(x + w * .2, y - h * .15, 11, 11, KUNING)


def karpet(c, x, w=620, col=PINK_MUDA, y=60):
    c.ell(x, y, w / 2, 40, col, OW, OUT)
    c.ell(x, y, w / 2 - 50, 24, None, 3, terang(col, -0.0) if False else mix(col, (255, 255, 255), .5))


def glow(c, x, y, r, col=(255, 214, 120), a=70, n=7):
    for i in range(n):
        k = 1 - i / n
        c.ell(x, y, r * (.35 + .65 * k), r * (.35 + .65 * k) * .9, col + (int(a * (1 - k) * .55 + 6),))


# ================================================================= KAMAR
def kamar_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (255, 236, 220) if wk != "malam" else (60, 72, 150))
    c.rect(X0, -300, X1, 0, mix((255, 236, 220), (240, 200, 180), .5) if wk != "malam" else (52, 62, 134))   # lis dinding bawah
    c.line([(X0, -300), (X1, -300)], OUT, 3)
    lantai(c, KAYU if wk != "malam" else (150, 112, 100), garis=KAYU_TUA if wk != "malam" else (120, 90, 90))
    jendela(c, 520, -520, 320, 300, o)
    # tirai
    c.poly([(330, -690), (400, -690), (386, -300), (330, -300)], (255, 150, 170), OW, OUT)
    c.poly([(640, -690), (710, -690), (710, -300), (654, -300)], (255, 150, 170), OW, OUT)
    # tempat tidur (kepala di kiri)
    c.rect(-640, -430, -590, 0, COKLAT, OW, OUT, r=8)
    c.rect(-640, -470, -560, -410, COKLAT, OW, OUT, r=18)
    c.rect(-600, -150, 40, -40, (236, 200, 168), OW, OUT, r=12)    # rangka
    c.rect(-596, -180, 36, -110, (250, 244, 250), OW, OUT, r=26)     # kasur
    c.rect(-596, -80, 36, 0, COKLAT, OW, OUT, r=8)
    c.rect(-560, -250, -420, -150, (250, 214, 232) if wk != "malam" else (190, 190, 240), OW, OUT, r=28)    # bantal
    # boneka kelinci
    bx, by = -290, -190
    for sg in (-1, 1):
        c.blob([(bx + sg * 12, by - 70), (bx + sg * 26, by - 130), (bx + sg * 40, by - 112), (bx + sg * 32, by - 66)], (255, 244, 238), OW * .8, OUT)
    c.ell(bx, by - 30, 50, 44, (255, 244, 238), OW * .8, OUT)
    c.ell(bx - 16, by - 34, 4, 5, OUT); c.ell(bx + 16, by - 34, 4, 5, OUT)
    c.ell(bx, by - 22, 4, 3, PINK_TUA)
    # nakas + jam digital
    c.rect(70, -170, 300, 0, COKLAT, OW, OUT, r=6)
    c.rect(78, -160, 292, -90, KAYU, 3, OUT)
    c.ell(185, -125, 6, 6, OUT)
    benda_jam(c, 185, -214, o, t)
    # rak
    c.rect(-980, -520, -760, -496, KAYU_TUA, OW, OUT, r=4)
    tanaman(c, -910, -496, .55)
    for i, col in enumerate((MERAH, BIRU, KUNING)):
        c.rect(-840 + i * 22, -586 + (i % 2) * 8, -820 + i * 22, -498, col, 3, OUT)
    lukisan(c, -250, -600, 190, 140)
    lukisan(c, 880, -600, 130, 100, (255, 214, 190))
    karpet(c, 160, 700, PINK_MUDA if wk != "malam" else (120, 110, 200), 150)
    if wk == "malam":
        glow(c, 185, -300, 260, (255, 210, 120), 90)
    tint(c, o)


def benda_jam(c, x, y, o, t):
    import benda
    benda.weker(c, benda._T(x, y, 1, 0), 1.0, t, jam=o.get("jam", "07:00"), on=bool(o.get("alarm")))


def kamar_f(c, t, o):
    # selimut menutupi badan (hanya bila ada tokoh di tempat tidur: opsi selimut)
    if o.get("selimut", True):
        col = o.get("selimut_warna", PINK)
        if o.get("selimut_warna") is None:
            col = PINK if waktu_of(o) != "malam" else (240, 150, 190)
        c.blob([(-400, -196), (-300, -224), (-120, -206), (30, -172), (54, -40), (-400, -40)], col, OW, OUT, n=7)
        c.curve([(-340, -150), (-200, -170), (-60, -146)], gelap(col, .12), 4)
    tint(c, o, True)


# ================================================================= SEKOLAH LUAR
def sekolah_luar_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    # bukit jauh
    c.set_depth(0.45)
    c.blob([(-1800, 0), (-1400, -150), (-900, -90), (-500, -190), (-100, -80), (400, -160), (900, -70), (1500, -170), (2000, 0)], mix(HIJAU_MUDA, (170, 215, 235), .45), 0)
    c.set_depth(0.8)
    pohon(c, -980, .9, HIJAU_TUA)
    pohon(c, 1300, .85, HIJAU_TUA)
    c.set_depth(1.0)
    rumput(c, warna=(150, 214, 126))
    c.poly([(-150, 0), (150, 0), (360, 420), (-360, 420)], (240, 226, 200), OW, OUT)   # jalan masuk
    # gedung
    bx = 260
    c.rect(bx - 560, -430, bx + 560, 0, (252, 238, 212), OW, OUT)
    c.poly([(bx - 600, -430), (bx + 600, -430), (bx + 520, -520), (bx - 520, -520)], (238, 124, 100), OW, OUT)
    c.rect(bx - 640, -450, bx + 640, -425, (222, 100, 84), OW, OUT)
    for sx in (-1, 1):
        for i in range(2):
            wx = bx + sx * (250 + i * 150) + (0 if sx > 0 else 0)
            c.rect(wx - 52, -340, wx + 52, -150, (178, 212, 250), OW, OUT)
            c.line([(wx, -340), (wx, -150)], OUT, 3.4)
            c.line([(wx - 52, -245), (wx + 52, -245)], OUT, 3.4)
    # pintu
    c.rect(bx - 130, -330, bx + 130, 0, (60, 110, 200), OW, OUT)
    c.line([(bx, -330), (bx, 0)], OUT, OW)
    for sx in (-1, 1):
        c.rect(bx + sx * 100 - 36 if sx < 0 else bx + 24, -290, bx + sx * 100 + 36 if sx > 0 else bx - 24, -170, (150, 196, 248), 3, OUT)
    c.rect(bx - 170, -360, bx + 170, -330, (240, 226, 196), OW, OUT)
    papan_nama(c, bx, -420, 330, 96, o.get("papan", "SMP"), (255, 226, 130), 66)
    for i in range(4):
        c.rect(bx - 190 + i * 8, -i * 14, bx + 190 - i * 8, -i * 14 + 14, (232, 224, 208), 3, OUT)
    # tiang bendera
    c.line([(-600, 0), (-600, -700)], OUT, 8)
    c.poly([(-596, -700), (-440, -700 + 10 * math.sin(t * 3)), (-440, -640 + 10 * math.sin(t * 3 + 1)), (-596, -640)], MERAH, 3.4, OUT)
    c.poly([(-596, -640), (-440, -640 + 10 * math.sin(t * 3 + 1)), (-440, -590 + 10 * math.sin(t * 3)), (-596, -590)], PUTIH, 3.4, OUT)
    semak(c, -200, 240, 100)
    semak(c, 760, 300, 110)
    tint(c, o)


def sekolah_luar_f(c, t, o):
    c.set_depth(1.25)
    semak(c, -900, 380, 190, HIJAU, y=120)
    semak(c, 1000, 380, 190, HIJAU, y=140)
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= TAMAN
def taman_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    c.set_depth(0.4)
    for i in range(7):
        x = -1500 + i * 520
        c.blob([(x - 160, 0), (x - 120, -230 - (i % 3) * 70), (x, -300 - (i % 2) * 60), (x + 130, -220), (x + 180, 0)], mix((130, 190, 150), (200, 225, 240), .5), 0)
    c.set_depth(0.75)
    for i, x in enumerate((-1500, -760, 700, 1450)):
        pohon(c, x, .78 + (i % 2) * .15, HIJAU_TUA if i % 2 else HIJAU)
    c.set_depth(1.0)
    rumput(c, warna=(142, 210, 120))
    c.poly([(-90, 0), (90, 0), (420, 420), (-420, 420)], (238, 224, 196), OW, OUT)
    pohon(c, -420, 1.15, HIJAU)
    pohon(c, 840, 1.0, (118, 196, 100))
    # bangku
    bx = 330
    c.rect(bx - 120, -130, bx + 120, -104, COKLAT, OW, OUT, r=4)
    c.rect(bx - 120, -200, bx + 120, -150, KAYU, OW, OUT, r=4)
    for sx in (-100, 100):
        c.rect(bx + sx - 8, -104, bx + sx + 8, 0, (80, 84, 100), OW, OUT)
    # bunga
    for i, col in enumerate((PINK, KUNING, PUTIH, PINK, KUNING)):
        fx = -140 - i * 70 + (i % 2) * 20
        c.line([(fx, 120), (fx, 70)], HIJAU_TUA, 4)
        c.ell(fx, 62, 13, 13, col, 3, OUT)
    semak(c, -840, 300, 100)
    semak(c, 360, 280, 100, HIJAU)
    tint(c, o)


def taman_f(c, t, o):
    c.set_depth(1.3)
    semak(c, 1100, 420, 200, HIJAU, y=160)
    semak(c, -1100, 380, 180, HIJAU_TUA, y=150)
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= KELAS
def kelas_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (255, 247, 226))
    c.rect(X0, -260, X1, 0, (244, 226, 190), 0)
    c.line([(X0, -260), (X1, -260)], OUT, 3)
    lantai(c, (226, 190, 150), garis=(200, 160, 120))
    # papan tulis
    c.rect(-520, -620, 220, -240, (190, 140, 96), OW * 1.3, OUT, r=8)
    c.rect(-500, -600, 200, -260, (52, 112, 96), OW, OUT)
    tx = o.get("papan_tulis", "")
    if tx:
        c.text(-150, -430, tx, 62, (240, 248, 240), "bulat")
    else:
        for i, (w, y) in enumerate(((300, -540), (420, -490), (240, -440), (380, -390))):
            c.curve([(-460, y), (-460 + w * .5, y - 8), (-460 + w, y + 4)], (236, 244, 236), 5)
        c.curve([(-70, -340), (-20, -330), (40, -344)], (255, 226, 130), 5)
    c.rect(-480, -250, 180, -232, (150, 100, 64), OW, OUT)
    c.rect(-100, -262, -30, -244, (240, 240, 240), 3, OUT)
    # jendela kanan
    jendela(c, 620, -480, 320, 300, o)
    jendela(c, 1100, -480, 280, 300, o)
    # jam dinding
    c.ell(-760, -620, 56, 56, PUTIH, OW, OUT)
    ang = (t * 0.2) % (2 * math.pi)
    c.line([(-760, -620), (-760 + math.sin(ang) * 36, -620 - math.cos(ang) * 36)], OUT, 4)
    c.line([(-760, -620), (-760 + 28, -620 + 6)], OUT, 5)
    # poster
    lukisan(c, -900, -450, 120, 150, (200, 230, 255))
    # meja guru
    c.rect(300, -190, 700, -164, COKLAT, OW, OUT, r=4)
    c.rect(318, -164, 682, 0, KAYU, OW, OUT)
    tanaman(c, 380, -190, .42)
    tint(c, o)


def kelas_f(c, t, o):
    # barisan meja siswa di depan
    if o.get("meja_depan", True):
        c.set_depth(1.15)
        for x in (-860, 900):
            c.rect(x - 150, 150, x + 150, 190, KAYU, OW, OUT, r=4)
            c.rect(x - 120, 190, x - 100, 330, (90, 96, 116), OW, OUT)
            c.rect(x + 100, 190, x + 120, 330, (90, 96, 116), OW, OUT)
        c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= RUANG BELAJAR
def ruang_belajar_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (255, 232, 202) if wk != "malam" else (86, 76, 120))
    lantai(c, KAYU, garis=KAYU_TUA)
    rak_buku(c, -640, 0, 360, 760, 5)
    jendela(c, 700, -560, 280, 300, o)
    # papan gabus + sticky notes
    c.rect(-100, -740, 360, -480, (206, 150, 96), OW, OUT, r=6)
    for i, (x, y, col) in enumerate(((-60, -700, KUNING_MUDA), (50, -690, PINK_MUDA), (160, -706, BIRU_MUDA), (270, -690, HIJAU_MUDA), (-20, -580, PINK_MUDA), (150, -590, KUNING_MUDA), (270, -560, BIRU_MUDA))):
        c.rect(x - 38, y - 36, x + 38, y + 36, col, 3, OUT)
        c.line([(x - 22, y - 12), (x + 22, y - 12)], ABU_TUA, 3, False)
        c.line([(x - 22, y + 8), (x + 10, y + 8)], ABU_TUA, 3, False)
    # kursi (sandaran di belakang tokoh)
    kx = o.get("kursi_x", 230)
    c.rect(kx - 80, -340, kx + 80, -120, (96, 102, 140), OW, OUT, r=18)
    c.line([(kx, -120), (kx, 0)], OUT, 12)
    # lampu meja
    lx = o.get("lampu_x", 560)
    c.line([(lx, -132), (lx - 10, -250), (lx + 70, -340)], (60, 66, 96), 11)
    c.poly([(lx + 40, -350), (lx + 130, -330), (lx + 100, -288), (lx + 24, -308)], (46, 52, 86), OW, OUT)
    if wk == "malam" or o.get("lampu_nyala", True):
        glow(c, lx + 80, -290, 340, (255, 220, 140), 120)
    tint(c, o)
    if wk == "malam" or o.get("lampu_nyala", True):
        glow(c, lx + 80, -290, 380, (255, 214, 130), 70)


def ruang_belajar_f(c, t, o):
    # meja di depan tokoh (permukaan y=-132)
    c.rect(-60, -134, 760, -102, KAYU, OW, OUT, r=6)
    c.rect(-40, -102, 740, 0, (214, 160, 108), OW, OUT)
    c.rect(150, -102, 430, -30, (196, 142, 96), OW, OUT)
    c.ell(290, -66, 8, 8, OUT)
    for i, (w, col) in enumerate(((190, BIRU), (170, MERAH), (150, HIJAU))):
        c.rect(590 - w / 2, -134 - (i + 1) * 30, 590 + w / 2 + (i % 2) * 10, -134 - i * 30, col, OW * .8, OUT, r=3)
    c.rect(-20, -200, 40, -134, PINK, OW, OUT, r=8)
    for i, col in enumerate((BIRU, KUNING, MERAH)):
        c.line([(-10 + i * 18, -200), (-16 + i * 22, -252)], col, 8)
    tint(c, o, True)


# ================================================================= RUANG TAMU
def ruang_tamu_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (224, 238, 250) if wk != "malam" else (70, 84, 150))
    c.rect(X0, -240, X1, 0, (206, 224, 242) if wk != "malam" else (60, 72, 136), 0)
    c.line([(X0, -240), (X1, -240)], OUT, 3)
    lantai(c, (232, 196, 158), garis=(208, 170, 132))
    karpet(c, -120, 900, (255, 186, 190), 190)
    # sofa
    sx = o.get("sofa_x", -200)
    sc = (118, 142, 214)
    c.rect(sx - 330, -330, sx + 330, -90, gelap(sc, .08), OW, OUT, r=48)
    c.rect(sx - 380, -210, sx - 300, 0, sc, OW, OUT, r=30)
    c.rect(sx + 300, -210, sx + 380, 0, sc, OW, OUT, r=30)
    c.rect(sx - 300, -100, sx + 300, 0, terang(sc, .12), OW, OUT, r=26)
    c.line([(sx, -100), (sx, -16)], OUT, 3)
    c.rect(sx - 280, -310, sx - 170, -190, PINK, OW, OUT, r=22)
    c.rect(sx + 170, -300, sx + 280, -190, KUNING, OW, OUT, r=22)
    # kucing oranye di kanan
    kx, ky = sx + 340, -212
    c.ell(kx, ky - 30, 70, 38, ORANYE, OW, OUT)
    c.ell(kx - 54, ky - 54, 34, 30, ORANYE, OW, OUT)
    for sg in (-1, 1):
        c.poly([(kx - 54 + sg * 12, ky - 76), (kx - 54 + sg * 30, ky - 100), (kx - 54 + sg * 32, ky - 70)], ORANYE, 3, OUT)
    c.line([(kx - 64, ky - 54), (kx - 58, ky - 52)], OUT, 3); c.line([(kx - 48, ky - 54), (kx - 42, ky - 52)], OUT, 3)
    c.curve([(kx + 66, ky - 26), (kx + 112, ky - 34 + 10 * math.sin(t * 2.4)), (kx + 130, ky - 70 + 14 * math.sin(t * 2.4))], ORANYE, 12)
    # TV & tanaman
    c.rect(560, -420, 1000, -170, (40, 44, 60), OW, OUT, r=10)
    c.rect(576, -404, 984, -186, (120, 196, 250) if wk != "malam" else (140, 160, 250), 0)
    c.rect(520, -170, 1040, 0, KAYU, OW, OUT)
    tanaman(c, -760, 0, 1.2, PINK_TUA)
    jendela(c, -760, -560, 260, 260, o) if False else lukisan(c, -700, -520, 220, 150, (255, 214, 190))
    lukisan(c, 240, -560, 240, 160)
    tint(c, o)


def ruang_tamu_f(c, t, o):
    tint(c, o, True)


# ================================================================= JALAN KAMPUNG / KOMPLEK
def rumah(c, x, w=360, h=280, tembok=(255, 232, 200), atap=(236, 120, 96)):
    c.rect(x - w / 2, -h, x + w / 2, 0, tembok, OW, OUT)
    c.poly([(x - w / 2 - 30, -h), (x + w / 2 + 30, -h), (x + w / 2 - 40, -h - 110), (x - w / 2 + 40, -h - 110)], atap, OW, OUT)
    c.rect(x - 38, -170, x + 38, 0, (168, 112, 70), OW, OUT)
    c.rect(x - w / 2 + 36, -210, x - w / 2 + 120, -130, (178, 212, 250), OW, OUT)
    c.rect(x + w / 2 - 120, -210, x + w / 2 - 36, -130, (178, 212, 250), OW, OUT)


def jalan_b(c, t, o):
    langit(c, o)
    awan_set(c, o, 8)
    c.set_depth(0.35)
    x0, x1, _, _ = c.visible(400)
    per = 520
    i0 = int(math.floor(x0 / per)) - 1
    i1 = int(math.ceil(x1 / per)) + 1
    for i in range(i0, i1 + 1):
        h = 180 + (i * 53 % 4) * 40
        col = mix((176, 200, 230), (255, 232, 210), (i * 7 % 5) / 5) if waktu_of(o) != "malam" else (60, 70, 130)
        c.rect(i * per - 150, -h, i * per + 150, 40, col, 0)
        c.poly([(i * per - 170, -h), (i * per + 170, -h), (i * per + 110, -h - 70), (i * per - 110, -h - 70)], mix(col, (200, 120, 110), .5), 0)
    c.set_depth(0.7)
    x0, x1, _, _ = c.visible(500)
    per = 700
    for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
        if i % 2 == 0:
            pohon(c, i * per + 120, .72, HIJAU if i % 4 else HIJAU_TUA)
        else:
            rumah(c, i * per, 330, 230, [(255, 232, 200), (212, 236, 250), (255, 214, 214), (226, 244, 214)][i % 4], [(236, 120, 96), (120, 150, 210)][i % 2])
    c.set_depth(1.0)
    # trotoar + jalan
    c.rect(X0, 0, X1, 120, (214, 212, 208), OW, OUT)
    c.rect(X0, 120, X1, 1400, (96, 100, 116))
    c.line([(X0, 120), (X1, 120)], OUT, OW)
    x0, x1, _, _ = c.visible(300)
    for i in range(int(math.floor(x0 / 180)) - 1, int(math.ceil(x1 / 180)) + 2):
        c.line([(i * 180, 0), (i * 180, 120)], (190, 188, 184), 3)
    for i in range(int(math.floor(x0 / 320)) - 1, int(math.ceil(x1 / 320)) + 2):
        c.rect(i * 320, 330, i * 320 + 190, 350, (250, 250, 240), 0)
    # tiang lampu
    per = 1100
    for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
        px = i * per + 420
        c.rect(px - 7, -420, px + 7, 0, (70, 76, 96), OW * .8, OUT)
        c.line([(px, -420), (px + 70, -440)], (70, 76, 96), 9)
        c.ell(px + 76, -436, 20, 14, (255, 236, 150), 3, OUT)
        if waktu_of(o) == "malam":
            glow(c, px + 76, -420, 240, (255, 226, 130), 100)
    tint(c, o)


def jalan_f(c, t, o):
    tint(c, o, True)


# ================================================================= KANTIN
def kantin_b(c, t, o):
    dinding(c, (255, 240, 214))
    lantai(c, (214, 200, 180), garis=(190, 176, 156))
    # kios dengan atap garis-garis
    c.rect(-300, -380, 700, -40, (255, 226, 160), OW, OUT)
    c.rect(-340, -120, 740, -80, KAYU_TUA, OW, OUT)
    c.rect(-340, -80, 740, 0, COKLAT, OW, OUT)
    for i in range(10):
        col = MERAH if i % 2 == 0 else PUTIH
        x = -340 + i * 108
        c.poly([(x, -470), (x + 108, -470), (x + 120, -380), (x - 12, -380)], col, OW * .8, OUT)
    papan_nama(c, 200, -520, 360, 70, o.get("papan", "KANTIN"), (255, 255, 255), 48)
    # menu & makanan
    for i, (x, col) in enumerate(((-180, ORANYE), (20, KUNING), (220, PINK), (420, HIJAU_MUDA))):
        c.ell(x, -150, 70, 22, PUTIH, OW * .8, OUT)
        c.blob([(x - 52, -160), (x, -210), (x + 52, -160)], col, OW * .8, OUT)
    # meja + bangku
    for tx in (-980, 1000):
        c.rect(tx - 170, -180, tx + 170, -150, KAYU, OW, OUT, r=4)
        c.rect(tx - 10, -150, tx + 10, 0, (90, 96, 116), OW, OUT)
        for sg in (-1, 1):
            c.rect(tx + sg * 190 - 50, -90, tx + sg * 190 + 50, -66, COKLAT, OW, OUT, r=4)
            c.rect(tx + sg * 190 - 6, -66, tx + sg * 190 + 6, 0, (90, 96, 116), OW * .8, OUT)
    tint(c, o)


def kantin_f(c, t, o):
    tint(c, o, True)


# ================================================================= LAPANGAN
def lapangan_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    c.set_depth(0.5)
    c.rect(-2400, -120, 2400, 0, (170, 190, 170), 0)
    for i in range(-14, 15):
        c.rect(i * 160 - 4, -120, i * 160 + 4, 0, (110, 130, 120), 0)
    c.set_depth(0.7)
    for i, x in enumerate((-1400, -500, 900, 1700)):
        pohon(c, x, .7 + (i % 2) * .1, HIJAU_TUA)
    c.set_depth(1.0)
    c.rect(X0, 0, X1, 1400, (118, 200, 108))
    for i in range(-8, 9):
        if i % 2 == 0:
            c.rect(i * 260, 0, i * 260 + 260, 1400, (108, 190, 98), 0)
    c.line([(X0, 0), (X1, 0)], OUT, OW)
    c.line([(-1600, 260), (1600, 260)], PUTIH, 8)
    c.ell(0, 260, 220, 90, None, 8, PUTIH)
    # gawang
    for gx, sg in ((-1050, 1), (1050, -1)):
        c.line([(gx, 0), (gx, -250)], PUTIH, 12)
        c.line([(gx, -250), (gx + sg * 150, -230), (gx + sg * 150, 0)], PUTIH, 10)
        for i in range(1, 6):
            c.line([(gx + sg * 150 * i / 6, -240 + 10 * i / 6), (gx + sg * 150 * i / 6, 0)], (255, 255, 255, 130), 3, False)
    tint(c, o)


def lapangan_f(c, t, o):
    tint(c, o, True)


# ================================================================= RUMAH DEPAN
def rumah_depan_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    c.set_depth(0.75)
    pohon(c, -1100, .9, HIJAU_TUA)
    pohon(c, 1250, .8, HIJAU)
    c.set_depth(1.0)
    rumput(c, warna=(150, 214, 126))
    rumah(c, 0, 900, 380, (255, 236, 206), (232, 112, 92))
    c.rect(-72, -250, 72, 0, (168, 112, 70), OW, OUT)
    c.ell(46, -120, 7, 7, KUNING, 3, OUT)
    c.rect(-380, -300, -230, -170, (178, 212, 250), OW, OUT)
    c.rect(230, -300, 380, -170, (178, 212, 250), OW, OUT)
    c.line([(-305, -300), (-305, -170)], OUT, 3.4); c.line([(305, -300), (305, -170)], OUT, 3.4)
    c.poly([(-120, 0), (120, 0), (260, 420), (-260, 420)], (238, 224, 196), OW, OUT)
    for i in range(-9, 10):
        if abs(i * 56) > 230 or True:
            c.rect(i * 56 - 16, 40 if i % 2 == 0 else 46, i * 56 + 16, 150, PUTIH, 3.4, OUT) if abs(i * 56) > 300 else None
    c.line([(-1100, 70), (-300, 70)], OUT, 4); c.line([(300, 70), (1100, 70)], OUT, 4)
    tint(c, o)


def rumah_depan_f(c, t, o):
    tint(c, o, True)


# ================================================================= MEJA MAKAN / DAPUR
def meja_makan_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (255, 240, 214))
    lantai(c, (226, 196, 160), garis=(204, 172, 136))
    jendela(c, -520, -540, 300, 280, o)
    c.rect(300, -440, 900, -420, KAYU_TUA, OW, OUT)
    for i, col in enumerate((MERAH, KUNING, HIJAU, BIRU)):
        c.ell(380 + i * 130, -490, 44, 52, col, OW * .8, OUT)
    lukisan(c, 80, -560, 200, 140, (255, 214, 190))
    # kursi belakang
    for kx in (-340, 200):
        c.rect(kx - 70, -330, kx + 70, -130, KAYU_TUA, OW, OUT, r=14)
    tint(c, o)


def meja_makan_f(c, t, o):
    c.rect(-640, -230, 560, -196, KAYU, OW, OUT, r=8)
    c.rect(-600, -196, 520, -150, KAYU_TUA, OW, OUT)
    for sx in (-560, 480):
        c.rect(sx - 14, -150, sx + 14, 0, KAYU_TUA, OW, OUT)
    for x, col in ((-380, BIRU_MUDA), (-60, PINK_MUDA), (260, KUNING_MUDA)):
        c.ell(x, -226, 82, 18, PUTIH, OW * .8, OUT)
        c.blob([(x - 50, -236), (x, -290), (x + 50, -236)], col, OW * .8, OUT)
    c.poly([(380, -230), (420, -230), (412, -290), (388, -290)], (240, 248, 255), OW * .8, OUT)
    tint(c, o, True)


# ================================================================= PADANG / POLOS
def padang_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    c.set_depth(0.4)
    c.blob([(-2400, 0), (-1700, -280), (-900, -120), (-200, -330), (700, -140), (1500, -300), (2400, 0)], (150, 212, 150), 0)
    c.set_depth(0.7)
    c.blob([(-2400, 40), (-1500, -150), (-400, -40), (600, -180), (1800, -60), (2400, 40)], (118, 196, 118), 0)
    pohon(c, 900, .8, HIJAU_TUA)
    c.set_depth(1.0)
    rumput(c, warna=(132, 206, 112))
    for i in range(-10, 11):
        fx = i * 150 + (i * 37 % 60)
        c.line([(fx, 160 + (i % 3) * 60), (fx, 120 + (i % 3) * 60)], HIJAU_TUA, 4)
        c.ell(fx, 112 + (i % 3) * 60, 10, 10, [PINK, KUNING, PUTIH][i % 3], 3, OUT)
    tint(c, o)


def padang_f(c, t, o):
    tint(c, o, True)


def polos_b(c, t, o):
    col = o.get("warna", "krem")
    from tokoh import warna as _w
    base = _w(col, (255, 243, 226)) if isinstance(col, str) else tuple(col)
    c.gradient(terang(base, .35), base)
    # lingkaran lembut saja (TANPA partikel/konfeti kecil di latar: permintaan user, latar harus bersih)
    c.set_depth(0.5)
    c.ell(220, -330, 520, 520, mix(base, (255, 255, 255), .5))
    c.ell(-760, -520, 190, 190, mix(base, (255, 255, 255), .35))
    c.set_depth(1.0)
    c.rect(X0, 0, X1, 1400, mix(base, (255, 255, 255), .25) if not o.get("lantai") else (240, 223, 195))
    c.line([(X0, 0), (X1, 0)], OUT, 3)


def polos_f(c, t, o):
    pass


SET = {
    "kamar": (kamar_b, kamar_f), "sekolah_luar": (sekolah_luar_b, sekolah_luar_f), "sekolah": (sekolah_luar_b, sekolah_luar_f),
    "taman": (taman_b, taman_f), "kelas": (kelas_b, kelas_f), "ruang_belajar": (ruang_belajar_b, ruang_belajar_f),
    "ruang_tamu": (ruang_tamu_b, ruang_tamu_f), "jalan": (jalan_b, jalan_f), "kantin": (kantin_b, kantin_f),
    "lapangan": (lapangan_b, lapangan_f), "rumah_depan": (rumah_depan_b, rumah_depan_f), "meja_makan": (meja_makan_b, meja_makan_f),
    "padang": (padang_b, padang_f), "polos": (polos_b, polos_f),
}
ALIAS = {"kamar_tidur": "kamar", "gerbang_sekolah": "sekolah_luar", "halaman_sekolah": "taman", "dapur": "meja_makan",
         "ruang_keluarga": "ruang_tamu", "meja_belajar": "ruang_belajar", "komplek": "jalan", "kampung": "jalan", "luar": "padang"}


def set_of(name):
    name = ALIAS.get(name, name)
    return SET.get(name, SET["polos"])
