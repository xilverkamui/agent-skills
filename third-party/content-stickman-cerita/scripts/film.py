# -*- coding: utf-8 -*-
"""
film.py - menyusun semua adegan jadi film: jadwal, kata, transisi, subtitle, fade, panel komik.
"""
import math, os, sys, json
from PIL import Image, ImageDraw, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stik import *
import timing
from adegan import Adegan, ScreenCanvas, motion_blur
import tokoh as TK


class Film:
    def __init__(self, projdir, ss=2, ukuran=None):
        self.dir = projdir
        self.proj = json.load(open(os.path.join(projdir, "proyek.json"), encoding="utf-8"))
        W, H = ukuran or self.proj.get("ukuran", [1920, 1080])
        self.W, self.H = int(W), int(H)
        self.fps = int(self.proj.get("fps", 30))
        self.ss = ss
        vo = self.proj.get("vo")
        self.vo = os.path.join(projdir, vo) if vo and not os.path.isabs(vo) else vo
        if self.vo and not os.path.exists(self.vo):
            sys.exit(f"[GAGAL] file VO tidak ditemukan: {self.vo}")
        self.cast = self.proj.get("tokoh", {})
        sp = self.proj["adegan"]
        self.ts, self.total = timing.jadwal(sp, self.vo)
        wf = os.path.join(projdir, "input", "words.json")
        self.words = timing.kata_waktu(sp, self.ts, self.vo, wf)
        self.lv = timing.levels(self.vo, self.fps, self.total) if self.vo else None
        self.scenes = []
        for i, (sc, (a, b)) in enumerate(zip(sp, self.ts)):
            cls = Komik if sc.get("tipe") == "komik" else Adegan
            self.scenes.append(cls(dict(sc), self.W, self.H, a, b, self.fps, self, i))
        self.N = int(math.ceil(self.total * self.fps))
        self.pages = self._pages()
        self.warnings = [w for s in self.scenes for w in s.warn]

    # ---------------------------------------------------------------- kata & mulut
    def words_rel(self, idx):
        return self.words[idx] if idx < len(self.words) else []

    def level(self, t):
        if self.lv is None:                  # draf bisu: mulut bergerak palsu
            return 0.5 + 0.5 * math.sin(t * 13.0) * math.sin(t * 5.3 + 1)
        i = int(t * self.fps)
        if i < 0 or i >= len(self.lv):
            return 0.0
        return float(self.lv[i])

    # ---------------------------------------------------------------- subtitle
    def _pages(self):
        pages = []
        for ws in self.words:
            cur = []
            for w in ws:
                cur.append(w)
                txt = " ".join(x[0] for x in cur)
                if len(cur) >= 6 or len(txt) > 30 or w[0][-1:] in ".?!" or (w[0][-1:] in ",;:" and len(txt) > 16):
                    pages.append(cur)
                    cur = []
            if cur:
                pages.append(cur)
        out = []
        for i, pg in enumerate(pages):
            t0 = pg[0][1]
            t1 = pages[i + 1][0][1] if i + 1 < len(pages) else pg[-1][2] + 0.6
            t1 = min(t1, pg[-1][2] + 0.9)
            out.append((t0, max(t1, pg[-1][2] + 0.15), pg))
        return out

    def caption(self, img, t):
        if not self.proj.get("subtitle", True):
            return img
        pg = None
        for a, b, p in self.pages:
            if a - 0.05 <= t < b:
                pg = p
                break
        if pg is None:
            return img
        S = ScreenCanvas(self.W, self.H, 2)
        size = 56 * (self.H / 1080.0 if self.W >= self.H else self.W / 1080.0 * 0.95)
        f = font("teks", size * S.k)
        sp = size * 0.30
        lens = [f.getlength(w[0]) / S.k for w in pg]
        total = sum(lens) + sp * (len(pg) - 1)
        maxw = self.W * 0.88
        lines = [[]]
        cw = 0
        for w, l in zip(pg, lens):
            if cw + l > maxw and lines[-1]:
                lines.append([])
                cw = 0
            lines[-1].append((w, l))
            cw += l + sp
        y0 = self.H * (0.885 if self.W >= self.H else 0.80) - (len(lines) - 1) * size * 0.6
        pil_style = self.proj.get("gaya_subtitle", "komik") == "pil"
        if pil_style:
            bw = max(sum(l for _, l in ln) + sp * (len(ln) - 1) for ln in lines) + size * 1.4
            bh = len(lines) * size * 1.2 + size * .5
            S.rect(self.W / 2 - bw / 2, y0 - bh / 2 - size * .2, self.W / 2 + bw / 2, y0 + bh / 2 + (len(lines) - 1) * size * 1.2 - size * .2, PUTIH, 5, OUT, r=size * .6)
        for li, ln in enumerate(lines):
            wline = sum(l for _, l in ln) + sp * (len(ln) - 1)
            x = self.W / 2 - wline / 2
            for w, l in ln:
                active = w[1] - 0.02 <= t < w[2] + 0.05 or (t >= w[1] and w is pg[-1])
                col = (255, 214, 60) if (active and not pil_style) else (OUT if pil_style else PUTIH)
                if active and pil_style:
                    col = (226, 56, 56)
                grow = 1.0 + (0.1 * e_back((t - w[1]) / 0.12, 3) if active else 0)
                if pil_style:
                    S.text(x + l / 2, y0 + li * size * 1.2, w[0], size * grow, col, "teks", "mm")
                else:
                    S.text(x + l / 2, y0 + li * size * 1.2, w[0], size * grow, col, "teks", "mm", stroke=size * 0.16, stroke_fill=OUT)
                x += l + sp
        ov = S.finish()
        out = img.convert("RGBA")
        out.alpha_composite(ov)
        return out.convert("RGB")

    # ---------------------------------------------------------------- frame
    def scene_index(self, T):
        i = 0
        while i + 1 < len(self.scenes) and T >= self.scenes[i + 1].start:
            i += 1
        return i

    def trans_of(self, j):
        """Transisi MASUK ke adegan j (j>=1): dict kind,dur,..."""
        sc = self.scenes[j]
        tr = sc.s.get("transisi")
        prev = self.scenes[j - 1]
        if tr is None or tr == "auto":
            same = prev.s.get("latar") == sc.s.get("latar") and prev.s.get("waktu") == sc.s.get("waktu")
            tr = {"jenis": "potong"} if same else {"jenis": "geser", "dur": 0.5}
        if isinstance(tr, str):
            tr = {"jenis": tr}
        d = dict(tr)
        d.setdefault("dur", 0.0 if d["jenis"] == "potong" else 0.55)
        return d

    def raw(self, T):
        i = self.scene_index(T)
        # transisi ke adegan berikutnya mulai setengah durasi sebelum batas
        if i + 1 < len(self.scenes):
            tr = self.trans_of(i + 1)
            nxt = self.scenes[i + 1]
            if tr["dur"] > 0 and T >= nxt.start - tr["dur"] / 2:
                i2 = i + 1
                p = clamp((T - (nxt.start - tr["dur"] / 2)) / tr["dur"])
                A = self.scenes[i].render(T - self.scenes[i].start)
                B = nxt.render(T - nxt.start)
                return blend(A, B, p, tr)
        if i + 1 < len(self.scenes):
            pass
        return self.scenes[i].render(T - self.scenes[i].start)

    def frame(self, f):
        T = f / self.fps
        img = self.raw(T)
        img = self.caption(img, T)
        # fade dari/ke hitam
        fi = float(self.proj.get("fade_masuk", 0.5))
        fo = float(self.proj.get("fade_keluar", 0.8))
        a = 1.0
        if fi > 0 and T < fi:
            a = min(a, T / fi)
        if fo > 0 and T > self.total - fo:
            a = min(a, max(0.0, (self.total - T) / fo))
        if a < 0.999:
            img = Image.blend(Image.new("RGB", img.size, (20, 20, 30)), img, a)
        return img

    def events(self):
        ev = []
        for i, s in enumerate(self.scenes):
            ev += s.events()
            if i > 0:
                tr = self.trans_of(i)
                k = tr["jenis"]
                if k in ("whip", "geser"):
                    ev.append((s.start - tr["dur"] / 2, "whoosh", 0.8))
                elif k == "iris":
                    ev.append((s.start - tr["dur"] / 2, "iris", 0.7))
                elif k in ("zoom", "kedip"):
                    ev.append((s.start - tr["dur"] / 2, "whoosh_lembut", 0.8))
                elif k == "flash":
                    ev.append((s.start - 0.02, "kilat", 0.8))
        return sorted(ev)


# ==================================================================== transisi
def blend(A, B, p, tr):
    k = tr["jenis"]
    W, H = A.size
    e = e_io(p)
    if k == "fade":
        return Image.blend(A, B, e)
    if k == "flash":
        if p < 0.5:
            return Image.blend(A, Image.new("RGB", A.size, (255, 255, 255)), e_out(p * 2))
        return Image.blend(Image.new("RGB", A.size, (255, 255, 255)), B, e_io((p - 0.5) * 2))
    if k == "kedip":      # kelopak menutup lalu membuka
        im = A if p < 0.5 else B
        q = e_io(p * 2) if p < 0.5 else 1 - e_io((p - 0.5) * 2)
        d = ImageDraw.Draw(im)
        h = int(H * 0.5 * q)
        d.rectangle([0, 0, W, h], fill=(20, 20, 30))
        d.rectangle([0, H - h, W, H], fill=(20, 20, 30))
        return im
    if k == "iris":
        cx, cy = tr.get("x", 0.5) * W, tr.get("y", 0.5) * H
        R = math.hypot(max(cx, W - cx), max(cy, H - cy)) * e
        mask = Image.new("L", A.size, 0)
        ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
        out = Image.composite(B, A, mask)
        if 0.02 < p < 0.98:
            ImageDraw.Draw(out).ellipse([cx - R, cy - R, cx + R, cy + R], outline=OUT, width=8)
        return out
    if k in ("geser", "whip"):
        arah = tr.get("arah", "kiri")
        dx, dy = {"kiri": (-1, 0), "kanan": (1, 0), "atas": (0, -1), "bawah": (0, 1)}.get(arah, (-1, 0))
        ox, oy = int(-dx * W * e), int(-dy * H * e)
        canvas = Image.new("RGB", A.size)
        canvas.paste(A, (ox, oy))
        canvas.paste(B, (ox + dx * W, oy + dy * H))
        if k == "whip":
            canvas = motion_blur(canvas, int(math.sin(math.pi * p) * W * 0.06))
        return canvas
    if k == "zoom":
        s_out = 1 + 0.9 * e
        s_in = 0.55 + 0.45 * e
        a = A.resize((int(W * s_out), int(H * s_out)), Image.BILINEAR)
        a = a.crop(((a.width - W) // 2, (a.height - H) // 2, (a.width + W) // 2, (a.height + H) // 2))
        b = B.resize((max(2, int(W * s_in)), max(2, int(H * s_in))), Image.BILINEAR)
        out = Image.blend(a, Image.new("RGB", A.size, (255, 255, 255)), 0.0)
        mask = Image.new("L", A.size, int(255 * e_io(clamp(p * 1.3 - 0.15))))
        canvas = a.copy()
        full = Image.new("RGB", A.size, (255, 255, 255))
        full.paste(b, ((W - b.width) // 2, (H - b.height) // 2))
        return Image.composite(full if s_in < 1 else B, a, mask)
    if k == "wipe":
        x = int(W * e)
        out = A.copy()
        out.paste(B.crop((0, 0, x, H)), (0, 0))
        ImageDraw.Draw(out).line([(x, 0), (x, H)], fill=OUT, width=8)
        return out
    if k == "tirai":     # dua tirai menutup dari atas-bawah
        h = int(H * 0.5 * (e * 2 if p < .5 else 0))
        return Image.blend(A, B, e)
    return B if p >= 0.5 else A


# ==================================================================== panel komik
class Komik:
    """Halaman komik: beberapa panel kecil (masing-masing adegan mini) muncul satu per satu."""

    def __init__(self, spec, W, H, start, end, fps, film, idx):
        self.s = spec
        self.W, self.H = W, H
        self.start, self.end = start, end
        self.dur = max(0.2, end - start)
        self.fps, self.film, self.idx = fps, film, idx
        self.warn = []
        cols, rows = spec.get("grid", [3, 2])
        self.cols, self.rows = cols, rows
        m = int(min(W, H) * 0.03)
        self.m = m
        pw = (W - m * (cols + 1)) / cols
        ph = (H - m * (rows + 1)) / rows
        self.rect = []
        base = Adegan({"latar": "polos"}, W, H, start, end, fps, film, idx)
        self.base = base
        self.warn += base.warn
        self.panels = []
        for i, ps in enumerate(spec.get("panel", [])):
            r, c = divmod(i, cols)
            x0, y0 = m + c * (pw + m), m + r * (ph + m)
            self.rect.append((x0, y0, pw, ph))
            tmu = base.when(ps.get("muncul", i * 1.2))
            sub = Adegan(dict(ps), int(pw), int(ph), start + tmu, end, fps, film, idx)
            sub.u = pw / 1920.0 * 1.0 if W >= H else sub.u
            self.panels.append((tmu, sub))
            self.warn += sub.warn
        self.full = {}

    def render(self, t):
        W, H = self.W, self.H
        page = Image.new("RGB", (W, H), tuple(TK.warna(self.s.get("warna_halaman"), (255, 247, 232))))
        d = ImageDraw.Draw(page)
        zoom = self.s.get("zoom")
        zq, zi = 0.0, None
        if zoom:
            zi = int(zoom.get("panel", 0))
            z0 = base_t = self.base.when(zoom)
            zq = e_io(prog(t, z0, z0 + float(zoom.get("dur", 1.2))))
        for i, (tmu, sub) in enumerate(self.panels):
            if t < tmu:
                continue
            x0, y0, pw, ph = self.rect[i]
            q = e_back((t - tmu) / 0.35, 2.2)
            if zi == i and zq >= 0.995:
                key = i
                if key not in self.full:
                    self.full[key] = Adegan(dict(sub.s), W, H, sub.start, sub.end, self.fps, self.film, self.idx)
                return self.full[key].render(t - tmu)
            im = sub.render(t - tmu)
            if q < 0.98:
                s = max(0.05, q)
                im = im.resize((max(2, int(pw * s)), max(2, int(ph * s))), Image.BILINEAR)
                px, py = int(x0 + pw / 2 - im.width / 2), int(y0 + ph / 2 - im.height / 2)
            else:
                px, py = int(x0), int(y0)
            page.paste(im, (px, py))
            d.rounded_rectangle([px, py, px + im.width, py + im.height], radius=6, outline=OUT, width=7)
        if zi is not None and zq > 0:
            x0, y0, pw, ph = self.rect[zi]
            fx0, fy0, fx1, fy1 = lerp(0, x0, zq), lerp(0, y0, zq), lerp(W, x0 + pw, zq), lerp(H, y0 + ph, zq)
            page = page.crop((int(fx0), int(fy0), int(fx1), int(fy1))).resize((W, H), Image.BICUBIC)
        return page

    def events(self):
        ev = []
        for tmu, sub in self.panels:
            ev.append((self.start + tmu, "pop", 0.9))
            ev += sub.events()
        return ev
