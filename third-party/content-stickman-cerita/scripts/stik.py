# -*- coding: utf-8 -*-
"""
stik.py - inti mesin gambar "Stikman Cerita".

Isi:
  * palet warna, easing, font
  * Cam   : pose kamera virtual (x, y, z zoom, r roll) + parallax per lapisan
  * Canvas: kanvas supersampling; semua primitif menerima KOORDINAT DUNIA lalu
            diproyeksikan lewat kamera (garis, polygon, elips, teks, kurva).

Konvensi dunia (satuan = piksel 1080p pada zoom 1):
  * y = 0  -> garis lantai (kaki tokoh); ke atas = y negatif
  * x = 0  -> tengah panggung; kanan = positif
  * kamera default: x=0, y=-300, z=1  -> tokoh setinggi ±470 satuan muat penuh
"""
import math, os, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "assets", "fonts"))

# ------------------------------------------------------------------ palet
OUT = (24, 24, 34)            # warna garis tepi (hampir hitam)
PUTIH = (255, 255, 255)
KRIM = (255, 243, 226)
HITAM = (28, 28, 36)
MERAH = (226, 56, 56)
MERAH_TUA = (168, 36, 52)
LIDAH = (244, 120, 124)
PIPI = (255, 150, 165)
BIRU = (44, 104, 214)
BIRU_TUA = (30, 60, 150)
BIRU_MUDA = (170, 214, 250)
PINK = (244, 140, 172)
PINK_TUA = (214, 100, 140)
PINK_MUDA = (250, 190, 210)
KUNING = (255, 205, 60)
KUNING_MUDA = (255, 236, 150)
ORANYE = (250, 150, 60)
HIJAU = (96, 190, 108)
HIJAU_TUA = (56, 140, 80)
HIJAU_MUDA = (170, 224, 150)
COKLAT = (168, 112, 70)
COKLAT_TUA = (120, 78, 48)
KAYU = (226, 178, 130)
KAYU_TUA = (190, 140, 96)
UNGU = (140, 120, 220)
UNGU_TUA = (86, 70, 150)
NAVY = (36, 48, 104)
ABU = (200, 206, 218)
ABU_TUA = (120, 128, 148)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gelap(c, t=0.2):
    return mix(c, (0, 0, 0), t)


def terang(c, t=0.3):
    return mix(c, (255, 255, 255), t)


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, a, b):
    """0..1 linear antara waktu a dan b."""
    return clamp((t - a) / max(1e-6, b - a))


def e_io(p):          # ease in-out (halus, untuk gerak kamera)
    p = clamp(p)
    return p * p * p * (p * (p * 6 - 15) + 10)


def e_out(p):         # ease out cepat-lambat
    p = clamp(p)
    return 1 - (1 - p) ** 3


def e_in(p):
    p = clamp(p)
    return p ** 3


def e_back(p, s=1.70158):   # overshoot (muncul memantul)
    p = clamp(p)
    return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2


def e_spring(p):       # pegas teredam: lewat target lalu mantap
    p = clamp(p)
    if p >= 1:
        return 1.0
    return 1 - math.exp(-6.5 * p) * math.cos(10.5 * p)


def e_lin(p):
    return clamp(p)


def e_snap(p):          # sangat cepat di awal (untuk punch)
    p = clamp(p)
    return 1 - (1 - p) ** 5


EASE = {"io": e_io, "out": e_out, "in": e_in, "back": e_back, "spring": e_spring,
        "lin": e_lin, "snap": e_snap}


def lerp(a, b, t):
    return a + (b - a) * t


# ------------------------------------------------------------------ font
@functools.lru_cache(maxsize=256)
def font(name, size):
    """name: 'judul' (Fredoka), 'teks' (Nunito), 'bulat' (Baloo 2), 'seru' (Bungee)."""
    files = {"judul": ("Fredoka-Var.ttf", 700), "teks": ("Nunito-Var.ttf", 900),
             "bulat": ("Baloo2-Var.ttf", 800), "seru": ("Bungee-Regular.ttf", None)}
    fn, wt = files.get(name, files["judul"])
    path = os.path.join(FONT_DIR, fn)
    if not os.path.exists(path):
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        wt = None
    f = ImageFont.truetype(path, max(4, int(size)))
    if wt:
        try:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                nm = a["name"]
                nm = nm.decode() if isinstance(nm, bytes) else nm
                vals.append(min(a["maximum"], max(a["minimum"], wt)) if nm == "Weight" else a["default"])
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f


# ------------------------------------------------------------------ kamera
CX0, CY0 = 0.0, -300.0       # pusat kamera default


class Cam:
    """Pose kamera. x,y = titik dunia di tengah layar; z = zoom; r = roll (derajat)."""
    __slots__ = ("x", "y", "z", "r", "blur", "shk_x", "shk_y")

    def __init__(self, x=CX0, y=CY0, z=1.0, r=0.0, blur=0.0):
        self.x, self.y, self.z, self.r, self.blur = x, y, z, r, blur
        self.shk_x = self.shk_y = 0.0

    def copy(self):
        c = Cam(self.x, self.y, self.z, self.r, self.blur)
        c.shk_x, c.shk_y = self.shk_x, self.shk_y
        return c


# ------------------------------------------------------------------ kurva
def catmull(pts, closed=False, n=8):
    """Titik-titik kontrol -> kurva halus (Catmull-Rom) sebagai daftar titik."""
    P = list(pts)
    m = len(P)
    if m < 3:
        return P
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if (closed or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else P[(i + 1) % m]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(P[-1])
    return out


def arc_pts(cx, cy, rx, ry, a0, a1, n=18):
    """Titik busur elips (derajat; 0 = kanan, 90 = bawah)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def bezier(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


# ------------------------------------------------------------------ kanvas
class Canvas:
    """Kanvas supersampling. Semua koordinat = dunia; kedalaman lapisan lewat self.depth."""

    def __init__(self, W, H, ss, cam, u):
        self.W, self.H, self.ss, self.u = W, H, ss, u
        self.cam = cam
        self.depth = 1.0
        self.im = Image.new("RGB", (W * ss, H * ss), PUTIH)
        self.d = ImageDraw.Draw(self.im, "RGBA")
        self._refresh()

    # --- proyeksi
    def _refresh(self):
        c, d = self.cam, self.depth
        self.k = self.u * self.ss * (1 + (c.z - 1) * d)
        self.ox = self.W * self.ss / 2 - (CX0 + (c.x + c.shk_x - CX0) * d) * self.k
        self.oy = self.H * self.ss / 2 - (CY0 + (c.y + c.shk_y - CY0) * d) * self.k

    def set_depth(self, d):
        self.depth = d
        self._refresh()

    def P(self, x, y):
        return (self.ox + x * self.k, self.oy + y * self.k)

    def L(self, v):
        return v * self.k

    def visible(self, pad=0):
        """Rentang dunia yang terlihat di lapisan ini: (x0, x1, y0, y1)."""
        w, h = self.W * self.ss / 2 / self.k, self.H * self.ss / 2 / self.k
        cx = (self.W * self.ss / 2 - self.ox) / self.k
        cy = (self.H * self.ss / 2 - self.oy) / self.k
        return (cx - w - pad, cx + w + pad, cy - h - pad, cy + h + pad)

    # --- latar layar
    def fill(self, color):
        self.d.rectangle([0, 0, self.im.width, self.im.height], fill=color)

    def gradient(self, top, bottom, y0=0.0, y1=1.0):
        """Gradien vertikal di ruang layar (y0..y1 pecahan tinggi)."""
        w, h = self.im.size
        strip = Image.new("RGB", (1, 64))
        px = strip.load()
        for i in range(64):
            px[0, i] = mix(top, bottom, i / 63)
        a, b = int(h * y0), int(h * y1)
        self.im.paste(strip.resize((w, max(1, b - a)), Image.BILINEAR), (0, a))

    # --- primitif
    def _w(self, ow):
        return max(1, int(round(ow * self.k)))

    def _stroke(self, q, ow, color, closed=False, cap=True):
        """Garis tebal mulus: ruas lurus + bulatan di tiap titik (tanpa sambungan bergerigi)."""
        if not ow or len(q) < 2:
            return
        w = max(1.0, ow * self.k)
        seq = list(q) + [q[0]] if closed else list(q)
        iw = max(1, int(round(w)))
        r = iw / 2.0
        d = self.d
        last = None
        for i, (x, y) in enumerate(seq):
            if i:
                d.line([seq[i - 1], (x, y)], fill=color, width=iw)
            # bulatan di titik: lewati titik yang terlalu dekat dengan bulatan sebelumnya
            if last is None or (x - last[0]) ** 2 + (y - last[1]) ** 2 > (r * 0.45) ** 2 or i == len(seq) - 1:
                if cap or 0 < i < len(seq) - 1:
                    d.ellipse([x - r, y - r, x + r, y + r], fill=color)
                last = (x, y)

    def poly(self, pts, fill=None, ow=0, oc=OUT):
        q = [self.P(*p) for p in pts]
        if fill is not None:
            self.d.polygon(q, fill=fill)
        if ow:
            self._stroke(q, ow, oc, closed=True)

    def blob(self, pts, fill=None, ow=0, oc=OUT, n=8):
        """Bentuk lembut dari titik kontrol (kurva tertutup)."""
        self.poly(catmull(pts, True, n), fill, ow, oc)

    def line(self, pts, color=OUT, w=4, cap=True):
        self._stroke([self.P(*p) for p in pts], w, color, False, cap)

    def curve(self, pts, color=OUT, w=4, n=8, cap=True):
        self.line(catmull(pts, False, n), color, w, cap)

    def ell(self, cx, cy, rx, ry=None, fill=None, ow=0, oc=OUT):
        ry = rx if ry is None else ry
        x, y = self.P(cx, cy)
        a, b = rx * self.k, ry * self.k
        if ow:
            h = ow * self.k / 2
            self.d.ellipse([x - a - h, y - b - h, x + a + h, y + b + h], fill=oc)
            a, b = max(0.5, a - h), max(0.5, b - h)
            if fill is not None:
                self.d.ellipse([x - a, y - b, x + a, y + b], fill=fill)
        elif fill is not None:
            self.d.ellipse([x - a, y - b, x + a, y + b], fill=fill)

    def rect(self, x0, y0, x1, y1, fill=None, ow=0, oc=OUT, r=0):
        X0, Y0 = self.P(x0, y0)
        X1, Y1 = self.P(x1, y1)
        R = r * self.k
        if ow:
            h = ow * self.k / 2
            self.d.rounded_rectangle([X0 - h, Y0 - h, X1 + h, Y1 + h], radius=R + h, fill=oc)
            X0, Y0, X1, Y1, R = X0 + h, Y0 + h, X1 - h, Y1 - h, max(0, R - h)
        if fill is not None and X1 > X0 and Y1 > Y0:
            if R > 0.5:
                self.d.rounded_rectangle([X0, Y0, X1, Y1], radius=R, fill=fill)
            else:
                self.d.rectangle([X0, Y0, X1, Y1], fill=fill)

    def tube(self, p0, p1, w, fill, ow=3, oc=OUT):
        """Segmen tebal berujung bulat dengan garis tepi (lengan baju, kaki celana)."""
        a, b = self.P(*p0), self.P(*p1)
        W = w * self.k
        h = ow * self.k
        for color, ww in ((oc, W + 2 * h), (fill, W)):
            self.d.line([a, b], fill=color, width=int(round(ww)))
            r = ww / 2
            for (x, y) in (a, b):
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=color)

    def text(self, x, y, s, size, fill=OUT, name="judul", anchor="mm", stroke=0, stroke_fill=OUT, spacing=4):
        f = font(name, size * self.k)
        X, Y = self.P(x, y)
        kw = {}
        if stroke:
            kw = {"stroke_width": max(1, int(stroke * self.k)), "stroke_fill": stroke_fill}
        if "\n" in s:
            self.d.multiline_text((X, Y), s, font=f, fill=fill, anchor=anchor, align="center", spacing=spacing * self.k, **kw)
        else:
            self.d.text((X, Y), s, font=f, fill=fill, anchor=anchor, **kw)

    def text_size(self, s, size, name="judul"):
        f = font(name, size * self.k)
        b = f.getbbox(s)
        return (b[2] - b[0]) / self.k, (b[3] - b[1]) / self.k

    # --- keluaran
    def finish(self):
        """Roll kamera (jika ada) lalu perkecil ke ukuran akhir."""
        im = self.im
        r = self.cam.r
        if abs(r) > 0.02:
            im = im.rotate(r, resample=Image.BICUBIC, center=(im.width / 2, im.height / 2), fillcolor=(40, 40, 52))
            # perbesar sedikit agar sudut tidak kosong
            s = 1 + abs(math.radians(r)) * 1.1
            w, h = im.size
            cw, ch = int(w / s), int(h / s)
            im = im.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2)).resize((w, h), Image.BILINEAR)
        if self.ss > 1:
            im = im.reduce(self.ss)
        return im


def blur_image(im, radius):
    return im.filter(ImageFilter.GaussianBlur(radius)) if radius > 0.4 else im
