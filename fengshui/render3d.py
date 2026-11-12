"""
Möbel als einfache 3D-Modelle perspektivisch richtig in ein Zimmerfoto zeichnen.

Die Vermessung (foto3d.py) kennt Boden, Wände und Kamera. Darum lässt sich jeder Punkt im Grundriss
(x, y, Höhe) exakt auf einen Bildpunkt abbilden. Dieses Modul

  1. baut jedes Möbel aus Quadern, Zylindern und Kugeln in ECHTEN Maßen (Meter) auf,
  2. projiziert die Flächen ins Foto und malt sie mit einem Tiefenpuffer (z-Buffer: was näher an der
     Kamera ist, verdeckt, was weiter weg ist),
  3. ergänzt weiche Schatten am Boden und den Schein der Lampen.

Das Ergebnis ist eine maßstabsgetreue 3D-Skizze im Foto – kein Foto-Realismus. Dafür stimmt jedes Möbel
in Größe und Position mit dem Grundriss und der Einkaufsliste überein.
"""
from __future__ import annotations

import math
import zlib
from typing import Optional

import numpy as np

from .modell import Layout, Moebel

NAH = 0.12                      # nähere Flächen werden abgeschnitten (Kamera steht fast im Möbel)
WEISS = (246, 243, 237)
DUNKEL = (58, 54, 50)


def _f(farbe, faktor: float) -> tuple[int, int, int]:
    return tuple(int(max(0, min(255, c * faktor))) for c in farbe)


def _mix(a, b, t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


class Lokal:
    """Koordinaten relativ zum Möbel: u = nach rechts, w = nach vorne (Blickrichtung)."""

    def __init__(self, m: Moebel):
        self.m = m
        fx, fy = m.vorne
        self.f, self.r = (fx, fy), (fy, -fx)

    def p(self, u: float, w: float) -> tuple[float, float]:
        return (self.m.x + self.r[0] * u + self.f[0] * w, self.m.y + self.r[1] * u + self.f[1] * w)

    def box(self, u1, u2, w1, w2) -> tuple[float, float, float, float]:
        a, b = self.p(u1, w1), self.p(u2, w2)
        return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


class Szene:
    """Sammelt Dreiecke (Raumkoordinaten x, y, Höhe) samt Farbe und Flächennormale."""

    def __init__(self):
        self.punkte: list = []      # je Dreieck 3×3
        self.farben: list = []
        self.normalen: list = []
        self.art: list = []         # 1 = flach am Boden (Teppich), 2 = Körper, 3 = leuchtet selbst
        self.schatten: list = []    # Grundflächen (Liste von (x, y)) für weiche Bodenschatten
        self.lichter: list = []     # (x, y, h, radius_m)
        self.marken: dict = {}      # Möbelname -> (x, y, h) für die Nummer im Bild

    # ---------------------------------------------------------------- Grundformen
    def flaeche(self, pts, farbe, normale, art: int = 2) -> None:
        for i in range(1, len(pts) - 1):
            self.punkte.append((pts[0], pts[i], pts[i + 1]))
            self.farben.append(farbe)
            self.normalen.append(normale)
            self.art.append(art)

    def quader(self, x1, y1, x2, y2, h1, h2, farbe, art: int = 2) -> None:
        if x2 - x1 <= 0 or y2 - y1 <= 0 or h2 - h1 <= 0:
            return
        a, b, c, d = (x1, y1), (x2, y1), (x2, y2), (x1, y2)
        self.flaeche([(*a, h2), (*b, h2), (*c, h2), (*d, h2)], farbe, (0, 0, 1), art)
        self.flaeche([(*a, h1), (*b, h1), (*c, h1), (*d, h1)], farbe, (0, 0, -1), art)
        for (p, q), n in (((a, b), (0, -1, 0)), ((b, c), (1, 0, 0)), ((c, d), (0, 1, 0)), ((d, a), (-1, 0, 0))):
            self.flaeche([(*p, h1), (*q, h1), (*q, h2), (*p, h2)], farbe, n, art)

    def teil(self, L: Lokal, u1, u2, w1, w2, h1, h2, farbe, art: int = 2) -> None:
        self.quader(*L.box(u1, u2, w1, w2), h1, h2, farbe, art)

    def zylinder(self, cx, cy, r, h1, h2, farbe, n: int = 20, art: int = 2, r_oben: Optional[float] = None) -> None:
        ro = r if r_oben is None else r_oben
        w = [2 * math.pi * i / n for i in range(n)]
        unten = [(cx + r * math.cos(a), cy + r * math.sin(a), h1) for a in w]
        oben = [(cx + ro * math.cos(a), cy + ro * math.sin(a), h2) for a in w]
        self.flaeche(oben, farbe, (0, 0, 1), art)
        self.flaeche(unten, farbe, (0, 0, -1), art)
        for i in range(n):
            j = (i + 1) % n
            am = (w[i] + math.pi / n)
            self.flaeche([unten[i], unten[j], oben[j], oben[i]], farbe, (math.cos(am), math.sin(am), 0), art)

    def kugel(self, cx, cy, ch, r, farbe, art: int = 2, ringe: int = 5, segmente: int = 10) -> None:
        def pkt(i, j):
            th, ph = math.pi * i / ringe, 2 * math.pi * j / segmente
            return (cx + r * math.sin(th) * math.cos(ph), cy + r * math.sin(th) * math.sin(ph), ch + r * math.cos(th))
        for i in range(ringe):
            for j in range(segmente):
                p = [pkt(i, j), pkt(i + 1, j), pkt(i + 1, j + 1), pkt(i, j + 1)]
                th, ph = math.pi * (i + 0.5) / ringe, 2 * math.pi * (j + 0.5) / segmente
                n = (math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th))
                self.flaeche(p, farbe, n, art)

    def bodenflaeche(self, pts, farbe, h: float = 0.012) -> None:
        self.flaeche([(x, y, h) for x, y in pts], farbe, (0, 0, 1), 1)

    def schatten_rechteck(self, r, rand: float = 0.04) -> None:
        x1, y1, x2, y2 = r
        self.schatten.append([(x1 - rand, y1 - rand), (x2 + rand, y1 - rand), (x2 + rand, y2 + rand), (x1 - rand, y2 + rand)])

    def schatten_kreis(self, cx, cy, r) -> None:
        self.schatten.append([(cx + r * math.cos(2 * math.pi * i / 16), cy + r * math.sin(2 * math.pi * i / 16))
                              for i in range(16)])


# ====================================================================== Möbelmodelle
def _beine(sz: Szene, L: Lokal, b, t, h, dicke=0.05, einzug=0.04, farbe=DUNKEL) -> None:
    for su in (-1, 1):
        for sw in (-1, 1):
            u = su * (b / 2 - einzug - dicke / 2)
            w = sw * (t / 2 - einzug - dicke / 2)
            sz.teil(L, u - dicke / 2, u + dicke / 2, w - dicke / 2, w + dicke / 2, 0, h, farbe)


def _fugen(sz: Szene, L: Lokal, b, t, h1, h2, tueren: int, schubladen: int = 0, farbe=(0, 0, 0)) -> None:
    """Dünne dunkle Linien auf der Front: Türspalten, Schubladen, Griffe."""
    vorn = t / 2
    for i in range(1, tueren):
        u = -b / 2 + b * i / tueren
        sz.teil(L, u - 0.004, u + 0.004, vorn, vorn + 0.006, h1 + 0.02, h2 - 0.02, farbe)
    for i in range(1, schubladen):
        hh = h1 + (h2 - h1) * i / schubladen
        sz.teil(L, -b / 2 + 0.02, b / 2 - 0.02, vorn, vorn + 0.006, hh - 0.004, hh + 0.004, farbe)
    if schubladen:
        for i in range(schubladen):
            hh = h1 + (h2 - h1) * (i + 0.5) / schubladen
            for k in range(tueren):
                u = -b / 2 + b * (k + 0.5) / tueren
                sz.teil(L, u - 0.06, u + 0.06, vorn, vorn + 0.018, hh - 0.008, hh + 0.008, farbe)
    else:
        for i in range(tueren):
            seite = 1 if i % 2 == 0 else -1
            u = -b / 2 + b * (i + 0.5) / tueren + seite * (b / tueren / 2 - 0.05)
            mitte = min(1.05, (h1 + h2) / 2)
            sz.teil(L, u - 0.008, u + 0.008, vorn, vorn + 0.02, mitte - 0.09, mitte + 0.09, farbe)


def _bett(sz, m, f, a):
    L, b, t, h = Lokal(m), m.breite, m.tiefe, max(0.4, m.hoehe)
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, 0.06, 0.28, _f(f, 0.9))                      # Rahmen
    sz.teil(L, -b / 2 + 0.03, b / 2 - 0.03, -t / 2 + 0.08, t / 2 - 0.03, 0.28, h, WEISS)   # Matratze
    sz.teil(L, -b / 2 - 0.02, b / 2 + 0.02, -t / 2, -t / 2 + 0.09, 0.0, 1.05, f)           # Kopfteil
    decke = a.get("textil", (228, 220, 205))
    sz.teil(L, -b / 2 + 0.01, b / 2 - 0.01, -t / 2 + 0.72, t / 2 - 0.02, h, h + 0.07, decke)
    sz.teil(L, -b / 2 + 0.01, b / 2 - 0.01, t / 2 - 0.62, t / 2 - 0.02, h + 0.07, h + 0.09, _f(decke, 0.9))  # Plaid
    n = 2 if b >= 1.3 else 1
    kb = (b - 0.16) / n
    for i in range(n):
        u0 = -b / 2 + 0.08 + i * kb
        sz.teil(L, u0 + 0.03, u0 + kb - 0.03, -t / 2 + 0.14, -t / 2 + 0.6, h, h + 0.13, (252, 250, 246))
    sz.schatten_rechteck(m.rechteck)
    sz.marken[m.name] = (m.x, m.y, h + 0.25)


def _nachttisch(sz, m, f, a):
    if m.rund:
        r = min(m.breite, m.tiefe) / 2
        sz.zylinder(m.x, m.y, r * 0.92, 0.04, m.hoehe - 0.03, f)
        sz.zylinder(m.x, m.y, r, m.hoehe - 0.03, m.hoehe, _f(f, 1.08))
        sz.schatten_kreis(m.x, m.y, r + 0.03)
    else:
        L = Lokal(m)
        sz.teil(L, -m.breite / 2, m.breite / 2, -m.tiefe / 2, m.tiefe / 2, 0.08, m.hoehe, f)
        _fugen(sz, L, m.breite, m.tiefe, 0.08, m.hoehe, 1, 2, _f(f, 0.55))
        sz.schatten_rechteck(m.rechteck)
    sz.marken[m.name] = (m.x, m.y, m.hoehe + 0.1)


def _schrank(sz, m, f, a):
    L, b, t, h = Lokal(m), m.breite, m.tiefe, m.hoehe
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, 0.0, 0.06, _f(f, 0.7))
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, 0.06, h, f)
    _fugen(sz, L, b, t, 0.06, h, max(2, round(b / 0.5)), 0, _f(f, 0.6))
    sz.schatten_rechteck(m.rechteck)
    sz.marken[m.name] = (m.x, m.y, h + 0.05)


def _kommode(sz, m, f, a):
    L, b, t, h = Lokal(m), m.breite, m.tiefe, m.hoehe
    fuss = 0.12
    _beine(sz, L, b, t, fuss, 0.04, 0.03, _f(f, 0.55))
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, fuss, h - 0.025, f)
    sz.teil(L, -b / 2 - 0.01, b / 2 + 0.01, -t / 2, t / 2 + 0.01, h - 0.025, h, _f(f, 1.07))
    if m.typ == "regal":
        _fugen(sz, L, b, t, fuss, h - 0.025, 2, 0, _f(f, 0.55))
    else:
        _fugen(sz, L, b, t, fuss, h - 0.025, 2 if b < 1.3 else 3, 3 if b < 1.3 else 0, _f(f, 0.55))
    sz.schatten_rechteck(m.rechteck)
    sz.marken[m.name] = (m.x, m.y, h + 0.1)


def stuhl(sz: Szene, x, y, rot, farbe, hoch: bool = False, name: str = "") -> None:
    m = Moebel("stuhl", 0.46, 0.48, 1.05 if hoch else 0.85, x=x, y=y, rot=rot)
    L, b, t = Lokal(m), m.breite, m.tiefe
    _beine(sz, L, b, t, 0.43, 0.035, 0.02, DUNKEL)
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, 0.43, 0.49, farbe)
    sz.teil(L, -b / 2 + 0.02, b / 2 - 0.02, -t / 2, -t / 2 + 0.05, 0.49, m.hoehe, _f(farbe, 0.95))
    sz.schatten_rechteck(m.rechteck, 0.01)
    if name:
        sz.marken[name] = (x, y, m.hoehe + 0.08)


def _schreibtisch(sz, m, f, a):
    L, b, t, h = Lokal(m), m.breite, m.tiefe, m.hoehe
    _beine(sz, L, b, t, h - 0.035, 0.045, 0.03, DUNKEL)
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, h - 0.035, h, f)
    sz.schatten_rechteck(m.rechteck, 0.0)
    sz.marken[m.name] = (m.x, m.y, h + 0.12)
    if a.get("stuhl"):
        hx, hy = m.hinten
        sx, sy = m.x + hx * (t / 2 + 0.28), m.y + hy * (t / 2 + 0.28)
        stuhl(sz, sx, sy, m.rot, a["stuhl"], hoch=True, name=a.get("stuhl_name", ""))


def _sofa(sz, m, f, a):
    L, b, t, h = Lokal(m), m.breite, m.tiefe, m.hoehe
    arm = 0.16 if b > 1.0 else 0.12
    hell = _f(f, 1.07)
    sz.teil(L, -b / 2 + 0.03, b / 2 - 0.03, -t / 2 + 0.03, t / 2 - 0.03, 0.0, 0.1, DUNKEL)   # Füße/Sockel
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, 0.1, 0.4, f)
    sz.teil(L, -b / 2, b / 2, -t / 2, -t / 2 + 0.2, 0.4, h, f)                               # Rückenlehne
    for s in (-1, 1):
        u1, u2 = sorted((s * b / 2, s * (b / 2 - arm)))
        sz.teil(L, u1, u2, -t / 2, t / 2, 0.4, 0.62, f)
    n = 1 if b < 1.2 else (2 if b < 1.9 else 3)
    innen = b - 2 * arm
    for i in range(n):
        u0 = -innen / 2 + i * innen / n
        sz.teil(L, u0 + 0.008, u0 + innen / n - 0.008, -t / 2 + 0.2, t / 2 - 0.01, 0.4, 0.49, hell)
        sz.teil(L, u0 + 0.02, u0 + innen / n - 0.02, -t / 2 + 0.2, -t / 2 + 0.34, 0.49, h - 0.06, hell)
    akzent = a.get("akzent")
    if akzent and m.typ == "sofa":
        sz.teil(L, -innen / 2 + 0.04, -innen / 2 + 0.42, -t / 2 + 0.34, -t / 2 + 0.46, 0.49, 0.85, akzent)
    sz.schatten_rechteck(m.rechteck)
    sz.marken[m.name] = (m.x, m.y, h + 0.12)


def _tisch(sz, m, f, a):
    L, b, t, h = Lokal(m), m.breite, m.tiefe, m.hoehe
    if m.rund:
        r = min(b, t) / 2
        sz.zylinder(m.x, m.y, r, h - 0.04, h, f, n=28)
        sz.zylinder(m.x, m.y, 0.07 if h < 0.6 else 0.09, 0.03, h - 0.04, _f(f, 0.8), n=12)
        sz.zylinder(m.x, m.y, r * 0.5, 0.0, 0.03, _f(f, 0.8), n=20)
        sz.schatten_kreis(m.x, m.y, r * 0.95)
    else:
        _beine(sz, L, b, t, h - 0.04, 0.06, 0.05, _f(f, 0.8))
        sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, h - 0.04, h, f)
        sz.schatten_rechteck(m.rechteck, 0.0)
    if a.get("schale"):                                  # etwas Lebendiges auf dem Tisch (Obstschale)
        sz.zylinder(m.x, m.y, 0.09, h, h + 0.07, (214, 205, 190), n=14, r_oben=0.16)
        for k, farbe in enumerate([(214, 92, 60), (226, 160, 60), (150, 170, 80)]):
            w = 2.1 * k
            sz.kugel(m.x + 0.06 * math.cos(w), m.y + 0.06 * math.sin(w), h + 0.09, 0.05, farbe, ringe=4, segmente=8)
    sz.marken[m.name] = (m.x, m.y, h + 0.2)


def _tv(sz, m, f, a):
    L, b, t = Lokal(m), m.breite, m.tiefe
    h = min(0.5, m.hoehe)                       # Höhe des Lowboards; m.hoehe zählt den Bildschirm mit
    _beine(sz, L, b, t, 0.1, 0.04, 0.03, DUNKEL)
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, 0.1, h, f)
    _fugen(sz, L, b, t, 0.1, h, 3, 0, _f(f, 0.55))
    sb = min(b * 0.82, 1.1)
    sz.teil(L, -0.15, 0.15, -t / 2 + 0.08, -t / 2 + 0.24, h, h + 0.03, (30, 30, 32))
    sz.teil(L, -sb / 2, sb / 2, -t / 2 + 0.13, -t / 2 + 0.17, h + 0.05, h + 0.05 + sb * 0.56, (26, 27, 30))
    sz.schatten_rechteck(m.rechteck)
    sz.marken[m.name] = (m.x, m.y, h + 0.05 + sb * 0.56 + 0.06)


def _pflanze(sz, m, f, a):
    r = min(m.breite, m.tiefe) / 2
    hoehe = max(0.5, m.hoehe)
    topf = 0.3 if hoehe > 0.8 else 0.22
    sz.zylinder(m.x, m.y, r * 0.5, 0.0, topf, (203, 188, 168), n=16, r_oben=r * 0.62)
    sz.zylinder(m.x, m.y, 0.015, topf, hoehe * 0.6, (96, 120, 70), n=6)
    rng = np.random.default_rng(zlib.crc32(m.name.encode()))
    for i in range(7):
        w, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.0, r * 0.75)
        hh = rng.uniform(topf + 0.12, hoehe - 0.1)
        rr = rng.uniform(0.11, 0.17) * (1.0 if hoehe > 0.8 else 0.8)
        gruen = _f(f, rng.uniform(0.82, 1.18))
        sz.kugel(m.x + d * math.cos(w), m.y + d * math.sin(w), hh, rr, gruen)
    sz.schatten_kreis(m.x, m.y, r)
    sz.marken[m.name] = (m.x, m.y, hoehe + 0.1)


def _stehleuchte(sz, m, f, a):
    h = m.hoehe
    metall = a.get("metall", DUNKEL)
    sz.zylinder(m.x, m.y, 0.13, 0.0, 0.03, metall, n=16)
    if a.get("variante") == "uplight":
        sz.zylinder(m.x, m.y, 0.014, 0.03, h - 0.1, metall, n=6)
        sz.zylinder(m.x, m.y, 0.05, h - 0.1, h, f, n=16, art=3, r_oben=0.15)
        sz.lichter.append((m.x, m.y, h + 0.25, 0.7))
    else:
        sz.zylinder(m.x, m.y, 0.014, 0.03, h - 0.3, metall, n=6)
        sz.zylinder(m.x, m.y, 0.19, h - 0.32, h, f, n=18, art=3, r_oben=0.15)
        sz.lichter.append((m.x, m.y, h - 0.16, 0.55))
    sz.schatten_kreis(m.x, m.y, 0.14)
    sz.marken[m.name] = (m.x, m.y, h + 0.1)


def _tischleuchte(sz, m, f, a, h0: float):
    sz.zylinder(m.x, m.y, 0.055, h0, h0 + 0.2, a.get("fuss", (201, 168, 140)), n=12, r_oben=0.03)
    sz.zylinder(m.x, m.y, 0.13, h0 + 0.2, h0 + 0.4, f, n=16, art=3, r_oben=0.1)
    sz.lichter.append((m.x, m.y, h0 + 0.3, 0.42))
    sz.marken[m.name] = (m.x, m.y, h0 + 0.5)


def _pendelleuchte(sz, m, f, a, raumhoehe: float, h_unten: float):
    r = 0.2
    hk = min(raumhoehe - 0.45, h_unten + 0.85 + r)
    sz.quader(m.x - 0.006, m.y - 0.006, m.x + 0.006, m.y + 0.006, hk + r, raumhoehe, DUNKEL)
    sz.kugel(m.x, m.y, hk, r, f, art=3, ringe=7, segmente=14)
    sz.lichter.append((m.x, m.y, hk, 0.6))
    sz.marken[m.name] = (m.x, m.y, hk + r + 0.08)


def _teppich(sz, m, f, a):
    x1, y1, x2, y2 = m.rechteck
    if m.rund:
        rx, ry = (x2 - x1) / 2, (y2 - y1) / 2
        ring = [(math.cos(2 * math.pi * i / 36), math.sin(2 * math.pi * i / 36)) for i in range(36)]
        sz.bodenflaeche([(m.x + rx * c, m.y + ry * s) for c, s in ring], _f(f, 0.9), 0.010)
        sz.bodenflaeche([(m.x + (rx - 0.12) * c, m.y + (ry - 0.12) * s) for c, s in ring], f, 0.013)
    else:
        sz.bodenflaeche([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], _f(f, 0.9), 0.010)
        e = 0.12
        sz.bodenflaeche([(x1 + e, y1 + e), (x2 - e, y1 + e), (x2 - e, y2 - e), (x1 + e, y2 - e)], f, 0.013)
    sz.marken[m.name] = (x1 + 0.25, y1 + 0.25, 0.02)


def wandhoehe(m: Moebel) -> float:
    """Unterkante eines Wandobjekts über dem Boden (Bilder hängen auf Augenhöhe)."""
    if m.typ == "spiegel" and m.hoehe >= 1.4:
        return 0.2
    return max(0.25, 1.5 - m.hoehe / 2)


def _wandobjekt(sz, m, f, a):
    L, b, t = Lokal(m), m.breite, max(0.03, m.tiefe)
    h1, h2 = wandhoehe(m), wandhoehe(m) + m.hoehe
    rahmen = a.get("rahmen", (88, 70, 54))
    sz.teil(L, -b / 2, b / 2, -t / 2, t / 2, h1, h2, rahmen)
    v1, v2, e = t / 2, t / 2 + 0.004, 0.03
    u1, u2 = -b / 2 + e, b / 2 - e
    g1, g2 = h1 + e, h2 - e

    def streifen(von, bis, farbe, links=0.0, rechts=1.0):
        sz.teil(L, u1 + (u2 - u1) * links, u1 + (u2 - u1) * rechts, v1, v2, g1 + (g2 - g1) * von, g1 + (g2 - g1) * bis,
                farbe, art=3)

    if m.typ == "spiegel":
        streifen(0, 1, (205, 219, 226))
        streifen(0.55, 1.0, (222, 232, 237))
        streifen(0.0, 0.2, (190, 204, 212))
    elif m.typ == "pinnwand":
        streifen(0, 1, f)
        for k, (x, y, farbe) in enumerate([(0.1, 0.55, (250, 248, 240)), (0.42, 0.2, (246, 226, 150)),
                                            (0.68, 0.5, (250, 248, 240)), (0.2, 0.12, (188, 214, 226))]):
            sz.teil(L, u1 + (u2 - u1) * x, u1 + (u2 - u1) * (x + 0.2), v2, v2 + 0.003,
                    g1 + (g2 - g1) * y, g1 + (g2 - g1) * (y + 0.3), farbe, art=3)
    elif a.get("variante") == "froehlich":
        streifen(0, 1, (243, 233, 210))
        streifen(0.0, 0.3, (190, 150, 110))
        for x, farbe in [(0.18, (214, 92, 60)), (0.42, (232, 170, 60)), (0.66, (150, 172, 84))]:
            streifen(0.25, 0.62, farbe, x, x + 0.18)
    else:                                   # ruhige Landschaft: Himmel, Hügel, Wasser
        streifen(0.45, 1.0, (222, 230, 232))
        streifen(0.36, 0.5, (150, 170, 164))
        streifen(0.0, 0.38, (92, 120, 134))
        streifen(0.14, 0.2, (140, 164, 174))
    sz.marken[m.name] = (m.x, m.y, h2 + 0.08)


def vorhang(sz: Szene, raum, fenster, farbe) -> None:
    """Zwei bodenlange Schals links und rechts vom Fenster + Stange."""
    oben = min(raum.hoehe - 0.08, fenster.bruestung + fenster.hoehe + 0.25)
    breit, dick, ab = 0.38, 0.05, 0.03
    L = raum.wandlaenge(fenster.wand)
    bereiche = [(max(0.0, fenster.von - breit + 0.08), fenster.von + 0.08),
                (fenster.bis - 0.08, min(L, fenster.bis + breit - 0.08))]

    def box(s1, s2, d1, d2):
        if fenster.wand == "unten":
            return (s1, d1, s2, d2)
        if fenster.wand == "oben":
            return (s1, raum.tiefe - d2, s2, raum.tiefe - d1)
        if fenster.wand == "links":
            return (d1, s1, d2, s2)
        return (raum.breite - d2, s1, raum.breite - d1, s2)

    for s1, s2 in bereiche:
        falten = max(3, int((s2 - s1) / 0.07))
        for i in range(falten):
            a, b = s1 + (s2 - s1) * i / falten, s1 + (s2 - s1) * (i + 1) / falten
            vor = dick if i % 2 == 0 else dick * 0.55
            sz.quader(*box(a, b, ab, ab + vor), 0.02, oben, _f(farbe, 1.0 if i % 2 == 0 else 0.9))
    s1, s2 = bereiche[0][0] - 0.05, bereiche[1][1] + 0.05
    sz.quader(*box(max(0, s1), min(L, s2), ab + 0.02, ab + 0.045), oben, oben + 0.025, DUNKEL)


def baue_szene(layout: Layout, aussehen: Optional[dict] = None, deko: Optional[list] = None,
               nur: Optional[set] = None) -> Szene:
    """Alle (neuen) Möbel eines Layouts als 3D-Szene. `nur` = Namen der Möbel, die gezeichnet werden sollen."""
    sz = Szene()
    aussehen = aussehen or {}
    nach_name = {m.name: m for m in layout.moebel}
    for m in layout.moebel:
        if nur is not None and m.name not in nur:
            continue
        a = aussehen.get(m.name, {})
        f = a.get("farbe", (190, 180, 165))
        if m.typ == "bett":
            _bett(sz, m, f, a)
        elif m.typ == "nachttisch":
            _nachttisch(sz, m, f, a)
        elif m.typ == "schrank":
            _schrank(sz, m, f, a)
        elif m.typ in ("kommode", "regal", "sideboard", "konsole"):
            _kommode(sz, m, f, a)
        elif m.typ == "schreibtisch":
            _schreibtisch(sz, m, f, a)
        elif m.typ in ("sofa", "sessel"):
            _sofa(sz, m, f, a)
        elif m.typ in ("couchtisch", "esstisch", "beistelltisch"):
            _tisch(sz, m, f, a)
        elif m.typ == "stuhl":
            stuhl(sz, m.x, m.y, m.rot, f, name=m.name)
        elif m.typ == "tv":
            _tv(sz, m, f, a)
        elif m.typ in ("pflanze", "kaktus"):
            _pflanze(sz, m, f, a)
        elif m.typ == "stehleuchte":
            _stehleuchte(sz, m, f, a)
        elif m.typ == "tischleuchte":
            eltern = nach_name.get(m.gehoert_zu or "")
            _tischleuchte(sz, m, f, a, eltern.hoehe if eltern else 0.5)
        elif m.typ == "pendelleuchte":
            eltern = nach_name.get(m.gehoert_zu or "")
            _pendelleuchte(sz, m, f, a, layout.raum.hoehe, eltern.hoehe if eltern else 0.75)
        elif m.typ == "teppich":
            _teppich(sz, m, f, a)
        elif m.ist_wandobjekt:
            _wandobjekt(sz, m, f, a)
        else:                                   # unbekannter Typ: schlichter Quader in echter Größe
            sz.quader(*m.rechteck, 0.0, m.hoehe, f)
            sz.schatten_rechteck(m.rechteck)
            sz.marken[m.name] = (m.x, m.y, m.hoehe + 0.1)
    for d in deko or []:
        if d.get("art") == "vorhang":
            vorhang(sz, layout.raum, d["fenster"], d["farbe"])
    return sz


# ====================================================================== Projektion + z-Buffer
class Projektion:
    """Raumkoordinaten (x, y, Höhe) → Kamera → Pixel, für ganze Punktlisten auf einmal."""

    def __init__(self, v, skala: float = 1.0):
        g, k = v.geometrie, v.kamera
        self.g, self.skala = g, skala
        self.fx, self.fy, self.cx, self.cy = k.fx * skala, k.fy * skala, k.cx * skala, k.cy * skala
        self.B, self.H = int(round(k.breite * skala)), int(round(k.hoehe * skala))

    def kamera(self, P: np.ndarray) -> np.ndarray:
        g = self.g
        r = np.stack([P[..., 0] + g["links"], P[..., 1] + g["unten"]], -1)
        ab = r @ g["rot"].T
        return (ab[..., 0:1] * g["e1"] + ab[..., 1:2] * g["e2"] + (P[..., 2:3] - g["d"]) * g["n"])

    def pixel(self, X: np.ndarray) -> np.ndarray:
        z = X[..., 2]
        return np.stack([self.fx * X[..., 0] / z + self.cx, self.fy * X[..., 1] / z + self.cy], -1)

    def punkt(self, x, y, h) -> Optional[tuple[float, float, float]]:
        X = self.kamera(np.array([[x, y, h]], float))[0]
        if X[2] <= NAH:
            return None
        u, v_ = self.pixel(X[None])[0]
        return float(u), float(v_), float(X[2])


def _nah_abschneiden(tri: np.ndarray) -> list[np.ndarray]:
    """Dreieck (Kamerakoordinaten) an der Ebene z = NAH abschneiden → 0, 1 oder 2 Dreiecke."""
    innen = tri[:, 2] >= NAH
    if innen.all():
        return [tri]
    if not innen.any():
        return []
    poly = []
    for i in range(3):
        a, b = tri[i], tri[(i + 1) % 3]
        if innen[i]:
            poly.append(a)
        if innen[i] != innen[(i + 1) % 3]:
            s = (NAH - a[2]) / (b[2] - a[2])
            poly.append(a + s * (b - a))
    return [np.array([poly[0], poly[i], poly[i + 1]]) for i in range(1, len(poly) - 1)]


def _lichtrichtung(raum) -> np.ndarray:
    """Licht kommt vom (ersten) Fenster schräg von oben – sonst einfach von oben vorne."""
    f = raum.fenster[0] if raum.fenster else None
    if f is not None:
        fx, fy = f.mitte(raum)
        l = np.array([fx - raum.breite / 2, fy - raum.tiefe / 2, 0.0])
        n = np.linalg.norm(l)
        l = l / n if n > 1e-6 else np.array([0.3, 0.3, 0.0])
        l = l * 0.75 + np.array([0, 0, 0.66])
    else:
        l = np.array([0.35, 0.25, 0.9])
    return l / np.linalg.norm(l)


def rastern(sz: Szene, pr: Projektion, raum, helligkeit: float = 1.0, stich=(1.0, 1.0, 1.0)):
    """Zeichnet alle Dreiecke mit Tiefenpuffer. Rückgabe: Farbe (H,W,3), Tiefe (H,W), Art (H,W)."""
    H, W = pr.H, pr.B
    farbe = np.zeros((H, W, 3), np.float32)
    tiefe = np.full((H, W), np.inf, np.float64)
    art = np.zeros((H, W), np.uint8)
    if not sz.punkte:
        return farbe, tiefe, art
    P = np.array(sz.punkte, float)                    # (M, 3, 3)
    X = pr.kamera(P)
    licht = _lichtrichtung(raum)
    N = np.array(sz.normalen, float)
    schattierung = 0.6 + 0.26 * np.clip(N @ licht, 0, None) + 0.14 * np.clip(N[:, 2], 0, None)
    stich = np.array(stich, np.float32)
    for i in range(len(P)):
        if sz.art[i] == 3:
            c = np.array(sz.farben[i], np.float32)
        else:
            c = np.clip(np.array(sz.farben[i], np.float32) * schattierung[i] * helligkeit * stich, 0, 255)
        for tri in _nah_abschneiden(X[i]):
            px = pr.pixel(tri)
            z = tri[:, 2]
            x0, x1 = int(max(0, math.floor(px[:, 0].min()))), int(min(W - 1, math.ceil(px[:, 0].max())))
            y0, y1 = int(max(0, math.floor(px[:, 1].min()))), int(min(H - 1, math.ceil(px[:, 1].max())))
            if x1 < x0 or y1 < y0:
                continue
            (ax, ay), (bx, by), (cx_, cy_) = px
            nenner = (by - cy_) * (ax - cx_) + (cx_ - bx) * (ay - cy_)
            if abs(nenner) < 1e-9:
                continue
            xs = np.arange(x0, x1 + 1) + 0.5
            ys = (np.arange(y0, y1 + 1) + 0.5)[:, None]
            w0 = ((by - cy_) * (xs - cx_) + (cx_ - bx) * (ys - cy_)) / nenner
            w1 = ((cy_ - ay) * (xs - cx_) + (ax - cx_) * (ys - cy_)) / nenner
            w2 = 1.0 - w0 - w1
            innen = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not innen.any():
                continue
            zz = 1.0 / (w0 / z[0] + w1 / z[1] + w2 / z[2])        # perspektivisch richtige Tiefe
            ausschnitt = tiefe[y0:y1 + 1, x0:x1 + 1]
            neu = innen & (zz < ausschnitt)
            if not neu.any():
                continue
            ausschnitt[neu] = zz[neu]
            farbe[y0:y1 + 1, x0:x1 + 1][neu] = c
            art[y0:y1 + 1, x0:x1 + 1][neu] = sz.art[i]
    return farbe, tiefe, art


def zeichne_ins_foto(rgb: np.ndarray, v, layout: Layout, aussehen: Optional[dict] = None,
                     deko: Optional[list] = None, nur: Optional[set] = None, max_seite: int = 1600,
                     ueberabtastung: int = 2) -> dict:
    """Zeichnet die Möbel ins Foto.

    Rückgabe: {"bild": Foto mit Möbeln (uint8), "foto": verkleinertes Originalfoto, "tiefe": Tiefenkarte der
    eingerichteten Szene in Metern, "maske": wo Möbel sind (0..1), "projektion": Projektion, "szene": Szene}
    """
    from PIL import Image, ImageDraw, ImageFilter

    H0, W0 = rgb.shape[:2]
    s = min(1.0, max_seite / max(H0, W0))
    W, H = int(round(W0 * s)), int(round(H0 * s))
    foto = np.asarray(Image.fromarray(rgb).resize((W, H), Image.LANCZOS)).astype(np.float32)

    # Helligkeit und Farbstich der Möbel ans Foto anpassen
    mittel = foto.reshape(-1, 3).mean(0)
    helligkeit = float(np.clip(mittel.mean() / 165.0, 0.72, 1.05))
    stich = np.clip(mittel / max(1.0, mittel.mean()), 0.92, 1.08)

    sz = baue_szene(layout, aussehen, deko, nur)
    ss = max(1, int(ueberabtastung))
    pr_gross = Projektion(v, s * ss)
    pr_gross.B, pr_gross.H = W * ss, H * ss
    farbe, tiefe, art = rastern(sz, pr_gross, layout.raum, helligkeit, stich)

    # Vorhandene Möbel im Foto verdecken neue Möbel, die dahinter stehen
    if getattr(v, "masken", None) and getattr(v, "tiefe", None) is not None:
        vorn = np.zeros((H0, W0), bool)
        for e, m in zip(v.erkennungen, v.masken):
            if e.typ not in ("tuer", "fenster", "teppich", "bild", "spiegel", "uhr", "wandregal"):
                vorn |= m
        if vorn.any():
            yy = np.clip((np.arange(H * ss) / (s * ss)).astype(int), 0, H0 - 1)
            xx = np.clip((np.arange(W * ss) / (s * ss)).astype(int), 0, W0 - 1)
            sperre = np.where(vorn, v.tiefe, np.inf)[yy][:, xx]
            verdeckt = tiefe > sperre + 0.1
            tiefe[verdeckt] = np.inf
            art[verdeckt] = 0

    # von der Überabtastung auf Bildgröße mitteln (glatte Kanten)
    da = (art > 0).astype(np.float32)
    fest = (art >= 2).astype(np.float32)

    def mitteln(a):
        return a.reshape(H, ss, W, ss, *a.shape[2:]).mean((1, 3))

    alpha = mitteln(da)
    alpha_fest = mitteln(fest)
    summe = mitteln(farbe * da[..., None])
    farbe_klein = np.where(alpha[..., None] > 1e-6, summe / np.maximum(alpha[..., None], 1e-6), 0)
    tiefe_klein = tiefe[ss // 2::ss, ss // 2::ss]

    bild = foto * (1 - alpha[..., None]) + farbe_klein * alpha[..., None]

    # weiche Schatten am Boden (auch auf dem Teppich, nicht auf den Möbeln selbst)
    pr = Projektion(v, s)
    pr.B, pr.H = W, H
    sch = Image.new("L", (W, H), 0)
    zeichner = ImageDraw.Draw(sch)
    for poly in sz.schatten:
        X = pr.kamera(np.array([(x, y, 0.0) for x, y in poly], float))
        if (X[:, 2] < NAH).any():
            continue
        zeichner.polygon([tuple(p) for p in pr.pixel(X)], fill=255)
    weit = np.asarray(sch.filter(ImageFilter.GaussianBlur(max(2.0, W * 0.012))), np.float32) / 255
    eng = np.asarray(sch.filter(ImageFilter.GaussianBlur(max(1.0, W * 0.004))), np.float32) / 255
    dunkel = (0.20 * weit + 0.20 * eng) * (1 - alpha_fest)
    bild = bild * (1 - dunkel[..., None])

    # Lampenschein
    yy, xx = np.mgrid[0:H, 0:W]
    for (x, y, h, radius) in sz.lichter:
        p = pr.punkt(x, y, h)
        if p is None:
            continue
        u, vv, z = p
        rpx = pr.fx * radius / z
        if rpx < 2 or not (-rpx < u < W + rpx and -rpx < vv < H + rpx):
            continue
        if not punkt_sichtbar(pr, tiefe_klein, (x, y, h), nur_im_bild=False, toleranz=0.35):
            continue                                    # Lampe steht hinter einem anderen Möbel
        x0, x1 = int(max(0, u - 2 * rpx)), int(min(W, u + 2 * rpx))
        y0, y1 = int(max(0, vv - 2 * rpx)), int(min(H, vv + 2 * rpx))
        d2 = (xx[y0:y1, x0:x1] - u) ** 2 + (yy[y0:y1, x0:x1] - vv) ** 2
        schein = np.exp(-d2 / (2 * (rpx * 0.5) ** 2))[..., None] * np.array([36, 28, 12], np.float32)
        bild[y0:y1, x0:x1] += schein

    bild = np.clip(bild, 0, 255).astype(np.uint8)
    return {"bild": bild, "foto": foto.astype(np.uint8), "tiefe": tiefe_klein, "maske": alpha,
            "projektion": pr, "szene": sz}


def punkt_sichtbar(pr: Projektion, tiefe: Optional[np.ndarray], punkt, nur_im_bild: bool = True,
                   toleranz: float = 0.6) -> bool:
    """Liegt der Raumpunkt (x, y, h) im Bild und nicht hinter einem anderen gezeichneten Möbel?"""
    p = pr.punkt(*punkt)
    if p is None:
        return False
    u, vv, z = p
    drin = 0 <= u < pr.B and 0 <= vv < pr.H
    if not drin:
        return not nur_im_bild
    if tiefe is not None and tiefe[int(vv), int(u)] < z - toleranz:
        return False
    return True


def moebel_sichtbar(pr: Projektion, tiefe: Optional[np.ndarray], sz: Szene, m: Moebel) -> bool:
    """Ist das Möbel im Ergebnisbild zu sehen? Geprüft an Marke, Mitte und den vier Ecken."""
    punkte = []
    if m.name in sz.marken:
        punkte.append(sz.marken[m.name])
    x1, y1, x2, y2 = m.rechteck
    h = sz.marken[m.name][2] if m.name in sz.marken else m.hoehe
    h = max(0.02, h - 0.1)
    punkte += [(m.x, m.y, h), (x1, y1, h), (x2, y1, h), (x2, y2, h), (x1, y2, h)]
    return any(punkt_sichtbar(pr, tiefe, p) for p in punkte)


def beschrifte(bild: np.ndarray, pr: Projektion, sz: Szene, nummern: dict[str, int],
               tiefe: Optional[np.ndarray] = None) -> np.ndarray:
    """Setzt die Nummern der Einkaufsliste als runde Marken an die Möbel."""
    from PIL import Image, ImageDraw
    from .foto_korrektur import _schrift

    img = Image.fromarray(bild).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    r = max(13, W // 85)
    schrift = _schrift(int(r * 1.15))
    gesetzt: list[tuple[float, float]] = []
    for name, nr in sorted(nummern.items(), key=lambda kv: kv[1]):
        if name not in sz.marken:
            continue
        p = pr.punkt(*sz.marken[name])
        if p is None:
            continue
        u, vv, _ = p
        if not (r < u < W - r and r < vv < H - r):
            continue
        if not punkt_sichtbar(pr, tiefe, sz.marken[name]):
            continue                                    # verdeckt → keine Marke (steht in den Hinweisen)
        for _ in range(8):                              # Überlappungen der Marken auflösen
            if all(math.hypot(u - a, vv - b) > 2.1 * r for a, b in gesetzt):
                break
            vv -= 1.2 * r
        vv = max(r + 2, vv)
        gesetzt.append((u, vv))
        d.ellipse((u - r, vv - r, u + r, vv + r), fill=(122, 92, 58, 235), outline=(255, 255, 255, 255), width=2)
        d.text((u, vv), str(nr), fill=(255, 255, 255, 255), font=schrift, anchor="mm")
    return np.asarray(img)
