# -*- coding: utf-8 -*-
"""
rid2d.py - engine gambar kartun flat untuk skill "rid animations".

Isi: palet warna, font, karakter (pria berpeci & wanita berhijab pink) dengan
ekspresi + pose + mulut lipsync, ikon/props, latar, kartu, pil judul, balon kata,
teks kaya (**aksen**), easing. Semua digambar lewat kode (Pillow), supersampling
lalu diperkecil supaya garis halus. Semua fungsi yang mahal di-cache.
"""
import math, os, glob, functools, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

SS = 3  # supersampling untuk sprite

# ---------------------------------------------------------------- palet
OUT = (40, 42, 58)
SKIN = (250, 214, 180)
SKIN_SH = (236, 186, 148)
SKIN_LINE = (196, 132, 100)
HAIR = (30, 30, 38)
PECI = (26, 26, 32)
PECI_HI = (70, 72, 84)
SHIRT = (251, 251, 253)
SHIRT_SH = (220, 225, 236)
BUTTON = (196, 202, 214)
HIJAB = (234, 130, 162)
HIJAB_SH = (208, 98, 136)
HIJAB_HI = (244, 166, 190)
GSHIRT = (253, 242, 238)
MOUTH = (176, 40, 56)
TONGUE = (244, 116, 120)
BLUSH = (246, 150, 160)
EYE = (22, 22, 30)
WHITE = (255, 255, 255)

NAVY = (36, 52, 104)
BLUE = (40, 104, 214)
RED = (226, 52, 52)
ORANGE = (244, 120, 40)
YELLOW = (250, 200, 40)
GOLD = (244, 196, 70)
GOLD_SH = (214, 160, 40)
GREEN = (52, 168, 92)
GREEN_L = (120, 200, 110)
PINK = (244, 150, 178)
BROWN = (170, 112, 64)
BROWN_D = (128, 80, 44)
CARD = (255, 255, 255)
TEXT = (30, 40, 70)

LATAR = {  # gradien atas -> bawah
    "biru": ((222, 236, 252), (200, 222, 248)),
    "krem": ((253, 244, 228), (248, 232, 206)),
    "hijau": ((228, 244, 220), (204, 232, 196)),
    "ungu": ((236, 232, 250), (216, 210, 244)),
    "pink": ((252, 232, 240), (246, 214, 228)),
    "kuning": ((254, 246, 214), (250, 232, 176)),
    "abu": ((240, 242, 246), (222, 226, 234)),
}

# ---------------------------------------------------------------- font
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIRS = [os.path.join(HERE, "..", "assets", "fonts")]


def _fc(q):
    try:
        return subprocess.run(["fc-match", "-f", "%{file}", q], capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


@functools.lru_cache(None)
def font_path(weight="black"):
    """Font tebal membulat diutamakan (taruh Nunito/Baloo/Fredoka .ttf di assets/fonts)."""
    want = {"black": ["Black", "ExtraBold", "Heavy", "Bold"],
            "bold": ["ExtraBold", "Bold", "SemiBold"],
            "semi": ["SemiBold", "Bold", "Medium"]}[weight]
    for d in FONT_DIRS:
        files = glob.glob(os.path.join(d, "*.ttf")) + glob.glob(os.path.join(d, "*.otf"))
        for w in want:
            for f in files:
                if w.lower() in os.path.basename(f).lower():
                    return f
        if files:
            return files[0]
    for fam in ["Nunito", "Baloo 2", "Fredoka", "Inter", "Liberation Sans", "DejaVu Sans"]:
        for w in want:
            f = _fc(f"{fam}:style={w}")
            if f and fam.split()[0].lower() in os.path.basename(f).lower():
                return f
    return _fc("sans:bold")


@functools.lru_cache(None)
def font(size, weight="black"):
    return ImageFont.truetype(font_path(weight), max(6, int(size)))


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x); return 3 * x * x - 2 * x * x * x


def ease_back(x, s=1.7):
    x = clamp(x) - 1; return 1 + x * x * ((s + 1) * x + s)


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- pena
class Pen:
    """Menggambar dengan koordinat 'unit' yang diskalakan k (untuk supersampling)."""

    def __init__(self, img, k, ow=6):
        self.img = img; self.d = ImageDraw.Draw(img); self.k = k; self.ow = ow

    def P(self, x, y):
        return (x * self.k, y * self.k)

    def B(self, x0, y0, x1, y1):
        return [x0 * self.k, y0 * self.k, x1 * self.k, y1 * self.k]

    def W(self, w):
        return max(1, int(round(w * self.k)))

    def _o(self, ow):
        ow = self.ow if ow is None else ow
        return (OUT, self.W(ow)) if ow else (None, 0)

    def ell(self, x0, y0, x1, y1, fill, ow=None, oc=None):
        o, w = self._o(ow)
        self.d.ellipse(self.B(x0, y0, x1, y1), fill=fill, outline=(oc or o) if w else None, width=w)

    def rr(self, x0, y0, x1, y1, r, fill, ow=None, oc=None):
        o, w = self._o(ow)
        self.d.rounded_rectangle(self.B(x0, y0, x1, y1), radius=r * self.k, fill=fill,
                                 outline=(oc or o) if w else None, width=w)

    def poly(self, pts, fill, ow=None, oc=None):
        o, w = self._o(ow)
        P = [self.P(*p) for p in pts]
        self.d.polygon(P, fill=fill)
        if w:
            self.d.line(P + [P[0], P[1]], fill=oc or o, width=w, joint="curve")

    def line(self, pts, w, fill, ow=None, cap=True):
        """Garis tebal dengan outline (untuk lengan, batang, dsb)."""
        ow = self.ow if ow is None else ow
        P = [self.P(*p) for p in pts]
        if ow:
            ww = self.W(w + 2 * ow)
            self.d.line(P, fill=OUT, width=ww, joint="curve")
            if cap:
                for q in (P[0], P[-1]):
                    self.d.ellipse([q[0] - ww / 2, q[1] - ww / 2, q[0] + ww / 2, q[1] + ww / 2], fill=OUT)
        ww = self.W(w)
        self.d.line(P, fill=fill, width=ww, joint="curve")
        if cap:
            for q in (P[0], P[-1]):
                self.d.ellipse([q[0] - ww / 2, q[1] - ww / 2, q[0] + ww / 2, q[1] + ww / 2], fill=fill)

    def stroke(self, pts, w, col=OUT):
        P = [self.P(*p) for p in pts]
        ww = self.W(w)
        self.d.line(P, fill=col, width=ww, joint="curve")
        for q in (P[0], P[-1]):
            self.d.ellipse([q[0] - ww / 2, q[1] - ww / 2, q[0] + ww / 2, q[1] + ww / 2], fill=col)

    def arc(self, x0, y0, x1, y1, a0, a1, w, col=OUT):
        self.d.arc(self.B(x0, y0, x1, y1), a0, a1, fill=col, width=self.W(w))

    def chord(self, x0, y0, x1, y1, a0, a1, fill, ow=None):
        o, w = self._o(ow)
        self.d.chord(self.B(x0, y0, x1, y1), a0, a1, fill=fill, outline=o if w else None, width=w)

    def soft(self, x0, y0, x1, y1, col, alpha=120):
        """Elips transparan (pipi merona, bayangan)."""
        lay = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse(self.B(x0, y0, x1, y1), fill=col + (alpha,))
        self.img.alpha_composite(lay)


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def _finish(img, out_w, out_h):
    return img.resize((max(1, int(out_w)), max(1, int(out_h))), Image.LANCZOS)


# ================================================================ KARAKTER
CW, CH, CX = 720, 680, 360   # kanvas sprite karakter (unit), pusat x

EKSPRESI = {
    # ekspresi: (mata, alis, mulut_dasar)
    "senang": ("buka", "normal", ("buka", 2)),
    "senyum": ("buka", "normal", ("senyum", 0)),
    "tertawa": ("tutup", "normal", ("buka", 3)),
    "kaget": ("besar", "naik", ("o", 0)),
    "mikir": ("buka", "miring", ("datar", 0)),
    "marah": ("buka", "marah", ("cemberut", 0)),
    "sedih": ("buka", "sedih", ("cemberut", 0)),
    "bingung": ("buka", "miring", ("o_kecil", 0)),
}
POSE = ["diam", "tunjuk_samping", "tunjuk_atas", "lambai", "kepal", "mikir", "dua_kepal"]


def _face(p, ey, ex, eyes, brows, mouth, blink, girl):
    C = CX
    # pipi
    if girl:
        p.soft(C - ex - 46, ey + 30, C - ex + 6, ey + 58, BLUSH, 150)
        p.soft(C + ex - 6, ey + 30, C + ex + 46, ey + 58, BLUSH, 150)
    else:
        p.soft(C - ex - 44, ey + 32, C - ex + 2, ey + 56, BLUSH, 70)
        p.soft(C + ex - 2, ey + 32, C + ex + 44, ey + 56, BLUSH, 70)
    # mata
    for s in (-1, 1):
        x = C + s * ex
        if blink:
            p.arc(x - 20, ey - 14, x + 20, ey + 14, 20, 160, 6)
        elif eyes == "tutup":
            p.arc(x - 21, ey - 8, x + 21, ey + 30, 200, 340, 7)
        else:
            r = 1.18 if eyes == "besar" else 1.0
            p.ell(x - 21 * r, ey - 30 * r, x + 21 * r, ey + 30 * r, EYE, ow=0)
            p.ell(x - 3, ey - 23 * r, x + 12, ey - 8 * r, WHITE, ow=0)
            p.ell(x - 12, ey + 9, x - 4, ey + 17, WHITE, ow=0)
    # alis
    by = ey - 50
    for s in (-1, 1):
        x = C + s * ex
        if brows == "marah":
            p.stroke([(x - s * 24, by + 2), (x + s * 18, by + 14)], 7)
        elif brows == "sedih":
            p.stroke([(x - s * 22, by + 14), (x + s * 18, by + 2)], 6)
        elif brows == "naik":
            p.arc(x - 22, by - 16, x + 22, by + 12, 200, 340, 6)
        elif brows == "miring" and s == 1:
            p.arc(x - 22, by - 18, x + 22, by + 10, 200, 340, 6)
        else:
            p.arc(x - 22, by - 8, x + 22, by + 18, 205, 335, 6)
    # hidung
    p.arc(C - 9, ey + 32, C + 9, ey + 46, 20, 160, 4, SKIN_LINE)
    # mulut
    my = ey + 72
    kind, lv = mouth
    if kind == "buka":
        o = {1: 0.35, 2: 0.7, 3: 1.0}.get(lv, 0.7)
        w = 26 + 12 * o; h = 14 + 30 * o
        lay = Image.new("RGBA", p.img.size, (0, 0, 0, 0))
        q = Pen(lay, p.k)
        q.chord(C - w, my - h, C + w, my + h, 0, 180, MOUTH, ow=0)
        q.ell(C - w * 0.6, my + h * 0.3, C + w * 0.6, my + h * 1.25, TONGUE, ow=0)
        m = Image.new("L", p.img.size, 0)
        ImageDraw.Draw(m).chord(p.B(C - w, my - h, C + w, my + h), 0, 180, fill=255)
        lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
        p.img.alpha_composite(lay)
        p.d.chord(p.B(C - w, my - h, C + w, my + h), 0, 180, outline=OUT, width=p.W(5))
    elif kind == "senyum":
        p.arc(C - 30, my - 26, C + 30, my + 14, 25, 155, 6)
    elif kind == "o":
        p.ell(C - 15, my - 6, C + 15, my + 30, MOUTH, ow=5)
    elif kind == "o_kecil":
        p.ell(C - 9, my + 2, C + 9, my + 20, MOUTH, ow=4)
    elif kind == "datar":
        p.stroke([(C - 20, my + 8), (C + 18, my + 6)], 6)
    elif kind == "cemberut":
        p.arc(C - 24, my + 4, C + 24, my + 36, 205, 335, 6)


def _hand_open(p, x, y, up=False, s=1.3):
    """Telapak terbuka dengan 4 jari + jempol. up=True: jari ke atas (melambai)."""
    base = -90 if up else -35
    fingers = []
    for a, l in zip((base - 33, base - 11, base + 11, base + 33), (34, 42, 40, 32)):
        r = math.radians(a)
        fingers.append([(x + math.cos(r) * 16 * s, y + math.sin(r) * 16 * s),
                        (x + math.cos(r) * (16 + l) * s, y + math.sin(r) * (16 + l) * s)])
    r = math.radians(base - 95 if up else base - 85)
    fingers.append([(x + math.cos(r) * 10 * s, y + math.sin(r) * 10 * s), (x + math.cos(r) * 40 * s, y + math.sin(r) * 40 * s)])
    fw = 15 * s
    for f in fingers:
        p.stroke(f, fw + 12, OUT)
    p.ell(x - 30 * s, y - 28 * s, x + 30 * s, y + 28 * s, SKIN, ow=6)
    for f in fingers:
        p.stroke(f, fw, SKIN)
    p.ell(x - 23 * s, y - 21 * s, x + 23 * s, y + 21 * s, SKIN, ow=0)


def _fist(p, x, y, index=False, s=1.3):
    if index:
        p.rr(x - 10 * s, y - 74 * s, x + 14 * s, y - 10 * s, 12 * s, SKIN)
    p.ell(x - 30 * s, y - 28 * s, x + 30 * s, y + 26 * s, SKIN)
    p.stroke([(x - 14 * s, y - 6 * s), (x + 16 * s, y - 6 * s)], 3, SKIN_LINE)


def _arm(p, pose, sleeve, girl):
    C = CX
    sh = (C + 150, 530) if not girl else (C + 158, 550)
    if pose == "tunjuk_samping":
        el, wr = (C + 242, 615), (C + 272, 505)
        p.line([sh, el, wr], 62, sleeve); _hand_open(p, wr[0] + 10, wr[1] - 22)
    elif pose == "tunjuk_atas":
        el, wr = (C + 232, 625), (C + 238, 505)
        p.line([sh, el, wr], 62, sleeve); _fist(p, wr[0], wr[1] - 20, index=True)
    elif pose == "lambai":
        el, wr = (C + 250, 540), (C + 262, 410)
        p.line([sh, el, wr], 60, sleeve); _hand_open(p, wr[0], wr[1] - 26, up=True)
    elif pose == "kepal":
        el, wr = (C + 228, 630), (C + 236, 515)
        p.line([sh, el, wr], 62, sleeve); _fist(p, wr[0], wr[1] - 24)
    elif pose == "mikir":
        el, wr = (C + 130, 660), (C + 40, 500)
        p.line([sh, el, wr], 60, sleeve); _fist(p, C + 34, 452 if not girl else 462)


def _arm_left_fist(p, sleeve, girl):
    C = CX
    sh = (C - 150, 530) if not girl else (C - 158, 550)
    el, wr = (C - 228, 630), (C - 236, 515)
    p.line([sh, el, wr], 62, sleeve); _fist(p, wr[0], wr[1] - 24)


def _boy(p, expr, mouth, blink, pose):
    C = CX
    eyes, brows, _ = EKSPRESI.get(expr, EKSPRESI["senang"])
    # badan (baju koko putih)
    p.rr(C - 196, 466, C + 196, 830, 120, SHIRT)
    p.stroke([(C - 134, 560), (C - 140, 700)], 4, SHIRT_SH)
    p.stroke([(C + 134, 560), (C + 140, 700)], 4, SHIRT_SH)
    p.stroke([(C, 500), (C, 700)], 4, SHIRT_SH)
    for by in (548, 600, 652):
        p.ell(C - 7, by - 7, C + 7, by + 7, BUTTON, ow=2)
    p.rr(C + 52, 566, C + 108, 618, 8, SHIRT, ow=4)
    # leher + kerah shanghai
    p.rr(C - 40, 395, C + 40, 492, 14, SKIN)
    p.soft(C - 40, 420, C + 40, 470, SKIN_SH, 200)
    p.poly([(C - 74, 482), (C - 44, 458), (C - 4, 494), (C - 6, 512), (C - 66, 506)], SHIRT, ow=5)
    p.poly([(C + 74, 482), (C + 44, 458), (C + 4, 494), (C + 6, 512), (C + 66, 506)], SHIRT, ow=5)
    if pose in ("dua_kepal",):
        _arm_left_fist(p, SHIRT, False); _arm(p, "kepal", SHIRT, False)
    elif pose != "diam":
        _arm(p, pose, SHIRT, False) if pose != "mikir" else None
    # telinga
    for s in (-1, 1):
        p.ell(C + s * 124 - 26, 222, C + s * 124 + 26, 300, SKIN)
        p.arc(C + s * 124 - 14, 238, C + s * 124 + 14, 284, 90 - s * 70 - 70, 90 - s * 70 + 70, 4, SKIN_LINE)
    # kepala
    head = (C - 128, 112, C + 128, 412)
    p.ell(*head, SKIN)
    # rambut cambang (dipotong mengikuti kepala)
    lay = Image.new("RGBA", p.img.size, (0, 0, 0, 0)); q = Pen(lay, p.k)
    q.rr(C - 150, 90, C + 150, 205, 10, HAIR, ow=0)
    for s in (-1, 1):
        q.poly([(C + s * 150, 150), (C + s * 72, 150), (C + s * 86, 206), (C + s * 104, 262), (C + s * 150, 280)], HAIR, ow=0)
    m = Image.new("L", p.img.size, 0); ImageDraw.Draw(m).ellipse(p.B(*head), fill=255)
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m)); p.img.alpha_composite(lay)
    p.d.ellipse(p.B(*head), outline=OUT, width=p.W(6))
    # peci hitam
    p.poly(bez((C - 136, 198), (C - 90, 186), (C + 90, 186), (C + 136, 198), 16)
           + [(C + 126, 84), (C + 112, 72), (C - 112, 72), (C - 126, 84)], PECI)
    p.soft(C - 104, 84, C - 30, 108, PECI_HI, 160)
    _face(p, 276, 50, eyes, brows, mouth, blink, False)
    if pose == "mikir":
        _arm(p, "mikir", SHIRT, False)


def _girl(p, expr, mouth, blink, pose):
    C = CX
    eyes, brows, _ = EKSPRESI.get(expr, EKSPRESI["senang"])
    # baju krem (lengan)
    p.rr(C - 224, 520, C + 224, 840, 130, GSHIRT)
    p.stroke([(C - 168, 600), (C - 176, 700)], 4, SHIRT_SH); p.stroke([(C + 168, 600), (C + 176, 700)], 4, SHIRT_SH)
    if pose == "dua_kepal":
        _arm_left_fist(p, GSHIRT, True); _arm(p, "kepal", GSHIRT, True)
    elif pose not in ("diam", "mikir"):
        _arm(p, pose, GSHIRT, True)
    # kerudung menjuntai menutup bahu & dada
    drape = bez((C - 110, 300), (C - 190, 420), (C - 200, 600), (C - 180, 760), 20) + \
        [(C + 180, 760)] + bez((C + 180, 760), (C + 200, 600), (C + 190, 420), (C + 110, 300), 20)
    p.poly(drape, HIJAB)
    p.arc(C - 150, 430, C + 150, 640, 35, 145, 5, HIJAB_SH)
    p.arc(C - 120, 500, C + 120, 720, 45, 135, 4, HIJAB_SH)
    # kepala kerudung
    p.ell(C - 148, 92, C + 148, 440, HIJAB)
    p.soft(C - 118, 106, C - 30, 176, HIJAB_HI, 150)
    # lipatan bawah dagu
    p.arc(C - 120, 350, C + 120, 470, 25, 155, 6, HIJAB_SH)
    # wajah
    p.ell(C - 116, 150, C + 116, 414, SKIN, ow=6)
    _face(p, 286, 50, eyes, brows, mouth, blink, True)
    if pose == "mikir":
        _arm(p, "mikir", GSHIRT, True)


@functools.lru_cache(maxsize=512)
def karakter(kind, h, expr="senang", mouth=None, blink=False, pose="diam", flip=False):
    """Sprite RGBA karakter setengah badan, tinggi h piksel.
    kind: 'pria' | 'wanita'. mouth: None (ikut ekspresi) atau ('buka',1..3)/('senyum',0)/..."""
    if mouth is None:
        mouth = EKSPRESI.get(expr, EKSPRESI["senang"])[2]
    if expr == "mikir" and pose == "diam":
        pose = "mikir"
    k = h / CH * SS
    img = Image.new("RGBA", (int(CW * k), int(CH * k)), (0, 0, 0, 0))
    p = Pen(img, k, ow=6)
    (_girl if kind == "wanita" else _boy)(p, expr, mouth, blink, pose)
    out = _finish(img, CW * h / CH, h)
    return out.transpose(Image.FLIP_LEFT_RIGHT) if flip else out


# ================================================================ IKON (kotak 200 unit)
def _arrow(p, x0, y0, x1, y1, w, col):
    ang = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0)
    hx, hy = math.cos(ang), math.sin(ang); nx, ny = -hy, hx
    hl = w * 1.6; hw = w * 1.25
    bx, by = x1 - hx * hl, y1 - hy * hl
    pts = [(x0 + nx * w / 2, y0 + ny * w / 2), (bx + nx * w / 2, by + ny * w / 2), (bx + nx * hw, by + ny * hw),
           (x1, y1), (bx - nx * hw, by - ny * hw), (bx - nx * w / 2, by - ny * w / 2), (x0 - nx * w / 2, y0 - ny * w / 2)]
    p.poly(pts, col)


def _coin(p, x, y, w=96):
    p.ell(x - w / 2, y, x + w / 2, y + 34, GOLD_SH)
    p.rr(x - w / 2, y - 10, x + w / 2, y + 17, 0, GOLD_SH, ow=0)
    p.stroke([(x - w / 2, y - 8), (x - w / 2, y + 17)], 6); p.stroke([(x + w / 2, y - 8), (x + w / 2, y + 17)], 6)
    p.ell(x - w / 2, y - 26, x + w / 2, y + 8, GOLD)


def ic_koin(p):
    for i in range(4):
        _coin(p, 100, 150 - i * 26)
    p.ell(72, 63, 128, 81, GOLD_SH, ow=3)


def ic_celengan(p):
    p.ell(16, 104, 50, 120, PINK)  # ekor
    p.rr(52, 140, 82, 186, 12, PINK); p.rr(118, 140, 148, 186, 12, PINK)
    p.ell(22, 52, 172, 168, PINK)
    p.poly([(56, 70), (66, 30), (96, 58)], PINK)
    p.ell(146, 88, 192, 132, (240, 128, 160)); p.ell(158, 102, 166, 116, OUT, ow=0); p.ell(173, 102, 181, 116, OUT, ow=0)
    p.ell(118, 80, 132, 96, EYE, ow=0)
    p.rr(76, 58, 120, 68, 5, OUT, ow=0)
    p.soft(40, 70, 90, 110, (255, 200, 215), 160)


def ic_tanaman(p):
    p.stroke([(100, 120), (100, 70)], 8, (60, 140, 70))
    p.poly(bez((100, 80), (60, 30), (20, 50), (18, 60), 12) + bez((18, 60), (40, 100), (80, 100), (100, 80), 12), GREEN_L)
    p.poly(bez((100, 70), (130, 10), (180, 20), (184, 30), 12) + bez((184, 30), (170, 80), (130, 90), (100, 70), 12), GREEN)
    p.poly([(52, 132), (148, 132), (136, 192), (64, 192)], (196, 110, 70))
    p.rr(44, 118, 156, 140, 8, (214, 128, 84))


def ic_troli(p):
    for x0, c in ((66, (250, 200, 40)), (96, (60, 130, 220)), (124, (240, 90, 80))):
        p.rr(x0, 34 + (x0 % 3) * 6, x0 + 30, 92, 4, c, ow=4)
    p.stroke([(10, 40), (36, 40), (58, 140), (162, 140)], 8, (40, 90, 190))
    p.poly([(40, 88), (178, 88), (162, 132), (54, 132)], (110, 170, 240))
    for x in (80, 110, 140):
        p.stroke([(x, 90), (x - 4, 130)], 4, (40, 90, 190))
    p.ell(56, 152, 82, 178, OUT, ow=0); p.ell(138, 152, 164, 178, OUT, ow=0)


def ic_kardus_turun(p):
    p.poly([(30, 70), (100, 50), (170, 70), (100, 92)], (222, 170, 110))
    p.poly([(30, 70), (100, 92), (100, 182), (30, 156)], (196, 140, 86))
    p.poly([(100, 92), (170, 70), (170, 156), (100, 182)], (176, 120, 70))
    p.poly([(56, 62), (126, 84), (126, 100), (56, 78)], (236, 210, 160), ow=3)
    _arrow(p, 150, 40, 168, 180, 26, RED)


def ic_uang_naik(p):
    for i, dy in enumerate((0, -16, -32)):
        p.poly([(18, 130 + dy), (120, 100 + dy), (150, 156 + dy), (48, 186 + dy)], (120, 196, 120) if i % 2 else (90, 176, 100))
        p.ell(70, 128 + dy, 100, 150 + dy, (200, 236, 200), ow=3)
    _arrow(p, 158, 170, 164, 20, 28, RED)


def ic_roti(p):
    p.poly(bez((20, 140), (10, 60), (190, 50), (182, 136), 20), (226, 160, 80))
    p.ell(20, 108, 182, 160, (214, 140, 66))
    for x in (66, 100, 134):
        p.stroke([(x - 10, 92), (x + 10, 76)], 6, (170, 100, 40))


def ic_bbm(p):
    p.rr(40, 30, 126, 180, 14, (226, 52, 52))
    p.rr(56, 48, 110, 96, 8, (255, 230, 230), ow=4)
    p.rr(28, 172, 138, 190, 6, (120, 30, 30))
    p.stroke([(126, 80), (160, 90), (160, 150), (176, 150)], 8)
    p.rr(150, 60, 176, 96, 6, (60, 60, 70))
    p.ell(70, 112, 96, 138, (255, 200, 60), ow=4)


def ic_susu(p):
    p.poly([(52, 70), (100, 30), (148, 70)], (230, 238, 250))
    p.rr(52, 70, 148, 186, 8, WHITE)
    p.rr(52, 100, 148, 150, 0, (90, 150, 230), ow=0)
    p.d.rectangle(p.B(52, 100, 148, 150), outline=OUT, width=p.W(4))
    p.rr(84, 18, 116, 38, 4, (90, 150, 230))
    p.ell(84, 112, 116, 140, WHITE, ow=3)


def ic_grafik(p):
    for i, (x, h, c) in enumerate(((30, 50, (250, 150, 80)), (78, 90, (244, 110, 70)), (126, 140, RED))):
        p.rr(x, 180 - h, x + 40, 184, 6, c)
    _arrow(p, 30, 110, 176, 22, 18, RED)


def ic_centang(p):
    p.ell(20, 20, 180, 180, GREEN, ow=8)
    p.stroke([(58, 102), (88, 132), (144, 70)], 22, WHITE)


def ic_dompet(p):
    p.poly([(60, 40), (170, 30), (180, 90), (70, 100)], (120, 196, 120))
    p.rr(20, 64, 180, 180, 22, (150, 92, 50))
    p.rr(20, 64, 180, 108, 18, (176, 112, 62))
    p.rr(120, 110, 186, 150, 12, (120, 72, 38))
    p.ell(140, 120, 160, 140, GOLD, ow=3)


def ic_rumah(p):
    p.rr(40, 90, 160, 182, 6, (250, 236, 210))
    p.poly([(20, 98), (100, 24), (180, 98)], (226, 80, 70))
    p.rr(84, 120, 116, 182, 4, (150, 92, 50))
    p.rr(124, 108, 148, 132, 3, (150, 200, 240), ow=4)


def ic_lampu(p):
    for a in range(0, 360, 45):
        r = math.radians(a)
        if 30 < a < 150:
            continue
        p.stroke([(100 + 76 * math.cos(r), 84 - 76 * math.sin(r)), (100 + 92 * math.cos(r), 84 - 92 * math.sin(r))], 7, YELLOW)
    p.ell(46, 30, 154, 138, (255, 222, 90))
    p.rr(72, 126, 128, 168, 8, (170, 176, 190))
    p.stroke([(76, 142), (124, 142)], 4); p.rr(82, 166, 118, 182, 6, (120, 126, 140))


def ic_jam(p):
    p.ell(24, 24, 176, 176, WHITE, ow=10, oc=(80, 140, 230))
    p.stroke([(100, 100), (100, 52)], 8); p.stroke([(100, 100), (134, 118)], 8)
    p.ell(92, 92, 108, 108, OUT, ow=0)


def ic_buku(p):
    p.rr(30, 30, 170, 176, 10, (60, 120, 220))
    p.rr(46, 30, 170, 160, 8, (90, 150, 240))
    p.rr(74, 60, 146, 84, 4, WHITE, ow=3)
    p.stroke([(46, 160), (170, 160)], 4)


def ic_tameng(p):
    p.poly(bez((100, 18), (130, 34), (160, 36), (170, 40), 8) + bez((170, 40), (176, 120), (130, 168), (100, 186), 12)
           + bez((100, 186), (70, 168), (24, 120), (30, 40), 12) + bez((30, 40), (40, 36), (70, 34), (100, 18), 8), (80, 140, 230))
    p.stroke([(68, 100), (92, 124), (136, 76)], 16, WHITE)


def ic_bintang(p):
    pts = []
    for i in range(10):
        r = 86 if i % 2 == 0 else 38; a = math.radians(-90 + i * 36)
        pts.append((100 + r * math.cos(a), 104 + r * math.sin(a)))
    p.poly(pts, YELLOW)


def ic_hp(p):
    p.rr(50, 14, 150, 186, 18, (50, 56, 76))
    p.rr(60, 34, 140, 160, 6, (190, 222, 255), ow=0)
    p.rr(70, 50, 130, 70, 4, WHITE, ow=0); p.rr(70, 80, 116, 96, 4, (120, 196, 120), ow=0)
    p.rr(84, 168, 116, 176, 4, (120, 126, 140), ow=0)


def ic_keranjang(p):
    p.arc(46, 20, 154, 120, 180, 360, 10)
    p.poly([(16, 76), (184, 76), (164, 180), (36, 180)], (226, 160, 80))
    for x in (60, 100, 140):
        p.stroke([(x, 84), (x - 4 if x < 100 else x + 4 if x > 100 else x, 172)], 5, (170, 100, 40))
    p.ell(50, 44, 96, 90, (240, 80, 70)); p.ell(100, 40, 146, 86, (250, 200, 40))


def ic_seru(p):
    p.ell(20, 20, 180, 180, (250, 200, 40), ow=8)
    p.rr(88, 44, 112, 122, 12, OUT, ow=0); p.ell(86, 134, 114, 162, OUT, ow=0)


def ic_tanya(p):
    p.ell(20, 20, 180, 180, (110, 160, 240), ow=8)
    f = font(int(120 * p.k), "black")
    p.d.text(p.P(100, 104), "?", font=f, fill=WHITE, anchor="mm")


def ic_silang(p):
    p.ell(20, 20, 180, 180, RED, ow=8)
    p.stroke([(66, 66), (134, 134)], 20, WHITE); p.stroke([(134, 66), (66, 134)], 20, WHITE)


def ic_orang(p):
    for x, c in ((60, (110, 160, 240)), (140, (240, 130, 160)), (100, (120, 196, 120))):
        y = 30 if x == 100 else 50
        p.ell(x - 26, y, x + 26, y + 52, SKIN)
        p.rr(x - 40, y + 58, x + 40, y + 140, 30, c)


def ic_hati(p):
    p.poly(bez((100, 182), (40, 140), (6, 100), (20, 62), 12) + bez((20, 62), (34, 20), (88, 22), (100, 60), 10)
           + bez((100, 60), (112, 22), (166, 20), (180, 62), 10) + bez((180, 62), (194, 100), (160, 140), (100, 182), 12), (240, 90, 110))
    p.soft(46, 50, 90, 90, (255, 200, 210), 170)


def ic_kalender(p):
    p.rr(24, 34, 176, 180, 14, WHITE)
    p.rr(24, 34, 176, 76, 12, RED)
    for x in (60, 140):
        p.rr(x - 6, 18, x + 6, 50, 6, (120, 126, 140))
    for i in range(3):
        for j in range(3):
            p.rr(44 + j * 40, 92 + i * 28, 72 + j * 40, 112 + i * 28, 3, (200, 210, 230), ow=0)


def ic_toko(p):
    p.rr(30, 84, 170, 182, 4, (250, 240, 226))
    for i in range(5):
        c = RED if i % 2 == 0 else WHITE
        p.poly([(20 + i * 32, 40), (52 + i * 32, 40), (52 + i * 32, 84), (20 + i * 32, 84)], c, ow=4)
    p.rr(70, 116, 110, 182, 3, (110, 160, 240))
    p.rr(122, 108, 154, 140, 3, (190, 222, 255), ow=4)


def ic_target(p):
    for r, c in ((84, RED), (60, WHITE), (36, RED), (14, WHITE)):
        p.ell(100 - r, 100 - r, 100 + r, 100 + r, c, ow=5)
    _arrow(p, 182, 22, 104, 98, 12, (60, 60, 70))


IKON = {
    "koin": ic_koin, "celengan": ic_celengan, "tanaman": ic_tanaman, "troli": ic_troli,
    "kardus_turun": ic_kardus_turun, "uang_naik": ic_uang_naik, "roti": ic_roti, "bbm": ic_bbm,
    "susu": ic_susu, "grafik": ic_grafik, "centang": ic_centang, "dompet": ic_dompet, "rumah": ic_rumah,
    "lampu": ic_lampu, "jam": ic_jam, "buku": ic_buku, "tameng": ic_tameng, "bintang": ic_bintang,
    "hp": ic_hp, "keranjang": ic_keranjang, "seru": ic_seru, "tanya": ic_tanya, "silang": ic_silang,
    "orang": ic_orang, "hati": ic_hati, "kalender": ic_kalender, "toko": ic_toko, "target": ic_target,
}


@functools.lru_cache(maxsize=256)
def ikon(name, size):
    """Ikon RGBA kotak size x size. Nama tak dikenal -> 'bintang'."""
    fn = IKON.get(name, ic_bintang)
    k = size / 200 * SS
    img = Image.new("RGBA", (int(200 * k), int(200 * k)), (0, 0, 0, 0))
    fn(Pen(img, k, ow=6))
    return _finish(img, size, size)


@functools.lru_cache(maxsize=64)
def lingkaran_ikon(name, size, bg=(253, 226, 140)):
    """Ikon di dalam lingkaran pastel (seperti panel 'Penyebab Inflasi')."""
    k = SS
    img = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([0, 0, size * k - 1, size * k - 1], fill=bg + (255,))
    im = img.resize((size, size), Image.LANCZOS)
    ic = ikon(name, int(size * 0.72))
    im.alpha_composite(ic, ((size - ic.width) // 2, (size - ic.height) // 2))
    return im


# ================================================================ TEKS
def _tokens(text):
    """'**x**' = aksen. Baris baru '\n' dipertahankan. Token: (kata, aksen, nempel_ke_kata_sebelumnya)."""
    out = []
    parts = text.split("**")
    prev_end_space = True
    for i, part in enumerate(parts):
        acc = i % 2 == 1
        first = True
        for j, line in enumerate(part.split("\n")):
            if j > 0:
                out.append(("\n", acc, False)); first = False
            for k, w in enumerate(line.split(" ")):
                if w:
                    glue = first and k == 0 and j == 0 and not prev_end_space and bool(out) and out[-1][0] != "\n"
                    out.append((w, acc, glue)); first = False
                elif k == 0 and j == 0:
                    first = False
        if part:
            prev_end_space = part[-1] in " \n"
    return out


def teks(text, size, max_w, color=TEXT, accent=RED, weight="black", align="left", spacing=1.18, stroke=0, stroke_col=WHITE):
    f = font(size, weight)
    sp = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for w, acc, glue in _tokens(text):
        if w == "\n":
            lines.append(cur); cur, cw = [], 0; continue
        wl = f.getlength(w)
        if glue and cur:
            cur.append((w, acc, wl, True)); cw += wl; continue
        if cur and cw + sp + wl > max_w:
            lines.append(cur); cur, cw = [], 0
        cur.append((w, acc, wl, False)); cw += (sp if cw else 0) + wl
    lines.append(cur)
    lh = int(size * spacing)
    widths = [sum(x[2] for x in L) + sp * max(0, sum(1 for x in L[1:] if not x[3])) for L in lines]
    W = int(max(widths + [1])) + 4 + stroke * 2
    H = lh * len(lines) + int(size * 0.3) + stroke * 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, L in enumerate(lines):
        x = 2 + stroke + {"left": 0, "center": (W - 4 - stroke * 2 - widths[i]) / 2, "right": W - 4 - stroke * 2 - widths[i]}[align]
        y = stroke + i * lh
        for n_, (w, acc, wl, glue) in enumerate(L):
            if n_ > 0 and not glue:
                x += sp
            d.text((x, y), w, font=f, fill=accent if acc else color, stroke_width=stroke, stroke_fill=stroke_col)
            x += wl
    return img


# ================================================================ UI
def bayangan(img, blur=14, off=(0, 8), alpha=60):
    pad = blur * 3
    W, H = img.width + pad * 2, img.height + pad * 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: v * alpha // 255)
    blk = Image.new("RGBA", img.size, (30, 40, 80, 0)); blk.putalpha(a)
    sh.alpha_composite(blk, (pad + off[0], pad + off[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.alpha_composite(img, (pad, pad))
    return sh


def kartu(w, h, r=36, fill=CARD, border=None, shadow=True, alpha=255):
    k = 2
    img = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=r * k, fill=fill + (alpha,),
                                          outline=border, width=4 * k if border else 0)
    img = img.resize((w, h), Image.LANCZOS)
    return bayangan(img) if shadow else img


def pil_judul(text, size, fill=NAVY, color=WHITE, pad=(0.9, 0.42), ekor=False, max_w=2000):
    t = teks(text, size, max_w, color=color, accent=YELLOW, weight="black", align="center")
    pw, ph = int(size * pad[0]), int(size * pad[1])
    w, h = t.width + pw * 2, t.height + ph * 2 - int(size * 0.2)
    k = 2
    img = Image.new("RGBA", ((w) * k, (h + (24 if ekor else 0)) * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=h * k // 2, fill=fill + (255,))
    if ekor:
        d.polygon([(w * k * 0.16, h * k - 4), (w * k * 0.16 + 40 * k, h * k - 4), (w * k * 0.13, (h + 22) * k)], fill=fill + (255,))
    img = img.resize((w, h + (24 if ekor else 0)), Image.LANCZOS)
    img.alpha_composite(t, (pw, ph - int(size * 0.1)))
    return bayangan(img, blur=8, off=(0, 5), alpha=50)


def balon(content, fill=WHITE, ekor="kiri-bawah", pad=40, ow=5, r=None):
    """Balon kata membungkus gambar content. ekor: kiri-bawah|kanan-bawah|kiri|kanan|bawah|tidak."""
    cw, chh = content.width, content.height
    w, h = cw + pad * 2, chh + pad * 2
    r = r if r is not None else min(h // 2, 90)
    T = 70
    W, H = w + T * 2 + ow * 4, h + T * 2 + ow * 4
    k = 2
    img = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0 = T + ow * 2, T + ow * 2
    box = [x0, y0, x0 + w, y0 + h]
    tails = {
        "kiri-bawah": [(x0 + w * 0.18, y0 + h - 10), (x0 + w * 0.32, y0 + h - 10), (x0 + w * 0.08, y0 + h + 56)],
        "kanan-bawah": [(x0 + w * 0.68, y0 + h - 10), (x0 + w * 0.82, y0 + h - 10), (x0 + w * 0.92, y0 + h + 56)],
        "bawah": [(x0 + w * 0.44, y0 + h - 10), (x0 + w * 0.56, y0 + h - 10), (x0 + w * 0.5, y0 + h + 56)],
        "kiri": [(x0 + 10, y0 + h * 0.55), (x0 + 10, y0 + h * 0.8), (x0 - 56, y0 + h * 0.86)],
        "kanan": [(x0 + w - 10, y0 + h * 0.55), (x0 + w - 10, y0 + h * 0.8), (x0 + w + 56, y0 + h * 0.86)],
    }
    tail = tails.get(ekor)
    S = lambda pts: [(x * k, y * k) for x, y in pts]
    d.rounded_rectangle([(box[0] - ow) * k, (box[1] - ow) * k, (box[2] + ow) * k, (box[3] + ow) * k], radius=(r + ow) * k, fill=OUT + (255,))
    if tail:
        d.line(S(tail + [tail[0]]), fill=OUT + (255,), width=ow * 2 * k, joint="curve")
        d.polygon(S(tail), fill=OUT + (255,))
    d.rounded_rectangle([box[0] * k, box[1] * k, box[2] * k, box[3] * k], radius=r * k, fill=fill + (255,))
    if tail:
        d.polygon(S(tail), fill=fill + (255,))
    img = img.resize((W, H), Image.LANCZOS)
    img.alpha_composite(content, (x0 + pad, y0 + pad - 4))
    # potong ruang kosong
    bb = img.getbbox()
    return bayangan(img.crop(bb), blur=8, off=(0, 6), alpha=40)


def percikan(size, col=YELLOW, n=3):
    """Garis aksen 'kaget/semangat' (3 garis pendek seperti di referensi)."""
    k = SS
    img = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
    p = Pen(img, size * k / 100, ow=0)
    angs = [-50, -15, 20][:n]
    for a in angs:
        r = math.radians(a)
        x0, y0 = 20 + 30 * math.cos(r), 50 + 30 * math.sin(r)
        x1, y1 = 20 + 72 * math.cos(r), 50 + 72 * math.sin(r)
        p.stroke([(x0, y0), (x1, y1)], 11, col)
    return img.resize((size, size), Image.LANCZOS)


# ================================================================ LATAR
def _grad(W, H, top, bot):
    g = Image.new("RGB", (1, 256))
    for i in range(256):
        t = i / 255
        g.putpixel((0, i), tuple(int(lerp(a, b, t)) for a, b in zip(top, bot)))
    return g.resize((W, H), Image.BILINEAR)


def _awan(p, x, y, s):
    for dx, dy, r in ((0, 0, 40), (44, -20, 50), (92, 0, 40), (46, 12, 40)):
        p.ell(x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s, WHITE, ow=0)


@functools.lru_cache(maxsize=32)
def latar(name, W, H):
    """Latar RGB. name: kamar | kafe | bukit | <warna di LATAR> (default 'biru')."""
    land = W >= H
    if name in ("kamar", "kafe"):
        top, bot = ((226, 237, 250), (208, 224, 246)) if name == "kamar" else ((246, 238, 228), (236, 224, 210))
        img = _grad(W, H, top, bot).convert("RGBA")
        k = 2; s = (H / 1080) if land else (W / 1080)
        lay = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0)); p = Pen(lay, k, ow=5 * s)
        # jendela
        wx, wy, ww, wh = 0.03 * W, 0.08 * H, 0.2 * W if land else 0.32 * W, 0.46 * H if land else 0.26 * H
        p.rr(wx, wy, wx + ww, wy + wh, 14 * s, (250, 252, 255))
        p.rr(wx + 16 * s, wy + 16 * s, wx + ww - 16 * s, wy + wh - 16 * s, 8 * s, (176, 214, 246), ow=0)
        _awan(p, wx + ww * 0.25, wy + wh * 0.32, 0.5 * s)
        if name == "kafe":
            p.ell(wx + ww * 0.1, wy + wh * 0.55, wx + ww * 0.6, wy + wh * 1.2, (150, 200, 140), ow=0)
        p.rr(wx + ww / 2 - 6 * s, wy, wx + ww / 2 + 6 * s, wy + wh, 0, (250, 252, 255), ow=0)
        p.rr(wx, wy + wh * 0.55 - 6 * s, wx + ww, wy + wh * 0.55 + 6 * s, 0, (250, 252, 255), ow=0)
        p.d.rounded_rectangle(p.B(wx, wy, wx + ww, wy + wh), radius=14 * s * k, outline=(150, 170, 200), width=p.W(5 * s))
        # rak buku kanan
        bx0, bw = (0.86 * W, 0.12 * W) if land else (0.66 * W, 0.3 * W)
        for j, yy in enumerate((0.2 * H, 0.42 * H, 0.64 * H) if land else (0.12 * H, 0.22 * H)):
            p.rr(bx0, yy, bx0 + bw, yy + 14 * s, 4 * s, (200, 160, 120), ow=0)
            x = bx0 + 10 * s
            cols = [(90, 140, 210), (230, 110, 100), (250, 200, 80), (110, 180, 130), (150, 120, 200), (70, 110, 180)]
            for i in range(6):
                bwid = (20 + (i * 7 + j * 5) % 14) * s; bh = (70 + (i * 13 + j * 7) % 30) * s
                if x + bwid > bx0 + bw - 8 * s:
                    break
                p.rr(x, yy - bh, x + bwid, yy, 3 * s, cols[(i + j) % 6], ow=0)
                x += bwid + 4 * s
        # pot tanaman kecil
        px, py = (0.92 * W, 0.86 * H) if land else (0.84 * W, 0.3 * H)
        lay.alpha_composite(ikon("tanaman", int(130 * s * k)), (int(px * k - 65 * s * k), int(py * k - 260 * s * k)))
        if name == "kafe":
            p.rr(-20, 0.86 * H, W + 20, H + 40, 10 * s, (206, 150, 96), ow=0)
            p.rr(-20, 0.86 * H, W + 20, 0.86 * H + 14 * s, 0, (226, 172, 116), ow=0)
        img.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        return img.convert("RGB")
    if name == "bukit":
        img = _grad(W, H, (214, 234, 252), (240, 248, 255)).convert("RGBA")
        k = 2; s = min(W, H) / 1080
        lay = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0)); p = Pen(lay, k, ow=0)
        _awan(p, 0.1 * W, 0.18 * H, 1.0 * s); _awan(p, 0.72 * W, 0.12 * H, 0.8 * s)
        p.ell(-0.3 * W, 0.72 * H, 1.3 * W, 1.6 * H, (150, 206, 120))
        p.ell(0.3 * W, 0.78 * H, 1.6 * W, 1.7 * H, (126, 192, 100))
        img.alpha_composite(lay.resize((W, H), Image.LANCZOS))
        return img.convert("RGB")
    top, bot = LATAR.get(name, LATAR["biru"])
    img = _grad(W, H, top, bot).convert("RGBA")
    k = 2; s = min(W, H) / 1080
    lay = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0)); p = Pen(lay, k, ow=0)
    light = tuple(min(255, c + 14) for c in top)
    p.ell(-0.12 * W, -0.2 * H, 0.22 * W, 0.3 * H, light)
    p.ell(0.8 * W, 0.7 * H, 1.15 * W, 1.25 * H, light)
    for i, (x, y) in enumerate(((0.3, 0.1), (0.62, 0.92), (0.95, 0.2), (0.05, 0.8))):
        r = (10 + 6 * i) * s
        p.ell(x * W - r, y * H - r, x * W + r, y * H + r, tuple(max(0, c - 14) for c in bot))
    img.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return img.convert("RGB")
