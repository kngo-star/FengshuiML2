"""Geometrische Hilfsfunktionen für die Regelprüfung."""
from __future__ import annotations

import math
from collections import deque
from typing import Iterable, Optional

from .modell import (FLACH, VEKTOR_WAND, WAND_NORMALE, Layout, Moebel, Oeffnung, Raum)

Rect = tuple[float, float, float, float]
Punkt = tuple[float, float]


# ---------------------------------------------------------------- Rechtecke
def ueberlappung(a: Rect, b: Rect, toleranz: float = 1e-6) -> float:
    """Überlappungsfläche zweier Rechtecke."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= toleranz or h <= toleranz:
        return 0.0
    return w * h


def abstand_rechtecke(a: Rect, b: Rect) -> float:
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


def abstand_punkt_rechteck(p: Punkt, r: Rect) -> float:
    dx = max(r[0] - p[0], 0.0, p[0] - r[2])
    dy = max(r[1] - p[1], 0.0, p[1] - r[3])
    return math.hypot(dx, dy)


def im_raum(m: Moebel, raum: Raum, toleranz: float = 1e-6) -> bool:
    x1, y1, x2, y2 = m.rechteck
    return x1 >= -toleranz and y1 >= -toleranz and x2 <= raum.breite + toleranz and y2 <= raum.tiefe + toleranz


def ecken(r: Rect) -> list[Punkt]:
    return [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]


# ---------------------------------------------------------------- Wände
def abstand_zur_wand(m: Moebel, raum: Raum, richtung: tuple[int, int]) -> float:
    """Abstand der Möbelkante in `richtung` zur Wand in dieser Richtung."""
    x1, y1, x2, y2 = m.rechteck
    if richtung == (0, -1):
        return y1
    if richtung == (0, 1):
        return raum.tiefe - y2
    if richtung == (-1, 0):
        return x1
    return raum.breite - x2


def spanne_quer(m: Moebel, richtung: tuple[int, int]) -> tuple[float, float]:
    """Ausdehnung des Möbels entlang einer Wand, die in `richtung` liegt."""
    x1, y1, x2, y2 = m.rechteck
    if richtung[1] != 0:      # Wand unten/oben -> entlang x
        return x1, x2
    return y1, y2


def oeffnungen_an_wand(raum: Raum, wand: str, von: float, bis: float,
                       nur: Optional[Iterable[str]] = None) -> list[Oeffnung]:
    """Öffnungen auf `wand`, die das Intervall [von, bis] überlappen."""
    erg = []
    for o in raum.oeffnungen:
        if o.wand != wand:
            continue
        if nur is not None and o.typ not in nur:
            continue
        if min(bis, o.bis) - max(von, o.von) > 0.05:
            erg.append(o)
    return erg


def an_wand(m: Moebel, raum: Raum, toleranz: float = 0.15) -> list[str]:
    """Liste der Wände, die das Möbel (fast) berührt."""
    x1, y1, x2, y2 = m.rechteck
    w = []
    if y1 <= toleranz:
        w.append("unten")
    if raum.tiefe - y2 <= toleranz:
        w.append("oben")
    if x1 <= toleranz:
        w.append("links")
    if raum.breite - x2 <= toleranz:
        w.append("rechts")
    return w


# ---------------------------------------------------------------- Personen-/Blickpunkte
def personenpunkt(m: Moebel) -> Punkt:
    """Wo sich der Kopf/Körper der Person befindet, die das Möbel benutzt."""
    hx, hy = m.hinten
    if m.typ == "bett":
        # Kopf liegt ca. 35 cm vor dem Kopfteil
        halb = m.tiefe / 2 - 0.35
        return (m.x + hx * halb, m.y + hy * halb)
    if m.typ in ("schreibtisch", "esstisch"):
        # Person sitzt ca. 45 cm hinter der Tischkante
        halb = m.tiefe / 2 + 0.45
        return (m.x + hx * halb, m.y + hy * halb)
    return (m.x, m.y)


def rueckenabstand(m: Moebel, raum: Raum) -> float:
    """Abstand zwischen Rücken der Person (bzw. Rückseite des Möbels) und der Wand dahinter."""
    if m.typ in ("schreibtisch",):
        px, py = personenpunkt(m)
        hx, hy = m.hinten
        # Abstand Personenpunkt -> Wand in Rückrichtung, minus Oberkörpertiefe (~0.25)
        if hx == 0:
            d = py if hy < 0 else raum.tiefe - py
        else:
            d = px if hx < 0 else raum.breite - px
        return max(0.0, d - 0.25)
    return abstand_zur_wand(m, raum, m.hinten)


def winkel_zu(punkt: Punkt, blick: tuple[int, int], ziel: Punkt) -> float:
    """Winkel (Grad) zwischen Blickrichtung und Richtung zum Ziel."""
    vx, vy = ziel[0] - punkt[0], ziel[1] - punkt[1]
    n = math.hypot(vx, vy)
    if n < 1e-9:
        return 0.0
    c = (vx * blick[0] + vy * blick[1]) / n
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def sichtlinie_frei(a: Punkt, b: Punkt, hindernisse: list[Rect], schritte: int = 40) -> bool:
    """Prüft, ob die Linie a->b durch keine (hohen) Möbel verläuft."""
    for i in range(1, schritte):
        t = i / schritte
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        for r in hindernisse:
            if r[0] < p[0] < r[2] and r[1] < p[1] < r[3]:
                return False
    return True


# ---------------------------------------------------------------- Türen
def tuer_schwenkbereich(t: Oeffnung, raum: Raum) -> Rect:
    """Fläche, die eine nach innen öffnende Tür beim Aufschwenken braucht."""
    (ax, ay), (bx, by) = t.endpunkte(raum)
    nx, ny = WAND_NORMALE[t.wand]
    tiefe = t.breite
    x1, x2 = min(ax, bx), max(ax, bx)
    y1, y2 = min(ay, by), max(ay, by)
    if nx != 0:
        x2 = x1 + tiefe if nx > 0 else x2
        x1 = x1 if nx > 0 else x1 - tiefe
    else:
        y2 = y1 + tiefe if ny > 0 else y2
        y1 = y1 if ny > 0 else y1 - tiefe
    return (x1, y1, x2, y2)


def punkt_vor_oeffnung(o: Oeffnung, raum: Raum, abstand: float = 0.3) -> Punkt:
    mx, my = o.mitte(raum)
    nx, ny = WAND_NORMALE[o.wand]
    return (mx + nx * abstand, my + ny * abstand)


def in_tuerflucht(m: Moebel, t: Oeffnung, raum: Raum, rand: float = 0.1) -> bool:
    """Liegt das Möbel im 'Strahl', der von der Tür quer durch den Raum geht?"""
    x1, y1, x2, y2 = m.rechteck
    if t.wand in ("unten", "oben"):
        return min(x2, t.bis + rand) - max(x1, t.von - rand) > 0.05
    return min(y2, t.bis + rand) - max(y1, t.von - rand) > 0.05


def schaut_zur_oeffnung(m: Moebel, o: Oeffnung) -> bool:
    """Zeigt die Vorderseite (beim Bett: Fußende) direkt auf diese Öffnung?"""
    wand_vorne = VEKTOR_WAND[m.vorne]
    if o.wand != wand_vorne:
        return False
    a, b = spanne_quer(m, m.vorne)
    return min(b, o.bis) - max(a, o.von) > 0.05


# ---------------------------------------------------------------- Chi-Fluss
GEGENUEBER = {"unten": "oben", "oben": "unten", "links": "rechts", "rechts": "links"}


def chi_korridor(raum: Raum, mit_faktor: bool = False):
    """Konvexe Vierecke zwischen jeder Tür und jeder anderen Öffnung (Fenster/Tür).

    Buch: Chi fließt von Eingang zum Ausgang (Fenster). Liegen beide sich gegenüber,
    schneidet das Chi schnell durch den Raum (Faktor 1.0) – liegen sie über Eck,
    nimmt es einen sanfteren, gebogenen Weg (Faktor 0.5).
    """
    polys = []
    for t in raum.tueren:
        for o in raum.oeffnungen:
            if o is t or o.typ == "schranktuer":
                continue
            if o.wand == t.wand:
                continue
            a1, a2 = t.endpunkte(raum)
            b1, b2 = o.endpunkte(raum)
            faktor = 1.0 if GEGENUEBER[t.wand] == o.wand else 0.5
            poly = _konvexe_huelle([a1, a2, b1, b2])
            polys.append((poly, faktor) if mit_faktor else poly)
    return polys


def _konvexe_huelle(punkte: list[Punkt]) -> list[Punkt]:
    pts = sorted(set(punkte))
    if len(pts) <= 2:
        return pts

    def kreuz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    unten, oben = [], []
    for p in pts:
        while len(unten) >= 2 and kreuz(unten[-2], unten[-1], p) <= 0:
            unten.pop()
        unten.append(p)
    for p in reversed(pts):
        while len(oben) >= 2 and kreuz(oben[-2], oben[-1], p) <= 0:
            oben.pop()
        oben.append(p)
    return unten[:-1] + oben[:-1]


def punkt_in_polygon(p: Punkt, poly: list[Punkt]) -> bool:
    if len(poly) < 3:
        return False
    innen = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > p[1]) != (yj > p[1]):
            xs = (xj - xi) * (p[1] - yi) / (yj - yi + 1e-12) + xi
            if p[0] < xs:
                innen = not innen
        j = i
    return innen


def anteil_im_polygon(r: Rect, poly: list[Punkt], n: int = 6) -> float:
    """Anteil (0..1) eines Rechtecks, der in einem Polygon liegt (Stichproben-Raster)."""
    treffer = 0
    for i in range(n):
        for j in range(n):
            p = (r[0] + (i + 0.5) / n * (r[2] - r[0]), r[1] + (j + 0.5) / n * (r[3] - r[1]))
            if punkt_in_polygon(p, poly):
                treffer += 1
    return treffer / (n * n)


# ---------------------------------------------------------------- Laufwege
def erreichbarkeit(layout: Layout, ziele: list[Punkt], aufloesung: float = 0.1,
                   durchgang: float = 0.6) -> list[bool]:
    """Breitensuche auf einem Raster: Sind die Zielpunkte von der Haupttür aus
    mit einem Durchgang von `durchgang` Metern erreichbar?"""
    raum = layout.raum
    t = raum.haupttuer
    if t is None:
        return [True] * len(ziele)
    nx = int(round(raum.breite / aufloesung))
    ny = int(round(raum.tiefe / aufloesung))
    radius = durchgang / 2
    hindernisse = [m.rechteck for m in layout.moebel if not m.ist_wandobjekt and m.typ not in FLACH]
    import numpy as np
    cx = (np.arange(nx) + 0.5) * aufloesung
    cy = (np.arange(ny) + 0.5) * aufloesung
    X, Y = np.meshgrid(cx, cy, indexing="ij")
    maske = (X >= radius) & (Y >= radius) & (X <= raum.breite - radius) & (Y <= raum.tiefe - radius)
    for r in hindernisse:
        dx = np.maximum(np.maximum(r[0] - X, 0.0), X - r[2])
        dy = np.maximum(np.maximum(r[1] - Y, 0.0), Y - r[3])
        maske &= (dx * dx + dy * dy) >= radius * radius
    frei = maske.tolist()

    sx, sy = punkt_vor_oeffnung(t, raum, abstand=radius + 0.05)
    start = (min(nx - 1, max(0, int(sx / aufloesung))), min(ny - 1, max(0, int(sy / aufloesung))))
    besucht = [[False] * ny for _ in range(nx)]
    if frei[start[0]][start[1]]:
        q = deque([start])
        besucht[start[0]][start[1]] = True
        while q:
            i, j = q.popleft()
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if 0 <= a < nx and 0 <= b < ny and frei[a][b] and not besucht[a][b]:
                    besucht[a][b] = True
                    q.append((a, b))

    ergebnis = []
    for zx, zy in ziele:
        ok = False
        reichweite = radius + 0.25
        for i in range(max(0, int((zx - reichweite) / aufloesung)), min(nx, int((zx + reichweite) / aufloesung) + 1)):
            for j in range(max(0, int((zy - reichweite) / aufloesung)), min(ny, int((zy + reichweite) / aufloesung) + 1)):
                cx, cy = (i + 0.5) * aufloesung, (j + 0.5) * aufloesung
                if besucht[i][j] and math.hypot(cx - zx, cy - zy) <= reichweite:
                    ok = True
                    break
            if ok:
                break
        ergebnis.append(ok)
    return ergebnis
