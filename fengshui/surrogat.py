"""
GRADIENT BOOSTING als Ersatzmodell (Surrogatmodell) für die Regelbasis.

Idee: Die Regelbasis (Buch + Menschenverstand) ist der „Lehrer“. Sie bewertet tausende automatisch erzeugte
Grundrisse – das sind die Labels, ganz ohne Handarbeit. Ein Gradient-Boosting-Modell lernt daraus,
  * den Feng-Shui-Score (0–100) vorherzusagen          -> Regression
  * ob ein Grundriss machbar ist (alle harten Regeln)   -> Klassifikation
nur aus einfachen geometrischen Merkmalen (Positionen, Abstände, Ausrichtung). Die Regeln selbst sieht es nie.

Wofür? Das Modell ist viel schneller als alle Regeln durchzurechnen. Es kann deshalb aus tausenden Kandidaten
die vielversprechendsten vorauswählen; nur diese prüft danach die echte Regelbasis (siehe surrogat_trainieren.py).
Fachbegriffe: Surrogatmodell, Wissensdestillation (ein Modell lernt das Verhalten eines anderen Systems).
"""
from __future__ import annotations

import math
import random
from typing import Optional

import numpy as np

from . import geometrie as g
from .bewertung import bewerte
from .modell import Layout
from .optimierer import _nachbar, optimiere, zufallslayout

RICHTUNGEN = (0, 90, 180, 270)
BLICK_MOEBEL = {"bett", "schreibtisch", "sofa"}


def _hauptmoebel(layout: Layout):
    """Möbel, die selbst platziert werden (Nachttische & Co. wandern mit und brauchen keine eigenen Merkmale)."""
    return [m for m in layout.moebel if not m.gehoert_zu]


def merkmal_namen(layout: Layout) -> list[str]:
    namen = []
    haupt = _hauptmoebel(layout)
    for m in haupt:
        n = m.name
        namen += [f"{n}: x (relativ)", f"{n}: y (relativ)"]
        namen += [f"{n}: Blick {r}°" for r in RICHTUNGEN]
        namen += [f"{n}: Rückseite bis Wand", f"{n}: Vorderseite bis Wand", f"{n}: Abstand zur Tür",
                  f"{n}: Abstand zum Fenster"]
        if m.typ in BLICK_MOEBEL:
            namen += [f"{n}: Winkel zur Tür"]
    for i, a in enumerate(haupt):
        for b in haupt[i + 1:]:
            namen += [f"Abstand {a.name}–{b.name}", f"Überlappung {a.name}–{b.name}"]
    return namen


def merkmale(layout: Layout) -> np.ndarray:
    """Geometrische Merkmale eines Grundrisses – dieselbe Reihenfolge wie `merkmal_namen`."""
    raum = layout.raum
    tuer = raum.haupttuer
    tm = tuer.mitte(raum) if tuer else (0.0, 0.0)
    fenster = [f.mitte(raum) for f in raum.fenster] or [(raum.breite / 2, raum.tiefe)]
    werte = []
    haupt = _hauptmoebel(layout)
    for m in haupt:
        werte += [m.x / raum.breite, m.y / raum.tiefe]
        werte += [1.0 if m.rot % 360 == r else 0.0 for r in RICHTUNGEN]
        werte += [g.abstand_zur_wand(m, raum, m.hinten), g.abstand_zur_wand(m, raum, m.vorne),
                  g.abstand_punkt_rechteck(tm, m.rechteck),
                  min(g.abstand_punkt_rechteck(f, m.rechteck) for f in fenster)]
        if m.typ in BLICK_MOEBEL:
            werte += [g.winkel_zu(g.personenpunkt(m), m.vorne, tm) / 180.0]
    for i, a in enumerate(haupt):
        for b in haupt[i + 1:]:
            werte += [g.abstand_rechtecke(a.rechteck, b.rechteck), g.ueberlappung(a.rechteck, b.rechteck)]
    return np.array(werte, dtype=float)


def erzeuge_datensatz(basis: Layout, anzahl: int = 6000, seed: int = 0, ausgabe: bool = True):
    """Grundrisse von sehr schlecht bis sehr gut erzeugen und von der Regelbasis bewerten lassen (= Labels).

    Mischung: 30 % ganz zufällig, 70 % ausgehend von (teil-)optimierten Grundrissen mit 0–12 zufälligen
    Veränderungen. So sind gute, mittlere und schlechte, machbare und unmachbare Beispiele dabei.
    Rückgabe: X (Merkmale), y_score (0–100), y_machbar (0/1), Liste der Layouts
    """
    rng = random.Random(seed)
    startpunkte = []
    for i in range(30):
        lay, _ = optimiere(basis, iterationen=rng.choice([100, 200, 400, 800]), neustarts=1,
                           seed=rng.randrange(10 ** 9), anzahl_ergebnisse=1, ausgabe=False)[0]
        startpunkte.append(lay)
    X, y_s, y_m, lays = [], [], [], []
    for i in range(anzahl):
        if rng.random() < 0.3:
            lay = zufallslayout(basis, rng)
        else:
            lay = rng.choice(startpunkte)
            for _ in range(rng.randint(0, 12)):
                lay = _nachbar(lay, rng, rng.uniform(0.2, 0.8))
        e = bewerte(lay)
        X.append(merkmale(lay))
        y_s.append(e.score)
        y_m.append(1 if e.machbar else 0)
        lays.append(lay)
        if ausgabe and (i + 1) % 1000 == 0:
            print(f"     {i + 1}/{anzahl} Grundrisse bewertet")
    return np.array(X), np.array(y_s), np.array(y_m), lays


class Surrogat:
    """Trainierte Modelle + Vorhersage für neue Grundrisse."""

    def __init__(self, regressor, klassifikator, namen: list[str]):
        self.regressor = regressor
        self.klassifikator = klassifikator
        self.namen = namen

    def schaetze(self, layouts: list[Layout]) -> tuple[np.ndarray, np.ndarray]:
        """(geschätzter Score, geschätzte Wahrscheinlichkeit 'machbar') für viele Grundrisse auf einmal."""
        X = np.array([merkmale(l) for l in layouts])
        return self.regressor.predict(X), self.klassifikator.predict_proba(X)[:, 1]

    def speichern(self, pfad: str) -> None:
        import joblib
        joblib.dump(self, pfad)

    @staticmethod
    def laden(pfad: str) -> Optional["Surrogat"]:
        import os
        if not os.path.exists(pfad):
            return None
        import joblib
        return joblib.load(pfad)


def vorauswahl(surrogat: Surrogat, kandidaten: list[Layout], k: int = 20) -> list[int]:
    """Indizes der k vielversprechendsten Kandidaten (machbar laut Modell zuerst, dann nach Score)."""
    s, p = surrogat.schaetze(kandidaten)
    rang = sorted(range(len(kandidaten)), key=lambda i: (p[i] < 0.5, -s[i]))
    return rang[:k]


def nachbarn(layout: Layout, anzahl: int, seed: int = 0) -> list[Layout]:
    """Kandidaten rund um einen Grundriss: 1–3 zufällige Veränderungen."""
    rng = random.Random(seed)
    out = []
    for _ in range(anzahl):
        lay = layout
        for _ in range(rng.randint(1, 3)):
            lay = _nachbar(lay, rng, 0.6)
        out.append(lay)
    return out


def _rmse(a, b) -> float:
    return math.sqrt(float(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))
