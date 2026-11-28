# -*- coding: utf-8 -*-
"""
adegan.py - satu adegan: aktor (tokoh + gerak), kamera virtual, benda, balon, teks, efek.

Waktu di dalam adegan selalu DETIK RELATIF terhadap awal adegan. Setiap item boleh memakai
  "t": 1.5                      -> detik tetap
  "kata": "jam tujuh"           -> saat frasa itu diucapkan di narasi adegan (+ "geser": -0.2 untuk maju/mundur)
"""
import math, re
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from stik import *
import tokoh as TK
import benda as BD
import dunia as DN

SS_DEFAULT = 2

# ---------------------------------------------------------------- ukuran bidikan (zoom, y pusat relatif tokoh berskala 1)
UKURAN = {
    "sangat_lebar": (0.56, -330),
    "lebar": (0.86, -300),
    "penuh": (1.25, -228),
    "sedang": (1.9, -330),
    "dekat": (3.0, -338),
    "sangat_dekat": (5.2, -352),
}
URUT_UKURAN = ["sangat_lebar", "lebar", "penuh", "sedang", "dekat", "sangat_dekat"]


def norm(s):
    return re.sub(r"[^\w\s]", "", s.lower().replace("-", " ")).split()


class ScreenCanvas(Canvas):
    """Kanvas ruang-layar (piksel, tanpa kamera) transparan untuk balon, teks, efek."""

    def __init__(self, W, H, ss):
        super().__init__(W, H, ss, Cam(), 1.0)
        self.im = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _refresh(self):
        self.k = self.ss
        self.ox = self.oy = 0.0

    def set_depth(self, d):
        pass


# =================================================================== AKTOR
class Aktor:
    def __init__(self, sc, spec, cast):
        self.sc = sc
        self.id = spec.get("id") or spec.get("dasar") or "raka"
        dasar = spec.get("dasar", self.id)
        base = cast.get(self.id, cast.get(dasar, dasar))
        if isinstance(base, str):
            base = {"dasar": base}
        base = dict(base)
        for k in ("kacamata", "hijab", "rambut", "kemeja", "dasi", "bawah", "bawah_warna", "skala_dasar"):
            if k in spec:
                base[k] = spec[k]
        self.tk = TK.Tokoh(base)
        self.s = float(spec.get("skala", 1.0))
        self.x0, self.y0 = float(spec.get("x", 0)), float(spec.get("y", 0))
        self.seed = (hash(self.id) % 97) / 10.0
        self.layer = spec.get("lapis", 0)
        base_state = {k: spec[k] for k in ("pose", "ekspresi", "hadap", "bawa", "ransel", "bicara", "lihat", "tali_ransel") if k in spec}
        base_state.setdefault("pose", "diam")
        base_state.setdefault("ekspresi", "senang")
        base_state["t"] = 0.0
        self.keys = [base_state]
        self.moves = []
        self.icons = []
        self.t_in, self.t_out = None, None
        self.in_style, self.out_style = None, None
        pos = (self.x0, self.y0)
        acts = []
        for a in spec.get("aksi", []):
            acts.append((sc.when(a), a))
        # masuk / keluar
        mk = spec.get("masuk")
        if mk:
            t0 = sc.when(mk)
            dur = float(mk.get("dur", 0.9))
            gaya = mk.get("gaya", "jalan" if mk.get("dari", "kiri") in ("kiri", "kanan") else mk.get("dari"))
            dr = mk.get("dari", "kiri")
            self.t_in = t0
            self.in_style = (gaya, dr, dur)
            if dr in ("kiri", "kanan"):
                sx = self.x0 + (-1 if dr == "kiri" else 1) * float(mk.get("jarak", 1300))
                self.moves.append(dict(t0=t0, t1=t0 + dur, x0=sx, y0=self.y0, x1=self.x0, y1=self.y0, gaya=gaya if gaya in ("jalan", "lari", "geser") else "jalan"))
                self.keys.append(dict(t=t0, hadap="kanan" if dr == "kiri" else "kiri"))
                self.keys.append(dict(t=t0 + dur, hadap=mk.get("hadap_akhir", "depan")))
        xk = spec.get("keluar")
        if xk:
            t0 = sc.when(xk)
            dur = float(xk.get("dur", 1.0))
            dr = xk.get("ke", "kanan")
            self.t_out = t0 + (dur if dr in ("kiri", "kanan") else 0.3)
            self.out_style = (xk.get("gaya", "jalan"), dr, dur)
            acts.append((t0, dict(ke_x_rel=(1 if dr == "kanan" else -1) * float(xk.get("jarak", 1300)), durasi=dur, gaya=xk.get("gaya", "jalan"))))
        acts.sort(key=lambda z: z[0])
        cur = pos
        for t, a in acts:
            st = {k: a[k] for k in ("pose", "ekspresi", "hadap", "bawa", "ransel", "bicara", "lihat", "skala", "tali_ransel") if k in a}
            if st:
                st["t"] = t
                self.keys.append(st)
            if "ke_x" in a or "ke_y" in a or "ke_x_rel" in a:
                # posisi awal gerak = posisi terakhir (hasil gerak sebelumnya)
                px, py = self._pos_end(cur)
                tx = a["ke_x"] if "ke_x" in a else (px + a["ke_x_rel"] if "ke_x_rel" in a else px)
                ty = a.get("ke_y", py)
                dur = float(a.get("durasi", max(0.4, abs(tx - px) / 300.0)))
                gaya = a.get("gaya", "jalan" if abs(tx - px) > 20 else "geser")
                self.moves.append(dict(t0=t, t1=t + dur, x0=px, y0=py, x1=tx, y1=ty, gaya=gaya))
                if abs(tx - px) > 30 and "hadap" not in a and gaya in ("jalan", "lari", "geser", "lompat"):
                    self.keys.append(dict(t=t, hadap="kanan" if tx > px else "kiri"))
                    if a.get("hadap_akhir"):
                        self.keys.append(dict(t=t + dur, hadap=a["hadap_akhir"]))
            if "efek" in a:
                self.icons.append(dict(t0=t, t1=t + float(a.get("efek_dur", 1.4)), jenis=a["efek"], dx=a.get("efek_x", None), dy=a.get("efek_y", None)))
        for m in self.moves:
            pass
        self.moves.sort(key=lambda m: m["t0"])
        self.keys.sort(key=lambda k: k["t"])
        # bicara: daftar jendela waktu
        self.talk_win = []
        bc = spec.get("bicara")
        if bc is True:
            self.talk_win.append((0, 1e9))
        elif isinstance(bc, list):
            for w in bc:
                if isinstance(w, (list, tuple)):
                    self.talk_win.append((sc.when(w[0]), sc.when(w[1])))

    def _pos_end(self, cur):
        if self.moves:
            m = self.moves[-1]
            return (m["x1"], m["y1"])
        return cur

    # --- keadaan diskret pada waktu t
    def disc(self, t):
        d = {}
        last_pose_t = 0.0
        prev_pose = None
        pose_t = 0.0
        for k in self.keys:
            if k["t"] <= t + 1e-6:
                if "pose" in k and k["pose"] != d.get("pose"):
                    prev_pose = d.get("pose")
                    pose_t = k["t"]
                d.update({kk: vv for kk, vv in k.items() if kk != "t"})
        d["_pose_t"] = pose_t
        d["_prev_pose"] = prev_pose
        return d

    def pos(self, t):
        x, y = self.x0, self.y0
        gaya, p, mv = None, 0.0, None
        for m in self.moves:
            if t >= m["t1"]:
                x, y = m["x1"], m["y1"]
            elif t > m["t0"]:
                p = (t - m["t0"]) / (m["t1"] - m["t0"])
                e = 0.65 * p + 0.35 * e_io(p) if m["gaya"] in ("jalan", "lari") else e_io(p)
                x, y = lerp(m["x0"], m["x1"], e), lerp(m["y0"], m["y1"], e)
                gaya, mv = m["gaya"], m
                break
            else:
                x, y = m["x0"], m["y0"]
                break
        return x, y, gaya, p, mv

    def visible(self, t):
        if self.t_in is not None and t < self.t_in - 1e-6:
            return False
        if self.t_out is not None and t > self.t_out + 1e-6:
            return False
        return True

    def talk_level(self, t):
        for a, b in self.talk_win:
            if a <= t <= b:
                return True
        d = self.disc(t)
        return bool(d.get("bicara")) is True and d.get("bicara") is True

    # --- state penuh untuk digambar
    def state(self, t, level=None):
        d = self.disc(t)
        x, y, gaya, p, mv = self.pos(t)
        pose_name = d.get("pose", "diam")
        base = TK.pose_state(pose_name, t)
        pt = d["_pose_t"]
        if d["_prev_pose"] and t - pt < 0.3:                  # campur pose lama -> baru
            q = e_io((t - pt) / 0.3)
            old = TK.pose_state(d["_prev_pose"], t)
            for side in "LR":
                a0, a1 = old["arms"][side], base["arms"][side]
                base["arms"][side] = (lerp(a0[0], a1[0], q), lerp(a0[1], a1[1], q), a1[2] if q > .5 else a0[2])
            for kk in ("sit", "lean", "tilt"):
                base[kk] = lerp(old[kk], base[kk], q)
        hadap = d.get("hadap", "depan")
        flip = -1 if hadap == "kiri" else 1
        look = (0.8 * (1 if hadap == "kanan" else -1 if hadap == "kiri" else 0), 0.0)
        if "lihat" in d and d["lihat"] is not None:
            look = tuple(d["lihat"])
        walking = gaya in ("jalan", "lari") and mv is not None
        hop = 0.0
        squash = (1.0, 1.0)
        phase, amp = 0.0, 0.0
        bob = 0.0
        if walking:
            sp = 2.3 if gaya == "lari" else 1.0
            dist = abs(mv["x1"] - mv["x0"]) * (0.65 * p + 0.35 * e_io(p))
            phase = dist / 78.0 * math.pi * (1.0 if gaya == "jalan" else 1.15)
            amp = 1.0 if gaya == "jalan" else 1.5
            base["legs"] = "walk"
            if pose_name in ("diam", "santai", "jalan", "lari"):
                sw = math.sin(phase) * (30 if gaya == "jalan" else 52)
                base["arms"]["L"] = (16 + sw, 10, "m") if gaya == "jalan" else (36 + sw, -78, "m")
                base["arms"]["R"] = (16 - sw, 10, "m") if gaya == "jalan" else (36 - sw, -78, "m")
            if gaya == "lari":
                base["lean"] = max(base["lean"], 9)
            bob = abs(math.sin(phase)) * (7 if gaya == "jalan" else 14)
            hop = -bob
        elif mv is not None and gaya == "lompat":
            hop = -4 * 70 * p * (1 - p)
            squash = (1 + 0.1 * (1 - 4 * p * (1 - p)) * 0, 1.0)
        else:
            amp = 0.0
        # napas (hidup)
        life = math.sin(t * 2.1 + self.seed) * 2.6
        if not walking:
            hop += life * 0.4
        # masuk: pop / jatuh
        if self.t_in is not None and self.in_style:
            gya, dr, dur = self.in_style
            q = t - self.t_in
            if gya == "pop" and 0 <= q < 0.6:
                k = e_back(q / 0.45, 2.4)
                squash = (k, k)
            elif gya == "jatuh" and 0 <= q < dur + 0.35:
                h0 = 900
                if q < dur:
                    hop = -h0 * (1 - e_in(q / dur))
                else:
                    z = (q - dur) / 0.35
                    squash = (1 + 0.28 * math.sin(math.pi * z) * (1 - z), 1 - 0.28 * math.sin(math.pi * z) * (1 - z))
            elif gya == "lompat" and 0 <= q < dur:
                z = q / dur
                hop = -4 * 160 * z * (1 - z)
        blink = TK.blink_at(t, self.seed)
        talk = None
        if level is not None and (self.talk_level(t)):
            talk = clamp(level)
        st = dict(x=x, y=y, s=self.s * d.get("skala", 1.0), flip=flip, expr=d.get("ekspresi", "senang"), look=look, blink=blink,
                  phase=phase, amp=amp, hop=hop, squash=squash, talk=talk,
                  ransel=d.get("ransel"), tali_ransel=d.get("ransel"), bawa=d.get("bawa"))
        st.update(base)
        if st.get("legs") != "walk":
            st["amp"] = 0.0
        if st["expr"] in ("tidur",) or pose_name == "tidur":
            st["blink"] = 0
        st["bob"] = bob
        return st

    # --- gambar
    def draw(self, c, t, level):
        if not self.visible(t):
            return None
        st = self.state(t, level)
        hands = self.tk.draw(c, st)
        d = self.disc(t)
        bawa = d.get("bawa")
        if bawa:
            self._bawa(c, st, hands, bawa, t)
        return st

    def _bawa(self, c, st, hands, bawa, t):
        s = st["s"] * self.tk.p["skala"]
        if isinstance(bawa, str):
            bawa = {"jenis": bawa}
        jenis = bawa["jenis"]
        side = bawa.get("tangan", "kanan")
        pose_hand = {"kanan": "R", "kiri": "L"}.get(side, "R")
        h = hands[pose_hand]
        hx, hy = h["pos"]
        px, py = hx, hy
        rot = bawa.get("rot", 0)
        if jenis in ("hp", "buku", "kertas", "laptop", "stik"):
            if jenis == "hp" and st["arms"]["R"][0] > 20 and st["arms"]["R"][1] < -100:
                # dua tangan memegang: taruh di tengah kedua tangan
                lx, ly = hands["L"]["pos"]
                px, py = (hx + lx) / 2, (hy + ly) / 2 - 14 * s * c.cam.z * 0
        k = c.k
        wx, wy = (px - c.ox) / k, (py - c.oy) / k   # balik ke koordinat dunia
        if jenis == "hp":
            rot = rot or (-8 if pose_hand == "R" else 8)
            BD.gambar(c, "hp", wx, wy - 8 * s, s * .95, rot, t, layar=tuple(bawa.get("layar", (120, 182, 255))), play=bawa.get("play"))
        elif jenis == "stik":
            BD.gambar(c, "stik", wx, wy - 6 * s, s * 1.05, rot, t)
        elif jenis == "pensil":
            BD.gambar(c, "pensil", wx, wy, s * .8, rot or 36, t)
        else:
            BD.gambar(c, jenis, wx, wy - 16 * s, s * (0.9 if jenis in ("buku", "kertas", "laptop") else 1.0), rot, t, **{k2: v for k2, v in bawa.items() if k2 in ("buka", "warna", "isi", "layar", "jam")})
        # tangan di atas benda: gambar ulang tangan (agar benda terlihat digenggam)
        c.ell(px, py, 17.5 * s * c.k / c.k if False else 17.5 * s, 17.5 * s, None) if False else None
        c.set_depth(1.0)

    def head_world(self, t):
        st = self.state(t)
        s = st["s"] * self.tk.p["skala"]
        dy = TK.SIT_DROP * st.get("sit", 0)
        hop = st.get("hop", 0)
        return st["x"], st["y"] + (TK.HEAD_Y - 120 + dy) * s + hop


# =================================================================== ADEGAN
class Adegan:
    def __init__(self, spec, W, H, start, end, fps, film, idx=0):
        self.s = spec
        self.W, self.H = W, H
        self.start, self.end = start, end
        self.dur = max(0.2, end - start)
        self.fps = fps
        self.film = film
        self.idx = idx
        self.u = H / 1080.0 if W >= H else W / 1080.0 * 1.25
        self.ss = film.ss
        self.opts = dict(spec.get("opsi", {}))
        for k in ("waktu", "jam", "papan", "warna", "alarm", "papan_tulis", "selimut", "lampu_nyala", "meja_depan"):
            if k in spec:
                self.opts[k] = spec[k]
        self.words = film.words_rel(idx)
        self.warn = []
        self.setb, self.setf = DN.set_of(spec.get("latar", "polos"))
        self.actors = [Aktor(self, a, film.cast) for a in spec.get("tokoh", [])]
        self.by_id = {a.id: a for a in self.actors}
        self.props = spec.get("benda", [])
        self.balon = spec.get("balon", [])
        self.teks = spec.get("teks", [])
        self.efek = spec.get("efek", [])
        self._build_camera(spec.get("kamera", {}))
        self.vign = None

    # ------------------------------------------------------------ waktu
    def cue(self, phrase, nth=0):
        """Detik (relatif adegan) saat frasa mulai diucapkan. Cocok per kata, abaikan tanda baca/huruf besar."""
        ws = norm(phrase)
        if not ws:
            return 0.0
        toks = []                      # (token, indeks kata)
        for i, w in enumerate(self.words):
            for tk in norm(w[0]):
                toks.append((tk, i))
        names = [t[0] for t in toks]
        hits = [i for i in range(len(names) - len(ws) + 1) if names[i:i + len(ws)] == ws]
        if not hits:                   # longgar: awalan 4 huruf (kata berimbuhan)
            hits = [i for i in range(len(names) - len(ws) + 1)
                    if all(names[i + j][:4] == ws[j][:4] for j in range(len(ws)))]
        if hits:
            i = hits[min(nth, len(hits) - 1)]
            return max(0.0, self.words[toks[i][1]][1] - self.start)
        self.warn.append(f"adegan {self.idx + 1}: frasa '{phrase}' tidak ditemukan di narasi (dipakai t=0)")
        return 0.0

    def when(self, a):
        if isinstance(a, (int, float)):
            return float(a)
        if isinstance(a, str):
            return self.cue(a[5:] if a.startswith("kata:") else a)
        if isinstance(a, dict):
            if "kata" in a:
                return self.cue(a["kata"], int(a.get("urutan", 0))) + float(a.get("geser", 0))
            return float(a.get("t", 0)) + float(a.get("geser", 0))
        return 0.0

    def when_end(self, a, key="sampai", default=None):
        if key + "_kata" in a:
            ws = norm(a[key + "_kata"])
            t = self.cue(a[key + "_kata"])
            return t + 0.35 * len(ws) + 0.25
        if key in a:
            v = a[key]
            return self.when(v) if not isinstance(v, (int, float)) else float(v)
        return default

    # ------------------------------------------------------------ kamera
    def _target(self, ke, t, base=None):
        """Spesifikasi target -> Cam. ke: {ukuran, fokus, x, y, z, r, blur, z_kali}"""
        base = base or Cam()
        if isinstance(ke, str):
            ke = {"ukuran": ke}
        p = base.copy()
        uk = ke.get("ukuran")
        fok = ke.get("fokus")
        ids = [fok] if isinstance(fok, str) else (fok or [])
        acts = [self.by_id[i] for i in ids if i in self.by_id]
        if acts:
            xs, ys = [], []
            zmin = 9
            for a in acts:
                st = a.state(t)
                xs.append(st["x"])
                ys.append(st["y"])
            if uk:
                z0, yo = UKURAN.get(uk, UKURAN["lebar"])
                a0 = acts[0]
                st0 = a0.state(t)
                sk = st0["s"] * a0.tk.p["skala"]
                sit_drop = TK.SIT_DROP * st0.get("sit", 0) if uk in ("sedang", "dekat", "sangat_dekat", "penuh") else 0
                p.y = float(np_mean(ys)) + (yo + sit_drop) * sk
                p.z = z0 / (sk if uk not in ("lebar", "sangat_lebar") else 1.0) if False else z0
                if len(acts) > 1:      # dua bidikan: muat semua
                    span = max(xs) - min(xs) + 520
                    p.z = min(z0, max(0.5, (self.W / self.u) * 0.9 / span))
                else:
                    p.z = z0
                # ruang pandang: geser sedikit ke arah hadap
                fl = 1 if a0.disc(t).get("hadap") == "kanan" else -1 if a0.disc(t).get("hadap") == "kiri" else 0
                p.x = float(np_mean(xs)) + fl * (0.05 * self.W / self.u / p.z)
            else:
                p.x = float(np_mean(xs))
        if uk and not acts:
            z0, yo = UKURAN.get(uk, UKURAN["lebar"])
            p.z = z0
            p.y = yo
        for k in ("x", "y", "z", "r", "blur"):
            if k in ke and not (k in ("x", "y") and False):
                if k in ("x", "y") and ke.get("relatif"):
                    setattr(p, k, getattr(p, k) + ke[k])
                else:
                    setattr(p, k, ke[k])
        if "dx" in ke:
            p.x += ke["dx"]
        if "dy" in ke:
            p.y += ke["dy"]
        if "z_kali" in ke:
            p.z *= ke["z_kali"]
        return p

    def _build_camera(self, kam):
        self.cam_segs = []
        self.follows = []
        self.punches = []
        self.shakes = []
        self.ayun = []
        self.idle = kam.get("hidup", True)
        self.creep = kam.get("dorong_pelan", 0.05)
        awal = kam.get("awal", "lebar" if self.actors else {"x": 0, "y": -300, "z": 1.0})
        if isinstance(awal, str):
            awal = {"ukuran": awal, "fokus": [a.id for a in self.actors[:1]]}
        elif "ukuran" in awal and "fokus" not in awal and self.actors:
            awal = dict(awal, fokus=[self.actors[0].id])
        self.cam0 = self._target(awal, 0.0)
        cur = self.cam0.copy()
        gerak = sorted(kam.get("gerak", []), key=lambda g: self.when(g))
        self.whips = []
        for g in gerak:
            j = g.get("jenis", "pindah")
            t0 = self.when(g)
            dur = float(g.get("dur", 1.5))
            ease = g.get("ease", "io")
            ke = dict(g.get("ke", {})) if isinstance(g.get("ke", {}), dict) else {"ukuran": g.get("ke")}
            for k in ("ukuran", "fokus", "x", "y", "z", "r", "blur", "dx", "dy", "z_kali"):
                if k in g and k not in ke:
                    ke[k] = g[k]
            tend = t0 + dur
            if j in ("pindah", "push", "pull", "mendekat", "menjauh", "pan", "tilt", "terbang", "whip", "zoom_cepat", "crane", "potong", "miring", "fokus", "reveal"):
                if j in ("push", "mendekat") and not any(k in ke for k in ("ukuran", "z", "z_kali")):
                    ke["z_kali"] = float(g.get("kali", 1.4))
                if j in ("pull", "menjauh") and not any(k in ke for k in ("ukuran", "z", "z_kali")):
                    ke["z_kali"] = 1.0 / float(g.get("kali", 1.4))
                if j in ("push", "mendekat", "pull", "menjauh", "pan", "tilt", "crane", "miring", "fokus", "zoom_cepat") and "fokus" not in ke and "ukuran" not in ke:
                    pass
                tgt = cur.copy()
                if j == "pan":
                    if "fokus" in ke or "x" in ke or "dx" in ke:
                        tp = self._target(dict(ke, ukuran=None) if "fokus" in ke else ke, tend, cur)
                        tgt.x = tp.x
                elif j == "tilt" or j == "crane":
                    tp = self._target(ke, tend, cur)
                    tgt.y = tp.y if ("y" in ke or "dy" in ke or "fokus" in ke) else cur.y
                elif j == "miring":
                    tgt.r = float(ke.get("r", g.get("r", 4)))
                elif j == "fokus":
                    tgt.blur = float(ke.get("blur", g.get("blur", 6)))
                elif j == "potong":
                    tgt = self._target(ke, t0, cur)
                    dur = 0.0
                    tend = t0
                else:
                    tgt = self._target(ke, tend, cur)
                if j == "whip":
                    dur = float(g.get("dur", 0.38))
                    tend = t0 + dur
                    ease = "io"
                    self.whips.append((t0, tend))
                if j == "zoom_cepat":
                    dur = float(g.get("dur", 0.25))
                    tend = t0 + dur
                    ease = "snap"
                dip = 0.0
                if j == "terbang":
                    dist = math.hypot((tgt.x - cur.x), (tgt.y - cur.y)) * cur.z
                    dip = float(g.get("dip", clamp(dist / 2600, 0.12, 0.5)))
                self.cam_segs.append(dict(t0=t0, t1=tend, p0=cur.copy(), p1=tgt.copy(), ease=ease, dip=dip, jenis=j))
                cur = tgt
            elif j == "ikut":
                fok = g.get("fokus") or (self.actors[0].id if self.actors else None)
                self.follows.append(dict(t0=t0, t1=float(self.when_end(g, "sampai", self.dur)), id=fok, dx=float(g.get("dx", g.get("ofset", 0))), lag=float(g.get("lag", 0.5)),
                                         z=g.get("z"), ukuran=g.get("ukuran")))
            elif j == "punch":
                self.punches.append((t0, float(g.get("kuat", 0.16)), float(g.get("dur", 0.45))))
            elif j == "goyang":
                self.shakes.append((t0, float(g.get("kuat", 14)), float(g.get("dur", 0.5))))
            elif j == "ayun":
                self.ayun.append((t0, float(g.get("sampai", self.dur)) if not isinstance(g.get("sampai"), str) else self.dur, float(g.get("kuat", 70)), float(g.get("periode", 6))))
            elif j == "diam":
                pass

    def cam_at(self, t):
        # dasar
        c = self.cam0.copy()
        for sg in self.cam_segs:
            if t >= sg["t1"] - 1e-9:
                c = sg["p1"].copy()
            elif t >= sg["t0"]:
                q = EASE.get(sg["ease"], e_io)((t - sg["t0"]) / max(1e-6, sg["t1"] - sg["t0"]))
                a, b = sg["p0"], sg["p1"]
                lz = lerp(math.log(max(a.z, 1e-3)), math.log(max(b.z, 1e-3)), q) - sg["dip"] * math.sin(math.pi * q)
                c = Cam(lerp(a.x, b.x, q), lerp(a.y, b.y, q), math.exp(lz), lerp(a.r, b.r, q), lerp(a.blur, b.blur, q))
                break
            else:
                break
        # idle + dorong pelan
        if self.idle:
            c.x += 5 * math.sin(t * 0.37)
            c.y += 3 * math.sin(t * 0.51 + 1)
            c.z *= 1 + 0.004 * math.sin(t * 0.43)
        if self.creep:
            c.z *= 1 + self.creep * clamp(t / max(self.dur, 1.0))
        # ikut
        for f in self.follows:
            a = self.by_id.get(f["id"])
            if not a:
                continue
            w = e_io(prog(t, f["t0"] - 0.0, f["t0"] + 0.7)) * (1 - e_io(prog(t, f["t1"] - 0.5, f["t1"] + 0.3)))
            if w <= 0:
                continue
            n = 6
            xs = [a.pos(max(0, t - f["lag"] * i / n))[0] for i in range(n + 1)]
            tx = sum(xs) / len(xs) + f["dx"]
            hd = a.disc(t).get("hadap")
            tx += (1 if hd == "kanan" else -1 if hd == "kiri" else 0) * 130
            c.x = lerp(c.x, tx, w)
            if f.get("z"):
                c.z = lerp(c.z, float(f["z"]), w)
        # punch
        for (t0, k, d) in self.punches:
            q = t - t0
            if 0 <= q < d:
                c.z *= 1 + k * (e_snap(q / 0.08) if q < 0.08 else (1 - e_io((q - 0.08) / (d - 0.08))))
        # ayun (orbit semu)
        for (t0, t1, amp, per) in self.ayun:
            if t0 <= t <= t1:
                w = e_io(prog(t, t0, t0 + 0.8)) * (1 - e_io(prog(t, t1 - 0.8, t1)))
                c.x += math.sin((t - t0) / per * 2 * math.pi) * amp * w
        # goyang
        sx = sy = 0.0
        for (t0, amp, d) in self.shakes:
            q = t - t0
            if 0 <= q < d:
                dec = (1 - q / d) ** 2
                sx += math.sin(q * 61.0) * amp * dec
                sy += math.cos(q * 53.0 + 1) * amp * 0.7 * dec
        c.shk_x, c.shk_y = sx / max(c.z * self.u, 0.01), sy / max(c.z * self.u, 0.01)
        return c

    def whip_amount(self, t):
        for (a, b) in self.whips:
            if a - 0.02 <= t <= b + 0.02:
                return math.sin(math.pi * clamp((t - a) / (b - a))) ** 0.6
        return 0.0

    # ------------------------------------------------------------ render
    def render(self, t, absf=0):
        """Gambar frame pada waktu relatif t (boleh <0 atau >dur: ditahan)."""
        W, H = self.W, self.H
        tt = max(0.0, t)
        cam = self.cam_at(tt)
        c = Canvas(W, H, self.ss, cam, self.u)
        o = self.opts
        self.setb(c, tt, o)
        c.set_depth(1.0)
        # benda belakang
        self._props(c, tt, "belakang")
        if cam.blur > 0.4:
            c.im = c.im.filter(ImageFilter.GaussianBlur(cam.blur * self.ss * 0.9))
            c.d = ImageDraw.Draw(c.im, "RGBA")
        lv = self.film.level(self.start + tt)
        order = sorted(self.actors, key=lambda a: (a.layer, a.pos(tt)[1]))
        states = {}
        for a in order:
            st = a.draw(c, tt, lv)
            if st:
                states[a.id] = st
        self._props(c, tt, "depan")
        self._icons(c, tt, states)
        self.setf(c, tt, o)
        img = c.finish()
        wa = self.whip_amount(tt)
        if wa > 0.02:
            img = motion_blur(img, int(wa * W * 0.05))
        # overlay layar
        ov = self._overlay(tt, cam, states)
        if ov is not None:
            img = img.convert("RGBA")
            img.alpha_composite(ov)
            img = img.convert("RGB")
        img = self._fx(img, tt)
        return img

    # ------------------------------------------------------------ benda & ikon
    def _props(self, c, t, lapis):
        for p in self.props:
            if p.get("lapis", "depan") != lapis:
                continue
            t0 = self.when(p)
            t1 = self.when_end(p, "sampai", 1e9)
            if not (t0 <= t <= t1):
                continue
            x, y = p.get("x", 0), p.get("y", 0)
            anch = p.get("ikut")
            if anch and anch in self.by_id:
                a = self.by_id[anch]
                hx, hy = a.head_world(t)
                x, y = hx + p.get("dx", 0), hy + p.get("dy", 0)
            q = e_back((t - t0) / 0.35, 2.0)
            s = p.get("skala", 1.0) * q
            if p.get("melayang"):
                y -= (t - t0) * float(p["melayang"])
            if p.get("goyang"):
                x += math.sin(t * 9) * float(p["goyang"])
            BD.gambar(c, p["jenis"], x, y, s, p.get("rot", 0), t - t0, **{k: v for k, v in p.items() if k in ("jam", "warna", "isi", "buka", "layar", "on", "alarm", "pita")})

    def _icons(self, c, t, states):
        for a in self.actors:
            if a.id not in states:
                continue
            st = states[a.id]
            s = st["s"] * a.tk.p["skala"]
            for ic in a.icons:
                if not (ic["t0"] <= t <= ic["t1"]):
                    continue
                q = t - ic["t0"]
                k = e_back(q / 0.3, 2.2) * (1 - e_in(prog(t, ic["t1"] - 0.25, ic["t1"])))
                dx = ic["dx"] if ic["dx"] is not None else 118 * s
                dy = ic["dy"] if ic["dy"] is not None else -(470 + 36) * s + TK.SIT_DROP * st.get("sit", 0) * s
                if ic["jenis"] in ("hati", "not", "musik"):
                    dy -= q * 40
                if ic["jenis"] in ("keringat",):
                    dy, dx = -330 * s, 96 * s
                if ic["jenis"] in ("zzz",):
                    dx, dy = 110 * s, -400 * s + TK.SIT_DROP * st.get("sit", 0) * s
                if ic["jenis"] == "bintang":
                    for i in range(3):
                        ang = q * 5 + i * 2.1
                        BD.gambar(c, "bintang", st["x"] + math.cos(ang) * 110 * s, st["y"] - 480 * s + math.sin(ang) * 26 * s + TK.SIT_DROP * st.get("sit", 0) * s, 0.45 * s * k, 0, t)
                    continue
                BD.gambar(c, ic["jenis"], st["x"] + dx * st["flip"] * (1 if st["flip"] > 0 else -1) * (1 if True else 1), st["y"] + dy + st.get("hop", 0), 0.9 * s * k, math.sin(q * 6) * 6, q)

    # ------------------------------------------------------------ overlay layar
    def _screen_pt(self, cam, x, y):
        k = self.u * cam.z
        return (self.W / 2 + (x - cam.x) * k, self.H / 2 + (y - cam.y) * k)

    def _overlay(self, t, cam, states):
        S = ScreenCanvas(self.W, self.H, self.ss)
        any_ = False
        # balon bicara
        for b in self.balon:
            t0 = self.when(b)
            t1 = self.when_end(b, "sampai", t0 + 2.5)
            if not (t0 <= t <= t1 + 0.2):
                continue
            a = self.by_id.get(b.get("oleh"))
            q = e_back((t - t0) / 0.3, 2.0) * (1 - e_in(prog(t, t1, t1 + 0.2)))
            if a is None:
                continue
            hx, hy = a.head_world(t)
            sx, sy = self._screen_pt(cam, hx, hy)
            self._balon(S, b, sx, sy, q, t - t0, a)
            any_ = True
        for tk in self.teks:
            t0 = self.when(tk)
            t1 = self.when_end(tk, "sampai", t0 + 2.2)
            if t0 <= t <= t1 + 0.3:
                self._teks(S, tk, t - t0, t1 - t0)
                any_ = True
        return S.finish() if any_ else None

    def _balon(self, S, b, sx, sy, q, tt, a):
        gaya = b.get("gaya", "bicara")
        fs = float(b.get("ukuran", 40))
        teks = b["teks"]
        f = font("teks", fs * S.k)
        maxw = float(b.get("lebar", 560))
        words = teks.split()
        lines, cur = [], ""
        for w in words:
            tst = (cur + " " + w).strip()
            if f.getlength(tst) / S.k > maxw and cur:
                lines.append(cur)
                cur = w
            else:
                cur = tst
        lines.append(cur)
        tw = max(f.getlength(l) for l in lines) / S.k
        pad = 30
        bw, bh = tw + pad * 2, len(lines) * fs * 1.22 + pad * 1.6
        sd = b.get("sisi", "auto")
        if sd == "auto":
            sd = "kanan" if sx < self.W / 2 else "kiri"
        cx = sx + (bw / 2 * 0.55 if sd == "kanan" else -bw / 2 * 0.55)
        cy = sy - bh / 2 - 46
        cx = clamp(cx, bw / 2 + 40, self.W - bw / 2 - 40)
        cy = clamp(cy, bh / 2 + 40, self.H - bh / 2 - 220)
        if q <= 0.01:
            return
        sc = q
        w2, h2 = bw / 2 * sc, bh / 2 * sc
        fill = PUTIH
        if gaya == "teriak":
            n = 14
            pts = []
            for i in range(n * 2):
                ang = math.pi * 2 * i / (n * 2)
                r = 1.0 if i % 2 == 0 else 0.78
                pts.append((cx + math.cos(ang) * (w2 * 1.12) * r, cy + math.sin(ang) * (h2 * 1.28) * r))
            S.poly(pts, (255, 240, 150), 5, OUT)
        elif gaya == "pikir":
            S.ell(cx, cy, w2, h2, fill, 5, OUT)
            for i, (dx, dy, r) in enumerate(((0.0, 1.0, 13), (-0.14, 1.28, 9), (-0.26, 1.5, 6))):
                S.ell(sx - 30 * (1 if sd == "kanan" else -1) * 0 + (cx - sx) * (0.0) + (sx + (cx - sx) * (0.28 - 0.1 * i)), cy + h2 + 26 + i * 24, r * sc, r * sc, fill, 4, OUT)
        else:
            S.rect(cx - w2, cy - h2, cx + w2, cy + h2, fill, 5, OUT, r=min(h2, 40 * sc))
            tx = clamp(sx + (18 if sd == "kanan" else -18), cx - w2 + 40, cx + w2 - 40)
            S.poly([(tx - 18 * sc, cy + h2 - 3), (tx + 18 * sc, cy + h2 - 3), (sx + (6 if sd == "kanan" else -6), min(sy - 20, cy + h2 + 52))], fill, 0)
            S.line([(tx - 18 * sc, cy + h2 + 1), (sx + (6 if sd == "kanan" else -6), min(sy - 20, cy + h2 + 52)), (tx + 18 * sc, cy + h2 + 1)], OUT, 5)
            S.line([(tx - 16 * sc, cy + h2 - 2), (tx + 16 * sc, cy + h2 - 2)], fill, 7, False)
        if sc > 0.6:
            col = tuple(b["warna"]) if isinstance(b.get("warna"), list) else (OUT if not b.get("warna") else TK.warna(b["warna"], OUT))
            y0 = cy - (len(lines) - 1) * fs * 1.22 / 2
            nchar = int(len(teks) * clamp(tt / max(0.4, 0.045 * len(teks)))) if b.get("ketik", True) else len(teks)
            used = 0
            for i, l in enumerate(lines):
                part = l[:max(0, nchar - used)]
                used += len(l) + 1
                if part:
                    S.text(cx, y0 + i * fs * 1.22, l if nchar >= used - 1 else part, fs * sc, col, "teks", "mm" if nchar >= used - 1 else "lm") if False else S.text(cx, y0 + i * fs * 1.22, l, fs * sc, col, "teks", "mm") if nchar >= used - 1 else self._ketik(S, cx, y0 + i * fs * 1.22, l, part, fs * sc, col)

    def _ketik(self, S, cx, y, full, part, size, col):
        f = font("teks", size * S.k)
        wfull = f.getlength(full) / S.k
        S.text(cx - wfull / 2, y, part, size, col, "teks", "lm")

    def _teks(self, S, tk, tt, dur):
        gaya = tk.get("gaya", "judul")
        isi = tk["isi"]
        pos = tk.get("posisi", "atas")
        W, H = self.W, self.H
        if isinstance(pos, (list, tuple)):
            px, py = pos[0] * W, pos[1] * H
        else:
            px, py = {"atas": (W / 2, H * 0.14), "tengah": (W / 2, H * 0.45), "bawah": (W / 2, H * 0.68), "kiri_atas": (W * 0.2, H * 0.09), "kanan_atas": (W * 0.8, H * 0.09)}.get(pos, (W / 2, H * 0.14))
        q = e_back(tt / 0.35, 2.0) * (1 - e_in(prog(tt, dur, dur + 0.3)))
        if q <= 0.01:
            return
        size = float(tk.get("ukuran", 62 if gaya in ("judul", "pil") else 150))
        col = TK.warna(tk.get("warna"), BIRU) if tk.get("warna") else (BIRU if gaya == "judul" else PUTIH)
        if gaya in ("judul", "pil", "kapsul"):
            f = font("judul", size * S.k)
            tw = f.getlength(isi) / S.k
            padx, pady = size * .8, size * .5
            w2, h2 = (tw / 2 + padx) * q, (size * .62 + pady * .5) * q
            if gaya == "kapsul":
                S.rect(px - w2, py - h2, px + w2, py + h2, PUTIH, 5, OUT, r=h2)
                S.text(px, py + 2, isi, size * q, OUT, "judul")
            else:
                S.rect(px - w2 + 5, py - h2 + 7, px + w2 + 5, py + h2 + 7, (0, 0, 0, 40), 0, r=h2)
                S.rect(px - w2, py - h2, px + w2, py + h2, col, 0, r=h2)
                S.text(px, py + 2, isi, size * q, PUTIH, "judul")
        elif gaya == "seru":
            tx = font("seru", size * S.k)
            bb = tx.getbbox(isi)
            wpx, hpx = int((bb[2] - bb[0]) + 60 * S.k), int((bb[3] - bb[1]) + 60 * S.k)
            lay = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
            dd = ImageDraw.Draw(lay)
            wob = 1 + 0.05 * math.sin(tt * 24)
            dd.text((wpx / 2, hpx / 2), isi, font=tx, fill=col if tk.get("warna") else (255, 206, 60), anchor="mm", stroke_width=int(12 * S.k), stroke_fill=OUT)
            ang = float(tk.get("sudut", -7))
            lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
            k = q * wob
            lay = lay.resize((max(2, int(lay.width * k)), max(2, int(lay.height * k))), Image.BILINEAR)
            S.im.alpha_composite(lay, (int(px * S.k - lay.width / 2), int(py * S.k - lay.height / 2)))
        else:   # kata_besar: teks putih bergaris di tengah
            S.text(px, py, isi, size * q, col if tk.get("warna") else PUTIH, "judul", stroke=10, stroke_fill=OUT)

    # ------------------------------------------------------------ efek layar penuh
    def _fx(self, img, t):
        W, H = self.W, self.H
        for e in self.efek:
            j = e.get("jenis")
            t0 = self.when(e)
            t1 = self.when_end(e, "sampai", t0 + float(e.get("dur", 0.5)))
            if j == "flash" and t0 <= t <= t0 + float(e.get("dur", 0.35)):
                a = int(255 * (1 - (t - t0) / float(e.get("dur", 0.35))) * float(e.get("kuat", 0.9)))
                img = Image.alpha_composite(img.convert("RGBA"), Image.new("RGBA", img.size, (255, 255, 255, a))).convert("RGB")
            elif j == "gelap" and t0 <= t <= t1:
                a = int(float(e.get("kuat", 0.45)) * 255 * e_io(prog(t, t0, t0 + 0.4)) * (1 - e_io(prog(t, t1 - 0.4, t1))))
                img = Image.alpha_composite(img.convert("RGBA"), Image.new("RGBA", img.size, (10, 12, 40, a))).convert("RGB")
            elif j == "vinyet" and t0 <= t <= t1:
                img = vignette(img, float(e.get("kuat", 0.55)) * e_io(prog(t, t0, t0 + 0.5)))
            elif j == "garis_kecepatan" and t0 <= t <= t1:
                img = speed_lines(img, t - t0, float(e.get("kuat", 1.0)))
            elif j in ("hujan", "salju", "konfeti") and t0 <= t <= t1:
                img = particles(img, j, t, self.idx)
            elif j == "bar" and t0 <= t <= t1:
                q = e_io(prog(t, t0, t0 + 0.5)) * (1 - e_io(prog(t, t1 - 0.5, t1)))
                bh = int(H * 0.09 * q)
                d = ImageDraw.Draw(img)
                d.rectangle([0, 0, W, bh], fill=(0, 0, 0))
                d.rectangle([0, H - bh, W, H], fill=(0, 0, 0))
            elif j == "zoom_warna" and t0 <= t <= t1:
                pass
        return img

    # ------------------------------------------------------------ audio events
    def events(self):
        ev = []
        for a in self.actors:
            if a.t_in is not None and a.in_style:
                g = a.in_style[0]
                ev.append((self.start + a.t_in, "pop" if g == "pop" else ("boing" if g in ("jatuh", "lompat") else "step_a"), 0.8))
            for m in a.moves:
                if m["gaya"] in ("jalan", "lari"):
                    dist = abs(m["x1"] - m["x0"])
                    n = int(dist / 78.0 * (1.0 if m["gaya"] == "jalan" else 1.15))
                    for i in range(1, n + 1):
                        ph = i * math.pi
                        # waktu saat jarak tempuh = i*78*... (invers kasar easing)
                        frac = (i * 78.0 / (1.0 if m["gaya"] == "jalan" else 1.15)) / max(dist, 1)
                        tt = m["t0"] + (m["t1"] - m["t0"]) * clamp(frac)
                        if tt < m["t1"] and i % 1 == 0:
                            ev.append((self.start + tt, "langkah", 0.5))
                if m["gaya"] == "lompat":
                    ev.append((self.start + m["t0"], "boing", 0.8))
            for ic in a.icons:
                kind = {"tanda_seru": "ding", "seru": "ding", "tanya": "tanya", "hati": "sparkle", "bohlam": "sparkle", "kilau": "sparkle", "bintang": "sparkle", "zzz": "zzz", "keringat": "pop"}.get(ic["jenis"], "pop")
                ev.append((self.start + ic["t0"], kind, 0.8))
        for sg in self.cam_segs:
            if sg["jenis"] == "whip":
                ev.append((self.start + sg["t0"], "whoosh", 1.0))
            elif sg["jenis"] in ("terbang", "zoom_cepat") or (sg["t1"] - sg["t0"] > 0.2 and sg["p1"].z / max(sg["p0"].z, 1e-3) > 1.5):
                ev.append((self.start + sg["t0"], "whoosh_lembut", 0.7))
        for (t0, k, d) in self.punches:
            ev.append((self.start + t0, "thud", 0.8))
        for (t0, amp, d) in self.shakes:
            ev.append((self.start + t0, "thud", 1.0))
        for b in self.balon:
            ev.append((self.start + self.when(b), "pop", 0.5))
        for tk in self.teks:
            g = tk.get("gaya", "judul")
            ev.append((self.start + self.when(tk), "seru" if g == "seru" else "tik", 0.7))
        for p in self.props:
            if p["jenis"] in ("weker",) and p.get("alarm"):
                ev.append((self.start + self.when(p), "alarm", 1.0))
            else:
                ev.append((self.start + self.when(p), "pop", 0.6))
        for e in self.efek:
            if e.get("jenis") == "flash":
                ev.append((self.start + self.when(e), "kilat", 0.8))
        if self.opts.get("alarm"):
            ev.append((self.start + 0.2, "alarm", 1.0))
        for x in self.s.get("sfx", []):
            ev.append((self.start + self.when(x), x["jenis"], float(x.get("gain", 1.0))))
        return ev


# =================================================================== util gambar
def np_mean(v):
    return sum(v) / len(v)


def motion_blur(img, r):
    """Blur gerak horizontal (kotak selebar 2r+1) lewat jumlah kumulatif: cepat dan mulus."""
    import numpy as np
    r = int(r)
    if r < 2:
        return img
    x = np.asarray(img, dtype=np.float32)
    pad = np.pad(x, ((0, 0), (r + 1, r), (0, 0)), mode="edge")
    cs = np.cumsum(pad, axis=1)
    out = (cs[:, 2 * r + 1:, :] - cs[:, :-(2 * r + 1), :]) / (2 * r + 1)
    return Image.fromarray(np.clip(out[:, :x.shape[1]], 0, 255).astype("uint8"))


_VIG = {}


def vignette(img, k):
    key = (img.size,)
    if key not in _VIG:
        w, h = img.size
        small = Image.new("L", (64, 36))
        px = small.load()
        for y in range(36):
            for x in range(64):
                dx, dy = (x - 31.5) / 31.5, (y - 17.5) / 17.5
                px[x, y] = int(255 * clamp((math.hypot(dx, dy) - 0.55) / 0.95) ** 1.6)
        _VIG[key] = small.resize((w, h), Image.BILINEAR)
    mask = _VIG[key].point(lambda v: int(v * clamp(k)))
    dark = Image.new("RGB", img.size, (14, 14, 28))
    return Image.composite(dark, img, mask)


def speed_lines(img, t, k):
    w, h = img.size
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = w / 2, h / 2
    n = 46
    for i in range(n):
        a = (i / n) * 2 * math.pi + (math.floor(t * 18) * 0.37)
        r0 = (0.34 + 0.12 * ((i * 7) % 5) / 5) * h
        r1 = 1.4 * h
        wd = 0.012 + 0.01 * ((i * 3) % 4) / 4
        p0 = (cx + math.cos(a - wd) * r0, cy + math.sin(a - wd) * r0)
        p1 = (cx + math.cos(a + wd) * r0, cy + math.sin(a + wd) * r0)
        p2 = (cx + math.cos(a) * r1, cy + math.sin(a) * r1)
        d.polygon([p0, p1, p2], fill=(24, 24, 34, int(210 * k)))
    return Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")


def particles(img, kind, t, seed):
    w, h = img.size
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    n = {"hujan": 90, "salju": 70, "konfeti": 80}[kind]
    for i in range(n):
        r1 = ((i * 2654435761 + seed * 977) % 10007) / 10007
        r2 = ((i * 40503 + seed * 131) % 9973) / 9973
        sp = 0.5 + r2
        if kind == "hujan":
            x = (r1 * w * 1.2 + t * 120) % (w * 1.2) - w * 0.1
            y = ((r2 + t * (1.6 + sp)) % 1.0) * h
            d.line([(x, y), (x - 14, y + 44)], fill=(120, 170, 230, 200), width=3)
        elif kind == "salju":
            x = (r1 * w + math.sin(t * 1.3 + i) * 30) % w
            y = ((r2 + t * 0.12 * sp) % 1.0) * h
            rr = 4 + (i % 4) * 2
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, 235))
        else:
            x = (r1 * w + math.sin(t * 2 + i) * 40) % w
            y = ((r2 + t * 0.25 * sp) % 1.0) * h
            col = [PINK, KUNING, BIRU_MUDA, HIJAU_MUDA, ORANYE, UNGU][i % 6]
            d.rectangle([x - 8, y - 5, x + 8, y + 5], fill=col + (240,))
    return Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")
