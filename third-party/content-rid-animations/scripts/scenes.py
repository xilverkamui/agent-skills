# -*- coding: utf-8 -*-
"""
scenes.py - template adegan "rid animations".

Setiap adegan = latar + karakter (ber-lipsync) + elemen (kartu, pil judul, ikon, balon)
yang muncul dengan animasi. Tipe adegan (field "tipe"):
  dialog, tanya, definisi, contoh, ikon_grid, daftar, checklist, sorak, angka, banding, penutup, judul
Lihat references/format-adegan.md untuk semua field.
"""
import math, random
from PIL import Image, ImageDraw
import rid2d as R

TR = 0.3  # durasi crossfade antar adegan (detik)


class El:
    def __init__(self, img, cx, cy, t0=0.0, anim="pop", dur=0.45, loop=None, sfx="pop", z=0):
        self.img, self.cx, self.cy, self.t0, self.anim, self.dur, self.loop, self.sfx, self.z = img, cx, cy, t0, anim, dur, loop, sfx, z


class Tokoh:
    def __init__(self, kind, h, cx, bottom, expr="senang", pose="diam", flip=False, t0=0.0, enter=True):
        self.kind, self.h, self.cx, self.bottom = kind, int(h), cx, bottom
        self.expr, self.pose, self.flip, self.t0, self.enter = expr, pose, flip, t0, enter
        self.seed = 0.0 if kind == "pria" else 1.3


def _paste(base, img, x, y, alpha=1.0):
    if alpha <= 0.003:
        return
    if alpha < 0.999:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    base.paste(img, (int(round(x)), int(round(y))), img)


class Scene:
    def __init__(self, spec, W, H, start, end, fps, levels=None, sim_talk=False):
        self.s, self.W, self.H, self.start, self.end, self.fps = spec, W, H, start, end, fps
        self.dur = end - start
        self.levels, self.sim_talk = levels, sim_talk
        self.land = W >= H
        self.u = (H / 1080) if self.land else (W / 1080)
        self.els, self.chars = [], []
        self.bg = None
        self.bicara = spec.get("bicara")
        getattr(self, "b_" + spec.get("tipe", "dialog").replace("-", "_"), self.b_dialog)()
        self.els.sort(key=lambda e: e.z)

    # ------------------------------------------------------------ util tata letak
    def _bg(self, default):
        self.bg = R.latar(self.s.get("latar", default), self.W, self.H)

    def cue(self, i, n, key=None, lo=0.45, hi=0.72):
        """Waktu lokal kemunculan item ke-i: cari kata kunci di narasi, kalau tidak ada bagi rata."""
        nar = (self.s.get("narasi") or "").lower()
        span = max(0.6, self.dur - 0.3)
        if key and nar:
            words = [w for w in key.lower().replace("\n", " ").split() if len(w) > 2][:2]
            for w in words:
                pos = nar.find(w.strip("*.,!?:"))
                if pos >= 0:
                    return max(lo + 0.18 * i, min(pos / max(1, len(nar)) * span - 0.15, self.dur - 0.5))
        return lo + (span * hi - lo) * (i / max(1, n - 1) if n > 1 else 0)

    def satu_tokoh(self, default_expr="senang", default_pose="tunjuk_samping"):
        s = self.s
        kind = s.get("tokoh", "pria")
        kanan = s.get("posisi") == "kanan"
        W, H = self.W, self.H
        if self.land:
            h = H * 0.86; cx = W * (0.8 if kanan else 0.2)
            box = (W * 0.04, H * 0.07, W * 0.6, H * 0.93) if kanan else (W * 0.42, H * 0.07, W * 0.965, H * 0.93)
        else:
            h = H * 0.4; cx = W * 0.5
            box = (W * 0.06, H * 0.06, W * 0.94, H * 0.56)
        self.chars.append(Tokoh(kind, h, cx, H + h * 0.02, s.get("ekspresi", default_expr), s.get("pose", default_pose), flip=kanan))
        if self.bicara is None:
            self.bicara = kind
        return box, kind, kanan

    def dua_tokoh(self, pose_p="tunjuk_samping", pose_w="diam", expr="senang"):
        s = self.s; W, H = self.W, self.H
        p, w = s.get("pria", {}), s.get("wanita", {})
        h = H * (0.8 if self.land else 0.42)
        xs = (W * 0.27, W * 0.73) if self.land else (W * 0.27, W * 0.73)
        self.chars.append(Tokoh("pria", h, xs[0], H + h * 0.02, p.get("ekspresi", expr), p.get("pose", pose_p)))
        self.chars.append(Tokoh("wanita", h, xs[1], H + h * 0.02, w.get("ekspresi", expr), w.get("pose", pose_w), flip=True, t0=0.12))
        if self.bicara is None:
            self.bicara = "pria"
        return h, xs

    def percikan_di(self, cx, top, sisi=1, t0=0.3):
        u = self.u
        im = R.percikan(int(110 * u))
        if sisi < 0:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        x = cx + sisi * 150 * u
        self.els.append(El(im, x, top + 60 * u, t0, "pop", 0.3, loop="kedip", sfx=None, z=5))

    def pil(self, text, cx, cy, t0=0.15, size=58, ekor=False, max_w=None):
        im = R.pil_judul(text, int(size * self.u), ekor=ekor, max_w=max_w or self.W)
        self.els.append(El(im, cx, cy, t0, "pop", 0.45, sfx="pop", z=3))
        return im

    # ------------------------------------------------------------ tipe adegan
    def b_dialog(self):
        self._bg("kamar")
        h, xs = self.dua_tokoh()
        self._balon_dialog(h, xs)
        sp = self.s.get("percikan", True)
        if sp:
            i = 0 if self.bicara != "wanita" else 1
            self.percikan_di(xs[i], self.H - h, 1 if i == 0 else -1)

    def _balon_dialog(self, h, xs, fill=R.WHITE, t0=0.3):
        txt = self.s.get("balon")
        if not txt:
            return
        u = self.u
        i = 1 if self.bicara == "wanita" else 0
        content = R.teks(txt, int(54 * u), int((700 if self.land else 760) * u), align="center")
        b = R.balon(content, fill=fill, ekor="kiri-bawah" if i == 0 else "kanan-bawah")
        top = self.H - h
        if self.land:
            cx = (xs[0] + xs[1]) / 2 + (-1 if i == 0 else 1) * 0.06 * self.W
            cy = max(b.height / 2 + 20 * u, top + 30 * u - b.height * 0.25)
        else:
            cx = self.W / 2
            cy = max(b.height / 2 + 40 * u, top - b.height / 2 - 20 * u)
        self.els.append(El(b, cx, cy, t0, "pop", 0.4, sfx="pop", z=4))

    def b_judul(self):
        self._bg(self.s.get("latar", "biru"))
        u = self.u
        self.s.setdefault("pria", {}).setdefault("pose", "lambai")
        self.s.setdefault("wanita", {}).setdefault("pose", "lambai")
        h, xs = self.dua_tokoh(pose_p="lambai", pose_w="lambai")
        if self.land:
            for c in self.chars:
                c.h = int(self.H * 0.66); c.cx = self.W * (0.15 if c.kind == "pria" else 0.85)
        im = R.pil_judul(self.s.get("judul", "Judul"), int(88 * u), max_w=int(self.W * 0.6))
        self.els.append(El(im, self.W / 2, self.H * (0.36 if self.land else 0.25), 0.2, "pop", 0.5, z=3))
        if self.s.get("subjudul"):
            t = R.teks(self.s["subjudul"], int(54 * u), int(self.W * 0.6), color=R.NAVY, align="center", weight="black")
            self.els.append(El(t, self.W / 2, self.H * (0.36 if self.land else 0.25) + im.height / 2 + 50 * u, 0.6, "naik", 0.4, sfx=None, z=3))

    def b_tanya(self):
        self._bg("biru")
        box, kind, kanan = self.satu_tokoh("senang", "tunjuk_samping")
        u = self.u
        x0, y0, x1, y1 = box
        small = R.teks(self.s.get("teks", "Apa itu"), int(84 * u), int(x1 - x0), color=R.NAVY, align="center")
        big = R.pil_judul(self.s.get("sorot", "Topik?"), int(104 * u), fill=R.BLUE, pad=(0.55, 0.3))
        content = Image.new("RGBA", (max(small.width, big.width), small.height + big.height - int(10 * u)), (0, 0, 0, 0))
        content.alpha_composite(small, ((content.width - small.width) // 2, 0))
        content.alpha_composite(big, ((content.width - big.width) // 2, small.height - int(20 * u)))
        b = R.balon(content, ekor=("kanan-bawah" if kanan else "kiri-bawah") if not self.land else ("kanan" if kanan else "kiri"), pad=int(46 * u))
        cx = (x0 + x1) / 2; cy = (y0 + y1) / 2 - (40 * u if self.land else 0)
        self.els.append(El(b, cx, cy, 0.25, "pop", 0.5, z=3))
        top = self.chars[0].bottom - self.chars[0].h
        self.percikan_di(self.chars[0].cx, top, -1 if kanan else 1, 0.5)

    def b_definisi(self):
        self._bg("krem")
        box, kind, kanan = self.satu_tokoh("senang", "tunjuk_samping")
        u = self.u
        x0, y0, x1, y1 = box
        bw = int(min(x1 - x0, 980 * u))
        t = R.teks(self.s.get("teks", "Definisi"), int(64 * u), bw - int(110 * u), align="center", spacing=1.2)
        b = R.balon(t, ekor="kanan-bawah" if kanan else "kiri-bawah", pad=int(50 * u), r=int(60 * u))
        cx = (x0 + x1) / 2; cy = y0 + b.height / 2 + 10 * u
        self.els.append(El(b, cx, cy, 0.25, "pop", 0.5, z=3))
        hias = self.s.get("hias", "koin_naik")
        if hias == "koin_naik":
            n = 4
            for i in range(n):
                k = R.ikon("koin", int((120 + i * 24) * u))
                kx = cx - 220 * u + i * 150 * u
                ky = y1 - k.height / 2 - i * 22 * u
                self.els.append(El(k, kx, ky, 0.9 + i * 0.15, "naik", 0.35, z=2))
            arr = self._panah(int(560 * u), int(150 * u))
            self.els.append(El(arr, cx + 40 * u, y1 - 240 * u, 1.5, "gambar", 0.6, sfx="naik", z=2))
        elif hias:
            k = R.ikon(hias, int(220 * u))
            self.els.append(El(k, cx, y1 - k.height / 2, 0.9, "pop", 0.4, loop="goyang", z=2))

    def _panah(self, w, h, col=R.RED):
        k = 2
        img = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
        p = R.Pen(img, k, ow=0)
        pts = R.bez((10, h - 10), (w * 0.4, h - 10), (w * 0.7, h * 0.6), (w - 40, 30), 30)
        p.stroke(pts, 16, col)
        R._arrow(p, w - 80, 70, w - 10, 12, 24, col)
        return img.resize((w, h), Image.LANCZOS)

    def b_contoh(self):
        self._bg("biru")
        box, kind, kanan = self.satu_tokoh("senang", "tunjuk_samping")
        u = self.u
        x0, y0, x1, y1 = box
        card = R.kartu(int(x1 - x0), int(y1 - y0 - 40 * u), r=int(40 * u), alpha=235)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 20 * u
        self.els.append(El(card, cx, cy, 0.1, "pop", 0.45, sfx="pop", z=1))
        self.pil(self.s.get("judul", "Contohnya..."), cx - (x1 - x0) * 0.2, y0 + 40 * u, 0.25, 54)
        items = self.s.get("item", [])[:4] or [{"ikon": "roti", "label": "Roti", "dari": "Rp10.000", "ke": "Rp12.000"}]
        n = len(items)
        cw = (x1 - x0) - 120 * u
        # grafik garis naik
        gw, gh = int(cw), int((y1 - y0) * 0.26)
        g = Image.new("RGBA", (gw * 2, gh * 2), (0, 0, 0, 0)); p = R.Pen(g, 2, ow=0)
        pts = [(30 + i * (gw - 110) / 5, gh - 30 - (i * (gh - 70) / 5) - (12 if i % 2 else 0)) for i in range(6)]
        p.stroke(pts, 12, R.ORANGE)
        for i, q in enumerate(pts[:-1]):
            c = R.RED if i < 2 else R.ORANGE if i < 4 else R.YELLOW
            p.ell(q[0] - 15, q[1] - 15, q[0] + 15, q[1] + 15, c, ow=0)
        R._arrow(p, pts[-2][0], pts[-2][1], gw - 20, 20, 18, R.RED)
        g = g.resize((gw, gh), Image.LANCZOS)
        gy = y0 + 120 * u + gh / 2
        self.els.append(El(g, cx, gy, 0.5, "gambar", 1.2, sfx="naik", z=2))
        # item: ikon + label + harga
        colw = cw / n
        for i, it in enumerate(items):
            ix = x0 + 60 * u + colw * (i + 0.5)
            t0 = self.cue(i, n, it.get("label"), lo=0.9)
            ic = R.ikon(it.get("ikon", "bintang"), int(min(200, 640 / n) * u))
            iy = gy + gh / 2 + 30 * u + ic.height / 2
            self.els.append(El(ic, ix, iy, t0, "pop", 0.4, z=3))
            txt = it.get("label", "")
            if it.get("dari"):
                txt += "\n" + it["dari"]
            if it.get("ke"):
                txt += "\n**→ " + it["ke"] + "**"
            t = R.teks(txt, int(min(48, 160 / n) * u), int(colw), align="center", weight="bold", spacing=1.12)
            self.els.append(El(t, ix, iy + ic.height / 2 + t.height / 2 + 6 * u, t0 + 0.15, "naik", 0.35, sfx=None, z=3))

    def b_ikon_grid(self):
        self._bg(self.s.get("latar", "biru"))
        u = self.u; W, H = self.W, self.H
        items = self.s.get("item", [])[:4] or [{"ikon": "troli", "label": "Contoh"}]
        n = len(items)
        tokoh = self.s.get("tokoh")
        if tokoh:
            box, _, _ = self.satu_tokoh("senang", "tunjuk_samping")
        else:
            box = (W * 0.06, H * 0.06, W * 0.94, H * 0.94) if self.land else (W * 0.05, H * 0.2, W * 0.95, H * 0.8)
            self.bicara = self.bicara or "tidak"
        x0, y0, x1, y1 = box
        cx = (x0 + x1) / 2
        cols = n if (self.land or n <= 2) else 2
        rows = math.ceil(n / cols)
        cw = (x1 - x0 - 80 * u) / cols
        d = int(min(cw * 0.7, 300 * u, (y1 - y0 - 160 * u - rows * 150 * u) / rows))
        ch = d + 150 * u
        card_h = int(130 * u + rows * ch + 30 * u)
        ytop = (y0 + y1) / 2 - card_h / 2 + 20 * u
        card = R.kartu(int(x1 - x0), card_h, r=int(46 * u), fill=(255, 251, 240), alpha=245)
        self.els.append(El(card, cx, ytop + card_h / 2, 0.05, "pop", 0.45, z=1))
        self.pil(self.s.get("judul", "Judul"), cx, ytop, 0.2, 60)
        y0 = ytop - 20 * u
        cols_bg = [(253, 226, 140), (253, 214, 150), (255, 232, 160), (250, 220, 170)]
        for i, it in enumerate(items):
            r_, c_ = divmod(i, cols)
            in_row = min(cols, n - r_ * cols)
            ix = x0 + 40 * u + cw * (c_ + 0.5) + (cols - in_row) * cw / 2
            iy = y0 + 130 * u + ch * r_ + d / 2 + 10 * u
            t0 = self.cue(i, n, it.get("label"), lo=0.6)
            self.els.append(El(R.lingkaran_ikon(it.get("ikon", "bintang"), d, cols_bg[i % 4]), ix, iy, t0, "pop", 0.45, loop="goyang", z=2))
            t = R.teks(it.get("label", ""), int(50 * u), int(cw - 20 * u), align="center", weight="bold", spacing=1.1)
            self.els.append(El(t, ix, iy + d / 2 + 20 * u + t.height / 2, t0 + 0.15, "naik", 0.35, sfx=None, z=2))

    def b_daftar(self):
        self._bg("ungu")
        box, kind, kanan = self.satu_tokoh("senang", "tunjuk_samping")
        u = self.u
        x0, y0, x1, y1 = box
        items = self.s.get("item", [])[:4] or [{"ikon": "troli", "teks": "Poin"}]
        n = len(items)
        cx = (x0 + x1) / 2
        self.pil(self.s.get("judul", "Judul"), cx - (x1 - x0) * 0.08, y0 + 40 * u, 0.15, 58, ekor=True)
        top = y0 + 140 * u
        rh = min(200 * u, (y1 - top) / n)
        rw = int(x1 - x0 - 20 * u)
        for i, it in enumerate(items):
            ry = top + rh * (i + 0.5)
            t0 = self.cue(i, n, it.get("teks"), lo=0.7)
            row = R.kartu(rw, int(rh - 22 * u), r=int(28 * u), alpha=240, shadow=False)
            ic = R.ikon(it.get("ikon", "bintang"), int((rh - 40 * u) * 0.9))
            row.alpha_composite(ic, (int(30 * u), (row.height - ic.height) // 2))
            t = R.teks(it.get("teks", ""), int(50 * u), int(rw - ic.width - 90 * u), weight="bold", spacing=1.1)
            row.alpha_composite(t, (int(60 * u + ic.width), max(0, (row.height - t.height) // 2 + int(4 * u))))
            self.els.append(El(R.bayangan(row, blur=8, off=(0, 4), alpha=40), cx, ry, t0, "kanan", 0.4, z=2))

    def b_checklist(self):
        self._bg("hijau")
        box, kind, kanan = self.satu_tokoh("senang", "tunjuk_atas")
        u = self.u
        x0, y0, x1, y1 = box
        items = self.s.get("item", [])[:5] or ["Poin satu"]
        n = len(items)
        cx = (x0 + x1) / 2
        self.pil(self.s.get("judul", "Caranya"), cx - (x1 - x0) * 0.1, y0 + 40 * u, 0.15, 58)
        cw, chh = int(x1 - x0 - 40 * u), int(y1 - y0 - 140 * u)
        card = R.kartu(cw, chh, r=int(40 * u), alpha=240)
        self.els.append(El(card, cx, y0 + 120 * u + chh / 2, 0.05, "pop", 0.4, sfx=None, z=1))
        rh = min(210 * u, (chh - 60 * u) / n)
        for i, it in enumerate(items):
            ry = y0 + 150 * u + (chh - 60 * u - rh * n) / 2 + rh * (i + 0.5)
            t0 = self.cue(i, n, it, lo=0.6)
            ic = R.ikon("centang", int(min(100 * u, rh * 0.7)))
            self.els.append(El(ic, x0 + 100 * u, ry, t0, "pop", 0.35, sfx="ding", z=3))
            t = R.teks(it, int(54 * u), int(cw - 300 * u), weight="bold", spacing=1.1)
            self.els.append(El(t, x0 + 170 * u + t.width / 2, ry, t0 + 0.1, "kiri", 0.35, sfx=None, z=3))
        if self.s.get("ikon"):
            k = R.ikon(self.s["ikon"], int(200 * u))
            self.els.append(El(k, x1 - 120 * u, y1 - 110 * u, 1.0, "pop", 0.4, loop="goyang", z=4))

    def b_sorak(self):
        self._bg(self.s.get("latar", "krem"))
        s = self.s
        s.setdefault("pria", {}).setdefault("pose", "dua_kepal")
        s.setdefault("wanita", {}).setdefault("pose", "dua_kepal")
        h, xs = self.dua_tokoh(expr="senang")
        for c in self.chars:
            c.h = int(self.H * (0.78 if self.land else 0.42)); c.cx = self.W * ((0.3 if c.kind == 'pria' else 0.7) if self.land else (0.27 if c.kind == 'pria' else 0.73))
        hh = self.chars[0].h
        xs = [c.cx for c in self.chars]
        self._balon_dialog(hh, xs, fill=(255, 214, 90))
        self.percikan_di(xs[0], self.H - hh, -1, 0.4)
        self.percikan_di(xs[1], self.H - hh, 1, 0.5)
        if self.bicara is None or self.s.get("bicara") is None:
            self.bicara = "keduanya"

    def b_angka(self):
        self._bg(self.s.get("latar", "kuning"))
        box, kind, kanan = self.satu_tokoh("kaget", "tunjuk_samping")
        u = self.u
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        card = R.kartu(int(x1 - x0), int((y1 - y0) * 0.8), r=int(50 * u))
        self.els.append(El(card, cx, cy, 0.05, "pop", 0.4, z=1))
        big = R.teks(self.s.get("angka", "50%"), int(200 * u), int(x1 - x0), color=R.RED, align="center", stroke=0)
        self.els.append(El(big, cx, cy - 40 * u, 0.35, "pop", 0.5, sfx="naik", z=2))
        lab = R.teks(self.s.get("label", ""), int(48 * u), int(x1 - x0 - 120 * u), align="center", weight="bold")
        self.els.append(El(lab, cx, cy + big.height / 2 + 10 * u, 0.7, "naik", 0.35, sfx=None, z=2))
        if self.s.get("ikon"):
            self.els.append(El(R.ikon(self.s["ikon"], int(150 * u)), x1 - 90 * u, y0 + 120 * u, 0.9, "pop", 0.4, loop="goyang", z=3))
        self.percikan_di(self.chars[0].cx, self.chars[0].bottom - self.chars[0].h, -1 if kanan else 1, 0.4)

    def b_banding(self):
        self._bg(self.s.get("latar", "biru"))
        u = self.u; W, H = self.W, self.H
        tokoh = self.s.get("tokoh")
        if tokoh:
            box, _, _ = self.satu_tokoh("mikir", "diam")
        else:
            box = (W * 0.05, H * 0.05, W * 0.95, H * 0.95)
            self.bicara = self.bicara or "tidak"
        x0, y0, x1, y1 = box
        cx = (x0 + x1) / 2
        self.pil(self.s.get("judul", "Bandingkan"), cx, y0 + 40 * u, 0.15, 58)
        sides = [self.s.get("kiri", {}), self.s.get("kanan", {})]
        vertical = not self.land
        for i, sd in enumerate(sides):
            if vertical:
                bx0, by0, bx1, by1 = x0, y0 + 110 * u + i * (y1 - y0 - 110 * u) / 2, x1, y0 + 110 * u + (i + 1) * (y1 - y0 - 110 * u) / 2 - 20 * u
            else:
                bx0, by0, bx1, by1 = x0 + i * (x1 - x0) / 2 + 10 * u, y0 + 120 * u, x0 + (i + 1) * (x1 - x0) / 2 - 10 * u, y1
            col = [(255, 236, 236), (230, 246, 232)][i]
            t0 = 0.4 if i == 0 else self.cue(1, 2, sd.get("judul"), lo=1.0)
            bw = bx1 - bx0
            jt = R.teks(sd.get("judul", ""), int(56 * u), int(bw - 40 * u), color=[R.RED, R.GREEN][i], align="center")
            isz = int(min((by1 - by0) * 0.34, 230 * u))
            tt = R.teks(sd.get("teks", ""), int(46 * u), int(bw - 60 * u), align="center", weight="bold")
            need = 40 * u + jt.height + 20 * u + isz + 24 * u + tt.height + 40 * u
            ch = min(by1 - by0, need)
            by0 = (by0 + by1) / 2 - ch / 2
            bxc = (bx0 + bx1) / 2
            card = R.kartu(int(bw), int(ch), r=int(36 * u), fill=col)
            self.els.append(El(card, bxc, by0 + ch / 2, t0, "pop", 0.4, z=1))
            y = by0 + 40 * u
            self.els.append(El(jt, bxc, y + jt.height / 2, t0 + 0.1, "naik", 0.3, sfx=None, z=2)); y += jt.height + 20 * u
            self.els.append(El(R.ikon(sd.get("ikon", "bintang"), isz), bxc, y + isz / 2, t0 + 0.2, "pop", 0.4, sfx=None, z=2)); y += isz + 24 * u
            self.els.append(El(tt, bxc, y + tt.height / 2, t0 + 0.3, "naik", 0.3, sfx=None, z=2))

    def b_penutup(self):
        self._bg("bukit")
        u = self.u; W, H = self.W, self.H
        im = R.pil_judul(self.s.get("teks", "Terima kasih!"), int(80 * u), max_w=int(W * 0.7))
        self.els.append(El(im, W / 2, H * (0.24 if self.land else 0.2), 0.2, "pop", 0.5, z=3))
        ikons = self.s.get("ikon", ["celengan", "koin", "tanaman"])
        n = len(ikons)
        for i, nm in enumerate(ikons):
            sz = int((340 if i == 0 else 260) * u)
            x = W / 2 + (i - (n - 1) / 2) * (340 * u if self.land else 300 * u)
            self.els.append(El(R.ikon(nm, sz), x, H * 0.78 - sz / 2 + 40 * u, 0.6 + i * 0.25, "naik", 0.45, loop="goyang", z=2))
        self.bicara = self.bicara or "tidak"
        if self.s.get("tokoh"):
            self.satu_tokoh("senang", "lambai")
            c = self.chars[0]; c.h = int(H * (0.5 if self.land else 0.3)); c.cx = W * (0.12 if self.land else 0.2)

    # ------------------------------------------------------------ render
    def events(self):
        ev = [(self.start, "whoosh")]
        for e in self.els:
            if e.sfx and e.t0 < self.dur:
                ev.append((self.start + e.t0, e.sfx))
        return ev

    def _mouth(self, c, gf, t):
        """None = mulut bawaan ekspresi. Saat tokoh bicara, mulut buka-tutup mengikuti VO."""
        if self.bicara not in (c.kind, "keduanya"):
            return None
        lv = 0
        if self.levels is not None:
            i = min(len(self.levels) - 1, max(0, (gf // 2) * 2))
            lv = int(self.levels[i])
        elif self.sim_talk and t < self.dur - 0.4:
            ph = (gf // 3) * 7 + (3 if c.kind == "wanita" else 0)
            lv = [0, 2, 3, 1, 2, 0, 3, 1][ph % 8]
        if lv == 0:
            return ("senyum", 0) if c.expr == "senang" else None
        return ("buka", lv)

    def frame(self, t, gf):
        """t = detik lokal adegan, gf = indeks frame global (untuk lipsync)."""
        img = self.bg.copy()
        u = self.u
        for e in self.els:
            if e.z <= 1:
                self._draw_el(img, e, t)
        for c in self.chars:
            k = R.ease_back((t - c.t0) / 0.55, 1.2) if c.enter else 1.0
            dy = (1 - k) * c.h * 0.35
            bob = math.sin((t + c.seed) * 2.2) * 4 * u
            blink = ((t + c.seed * 1.7) % 3.4) < 0.11
            mouth = self._mouth(c, gf, t)
            spr = R.karakter(c.kind, c.h, c.expr, mouth, blink, c.pose, c.flip)
            _paste(img, spr, c.cx - spr.width / 2, c.bottom - spr.height + dy + bob, R.clamp((t - c.t0) / 0.2))
        for e in self.els:
            if e.z > 1:
                self._draw_el(img, e, t)
        return img

    def _draw_el(self, img, e, t):
        u = self.u
        if True:
            if t < e.t0:
                return
            x = R.clamp((t - e.t0) / e.dur)
            im = e.img; a = 1.0; dx = dy = 0.0; sc = 1.0
            if e.anim == "pop":
                sc = 0.55 + 0.45 * R.ease_back(x, 2.0); a = R.clamp(x * 3)
            elif e.anim == "naik":
                dy = (1 - R.ease_out(x)) * 60 * u; a = R.clamp(x * 2)
            elif e.anim == "fade":
                a = R.ease_out(x)
            elif e.anim == "kiri":
                dx = -(1 - R.ease_out(x)) * 90 * u; a = R.clamp(x * 2)
            elif e.anim == "kanan":
                dx = (1 - R.ease_out(x)) * 120 * u; a = R.clamp(x * 2)
            elif e.anim == "gambar" and x < 1:
                w = max(1, int(im.width * R.ease_in_out(x)))
                crop = im.crop((0, 0, w, im.height))
                _paste(img, crop, e.cx - im.width / 2, e.cy - im.height / 2)
                return
            if e.loop == "goyang" and x >= 1:
                dy += math.sin((t - e.t0) * 2.6 + e.cx * 0.01) * 6 * u
            elif e.loop == "kedip" and x >= 1:
                a = 0.55 + 0.45 * (math.sin((t - e.t0) * 9) > -0.3)
            if abs(sc - 1) > 0.004:
                im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
            _paste(img, im, e.cx - im.width / 2 + dx, e.cy - im.height / 2 + dy, a)
