"""
Nachgebautes LEERES Zimmer als Testbild – ohne KI-Modelle, ohne echtes Foto.

Wozu? Damit sich die Funktion „leeres Zimmer einrichten“ sofort ausprobieren und automatisch testen lässt:
Das Programm berechnet ein einfaches Bild eines leeren Raums (Boden, Wände, Tür, Fenster) und dazu die
exakte Tiefenkarte. Beides geht dann durch dieselbe Vermessung wie ein echtes Foto (foto3d.vermesse).

Bei einem echten Foto kommen Tiefe und Tür/Fenster stattdessen von den KI-Modellen (Depth Anything, YOLOE).
"""
from __future__ import annotations

import math

import numpy as np

from .foto import Erkennung
from .foto3d import Kamera, Vermessung, vermesse
from .modell import Oeffnung, Raum


def demo_raum(raumtyp: str = "schlafzimmer", breite: float = 3.8, tiefe: float = 4.4) -> Raum:
    """Tür rechts unten, großes Fenster in der Wand gegenüber der Kamera."""
    return Raum("Demo-Zimmer", breite, tiefe, raumtyp=raumtyp, hoehe=2.5, oeffnungen=[
        Oeffnung("tuer", wand="rechts", von=0.5, breite=0.9, hoehe=2.0),
        Oeffnung("fenster", wand="oben", von=breite / 2 - 0.8, breite=1.6, bruestung=0.9, hoehe=1.3),
    ])


def _wandpunkt(raum: Raum, o: Oeffnung, s: float, h: float) -> tuple[float, float, float]:
    if o.wand == "unten":
        return (s, 0.0, h)
    if o.wand == "oben":
        return (s, raum.tiefe, h)
    if o.wand == "links":
        return (0.0, s, h)
    return (raum.breite, s, h)


def leeres_zimmer(raum: Raum | None = None, bild_breite: int = 1200, bild_hoehe: int = 900,
                  kamera=(0.35, 0.35, 1.45), blickwinkel_grad: float = 82.0, rauschen: float = 0.004,
                  seed: int = 0) -> tuple[np.ndarray, np.ndarray, Kamera, list[Erkennung], Raum]:
    """Gibt (Bild, Tiefenkarte in Metern, Kamera, Erkennungen für Tür/Fenster, Raum) zurück.

    Die Kamera steht in der Ecke links unten und schaut diagonal in die gegenüberliegende Ecke –
    genau so, wie man ein Zimmer am besten fotografiert.
    """
    raum = raum or demo_raum()
    W, H = bild_breite, bild_hoehe
    f = (W / 2) / math.tan(math.radians(blickwinkel_grad) / 2)
    kam = Kamera(f, f, W / 2, H / 2, W, H)
    C = np.array(kamera, float)
    ziel = np.array([raum.breite * 0.82, raum.tiefe * 0.9, 0.95])
    F = ziel - C
    F /= np.linalg.norm(F)
    R = np.cross(F, [0, 0, 1.0])
    R /= np.linalg.norm(R)
    D = np.cross(F, R)                      # zeigt im Bild nach unten

    v, u = np.mgrid[0:H, 0:W]
    dx, dy = (u + 0.5 - kam.cx) / kam.fx, (v + 0.5 - kam.cy) / kam.fy
    strahl = dx[..., None] * R + dy[..., None] * D + F          # Vorwärtsanteil 1 → Parameter t = Tiefe z

    tiefe = np.full((H, W), np.inf)
    flaeche = np.zeros((H, W), np.uint8)                         # 1 Boden, 2 Decke, 3..6 Wände
    ebenen = [(1, 2, 0.0), (2, 2, raum.hoehe), (3, 1, 0.0), (4, 1, raum.tiefe), (5, 0, 0.0), (6, 0, raum.breite)]
    for kennung, achse, wert in ebenen:
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (wert - C[achse]) / strahl[..., achse]
        ok = (t > 1e-6) & (t < tiefe)
        tiefe = np.where(ok, t, tiefe)
        flaeche = np.where(ok, kennung, flaeche)
    P = C + strahl * tiefe[..., None]

    # ---- Farben: Parkett, helle Wände mit leichtem Verlauf, weiße Decke
    rng = np.random.default_rng(seed)
    bild = np.zeros((H, W, 3), np.float32)
    dielen = (np.floor(P[..., 0] / 0.14) % 2) * 6 + (np.floor(P[..., 1] / 1.1 + np.floor(P[..., 0] / 0.14) * 0.37) % 2) * 5
    boden = np.array([176, 140, 102], np.float32) + dielen[..., None]
    wandfarbe = {3: (228, 224, 216), 4: (236, 232, 224), 5: (221, 217, 209), 6: (231, 227, 219)}
    bild[flaeche == 1] = boden[flaeche == 1]
    bild[flaeche == 2] = (244, 243, 240)
    for k, farbe in wandfarbe.items():
        bild[flaeche == k] = farbe
    bild *= (1.0 - 0.10 * np.clip(tiefe / 7.0, 0, 1))[..., None]            # hinten etwas dunkler
    sockel = (flaeche >= 3) & (P[..., 2] < 0.07)
    bild[sockel] = (250, 249, 246)

    # ---- Tür und Fenster einzeichnen + als "Erkennungen" zurückgeben (wie YOLOE sie liefern würde)
    wand_kennung = {"unten": 3, "oben": 4, "links": 5, "rechts": 6}
    erk: list[Erkennung] = []
    for o in raum.oeffnungen:
        entlang = P[..., 0] if o.wand in ("unten", "oben") else P[..., 1]
        h1, h2 = (0.0, o.hoehe) if o.ist_tuer and o.typ == "tuer" else (o.bruestung, o.bruestung + o.hoehe)
        maske = (flaeche == wand_kennung[o.wand]) & (entlang >= o.von) & (entlang <= o.bis) & \
                (P[..., 2] >= h1) & (P[..., 2] <= h2)
        if not maske.any():
            continue
        if o.typ == "tuer":
            bild[maske] = (150, 112, 78)
            rahmen = maske & ((entlang < o.von + 0.05) | (entlang > o.bis - 0.05) | (P[..., 2] > h2 - 0.05))
            bild[rahmen] = (238, 236, 230)
            griff = maske & (np.abs(entlang - (o.von + 0.1)) < 0.05) & (np.abs(P[..., 2] - 1.05) < 0.02)
            bild[griff] = (70, 70, 72)
        else:
            himmel = 1.0 - (P[..., 2] - h1) / max(0.1, h2 - h1)
            bild[maske] = (np.array([196, 222, 240], np.float32) * (1 - 0.25 * himmel[..., None])
                           + np.array([120, 150, 110], np.float32) * 0.25 * himmel[..., None])[maske]
            mitte = (o.von + o.bis) / 2
            rahmen = maske & ((entlang < o.von + 0.05) | (entlang > o.bis - 0.05) | (P[..., 2] > h2 - 0.05) |
                              (P[..., 2] < h1 + 0.05) | (np.abs(entlang - mitte) < 0.025))
            bild[rahmen] = (248, 247, 244)
        ys, xs = np.nonzero(maske)
        box = (float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max()))
        # Umriss aus den vier Ecken (Rechteck an der Wand → Viereck im Bild)
        ecken = [_wandpunkt(raum, o, s, h) for s, h in ((o.von, h1), (o.bis, h1), (o.bis, h2), (o.von, h2))]
        poly = []
        for e in ecken:
            d = np.array(e) - C
            z = d @ F
            if z > 0.05:
                poly.append([float(kam.fx * (d @ R) / z + kam.cx), float(kam.fy * (d @ D) / z + kam.cy)])
        typ = "tuer" if o.typ == "tuer" else "fenster"
        erk.append(Erkennung(typ, "door" if typ == "tuer" else "window", 0.9, box, poly if len(poly) == 4 else None))

    bild += rng.normal(0, 1.5, bild.shape)
    tiefe_mess = tiefe * (1 + rng.normal(0, rauschen, tiefe.shape))          # kleines Messrauschen
    return np.clip(bild, 0, 255).astype(np.uint8), tiefe_mess.astype(np.float32), kam, erk, raum


def demo_vermessung(raumtyp: str = "schlafzimmer", **kw) -> tuple[np.ndarray, Vermessung, Raum]:
    """Leeres Demo-Zimmer bauen und wie ein Foto vermessen. Rückgabe: (Bild, Vermessung, wahrer Raum)."""
    rgb, tiefe, kam, erk, raum = leeres_zimmer(demo_raum(raumtyp), **kw)
    v = vermesse(rgb.shape[:2], tiefe, kam, erk, raumtyp, kamera_in_ecke=True)
    return rgb, v, raum
