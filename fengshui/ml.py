"""
Bewertungen (Noten von Menschen) speichern und damit die Regelbasis PRÜFEN.

Grundsatz des Projekts: Es gelten die Regeln aus dem Buch, ergänzt um Regeln mit Menschenverstand dort, wo das
Buch eine Lücke hat. Die Noten ändern die Gewichte der Regeln NICHT. Sie dienen zu zweierlei:
  1. Prüfen: Trifft die Reihenfolge nach Buch-Score das Gefühl der Menschen? (Rangkorrelation, siehe `pruefe`)
  2. Lücken finden: Wo Buch und Mensch stark auseinanderliegen, zeigen die Kommentare oft eine fehlende Regel.
     So sind die Menschenverstand-Regeln H08–H11 entstanden.

Widersprüchliche Noten (zwischen Personen oder bei einer Person) sind dadurch kein Problem für das System:
Sie werden gemessen und berichtet, aber nicht „gelernt“.

Das frühere Umgewichten per Regression (`trainiere`) ist noch vorhanden, wird aber nur benutzt, wenn
GEWICHTE_ANPASSEN = True gesetzt wird (z. B. für Experimente in auswertung.py).

Zusätzlich: `exportiere_datensatz` erzeugt eine CSV mit Merkmalen + Score.
"""
from __future__ import annotations

import csv
import json
import os
import random
from typing import Optional

import numpy as np

from .bewertung import bewerte
from .modell import Layout
from .regeln import REGELN, anwendbare_regeln

# False = die Gewichte aus dem Buch gelten immer; Noten werden nur gespeichert und zum Prüfen benutzt.
GEWICHTE_ANPASSEN = False


def weiche_regel_ids(raumtyp: str) -> list[str]:
    return [r.id for r in anwendbare_regeln(raumtyp) if r.kategorie != "hart"]


def merkmale(layout: Layout) -> dict[str, float]:
    erg = bewerte(layout)
    return {rid: erg.strafen[rid] for rid in weiche_regel_ids(layout.raum.raumtyp)}


class Personalisierung:
    def __init__(self, datei: str = "meine_bewertungen.json"):
        self.datei = datei
        self.daten: list[dict] = []
        self.gewichte: Optional[dict[str, float]] = None      # None = Buch-Gewichte (Standard)
        self._gelernt: Optional[dict[str, float]] = None
        if os.path.exists(datei):
            with open(datei, encoding="utf-8") as f:
                inhalt = json.load(f)
            self.daten = inhalt.get("daten", [])
            self._gelernt = inhalt.get("gewichte")
            if GEWICHTE_ANPASSEN:
                self.gewichte = self._gelernt

    # ------------------------------------------------------------------
    def bewertung_hinzufuegen(self, layout: Layout, note: float) -> None:
        """note: 0 (fühlt sich furchtbar an) … 10 (perfekt)."""
        self.daten.append({"raumtyp": layout.raum.raumtyp, "merkmale": merkmale(layout), "note": float(note)})
        self.speichern()

    def speichern(self) -> None:
        with open(self.datei, "w", encoding="utf-8") as f:
            json.dump({"daten": self.daten, "gewichte": self.gewichte or self._gelernt}, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    def trainiere(self, lambda_prior: float = 2.0, schritte: int = 4000, lernrate: float = 0.01) -> dict[str, float]:
        """Nicht-negative Ridge-Regression per projiziertem Gradientenabstieg."""
        if len(self.daten) < 3:
            raise ValueError("Mindestens 3 Bewertungen nötig (besser 8–15).")
        bekannt = {r.id for r in REGELN}
        ids = sorted({k for d in self.daten for k in d["merkmale"] if k in bekannt})   # entfernte Regeln ignorieren
        S = np.array([[d["merkmale"].get(k, 0.0) for k in ids] for d in self.daten])
        y = np.array([d["note"] for d in self.daten])
        buch = {r.id: r.gewicht for r in REGELN}
        w0 = np.array([buch[k] for k in ids])
        # Skala: Buch-Gewichte grob auf Notenskala bringen (Note 10 ~ keine Strafe)
        skala = 10.0 / max(1e-6, w0.sum() / 2)
        w = w0 * skala
        w_prior = w.copy()
        b = 10.0
        n = len(y)
        for _ in range(schritte):
            pred = b - S @ w
            fehler = pred - y
            grad_w = -(S.T @ fehler) / n + lambda_prior * (w - w_prior) / n
            grad_b = fehler.mean()
            w = np.maximum(0.0, w - lernrate * grad_w * 10)
            b -= lernrate * grad_b * 10
        # zurück auf Buch-Skala
        gelernt = {k: float(v / skala) for k, v in zip(ids, w)}
        self.gewichte = gelernt
        self.speichern()
        pred = b - S @ w
        mae = float(np.abs(pred - y).mean())
        print(f"Training mit {n} Bewertungen – mittlerer Fehler: {mae:.2f} Notenpunkte")
        return gelernt

    def vergleich(self) -> str:
        if not self.gewichte:
            return "Noch nicht trainiert."
        buch = {r.id: (r.gewicht, r.titel) for r in REGELN}
        zeilen = ["Regel                                         Buch  -> Du"]
        for k, v in sorted(self.gewichte.items(), key=lambda kv: -(kv[1] - buch[kv[0]][0])):
            w0, titel = buch[k]
            pfeil = "↑" if v > w0 * 1.15 else ("↓" if v < w0 * 0.85 else "=")
            zeilen.append(f"{k} {titel[:40]:<40} {w0:4.1f} -> {v:4.1f} {pfeil}")
        return "\n".join(zeilen)


def regel_score(merkm: dict[str, float]) -> float:
    """Buch-Score (0–100) aus gespeicherten Merkmalen – dieselbe Formel wie bewertung.bewerte (nur weiche Regeln)."""
    gewicht = {r.id: r.gewicht for r in REGELN}
    summe = sum(gewicht[k] * v for k, v in merkm.items() if k in gewicht)
    return 100.0 / (1.0 + summe / 5.0)


def _raenge(x):
    x = np.asarray(x, float)
    r = np.empty(len(x))
    r[x.argsort()] = np.arange(len(x))
    for v in np.unique(x):
        idx = x == v
        if idx.sum() > 1:
            r[idx] = r[idx].mean()
    return r


def spearman(a, b) -> float:
    """Rangkorrelation: 1 = gleiche Reihenfolge, 0 = kein Zusammenhang, −1 = genau umgekehrt."""
    ra, rb = _raenge(a), _raenge(b)
    if len(ra) < 3 or ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def pruefe(daten: list[dict], top: int = 3) -> str:
    """Wie gut trifft die Regelbasis die Noten? Plus die größten Abweichungen (Kandidaten für fehlende Regeln)."""
    if len(daten) < 3:
        return "Für die Prüfung braucht es mindestens 3 Noten."
    scores = [regel_score(d["merkmale"]) for d in daten]
    noten = [d["note"] for d in daten]
    rho = spearman(scores, noten)
    z = [f"Übereinstimmung Regeln ↔ Noten (Rangkorrelation, {len(daten)} Noten): {rho:+.2f}",
         "  (1 = Regeln treffen dein Gefühl perfekt, 0 = kein Zusammenhang, negativ = eher umgekehrt)"]
    # Abweichung: Rang nach Regeln vs. Rang nach Note
    rs, rn = _raenge(scores), _raenge(noten)
    abw = sorted(range(len(daten)), key=lambda i: -abs(rs[i] - rn[i]))[:top]
    titel = {r.id: r.titel for r in REGELN}
    z.append("")
    z.append("Größte Abweichungen – hier fehlt vielleicht eine Regel (Kommentare dazu lesen!):")
    for i in abw:
        d = daten[i]
        richtung = "Mensch besser als Regeln" if rn[i] > rs[i] else "Mensch schlechter als Regeln"
        haupt = sorted(((v, k) for k, v in d["merkmale"].items() if v > 0.2 and k in titel), reverse=True)[:3]
        wo = f"{d.get('runde', '?')} Vorschlag {d.get('vorschlag', '?')}"
        z.append(f"  {wo}: Note {d['note']:g}, Regel-Score {scores[i]:.0f} → {richtung}")
        if haupt:
            z.append("     verletzt laut Buch: " + ", ".join(f"{k} {titel[k]}" for _, k in haupt))
    return "\n".join(z)


def exportiere_datensatz(layout: Layout, anzahl: int, pfad: str, seed: int = 0) -> None:
    """Erzeugt zufällige Layouts und speichert Merkmale + Regel-Score als CSV (Trainingsdaten)."""
    from .optimierer import zufallslayout
    rng = random.Random(seed)
    ids = weiche_regel_ids(layout.raum.raumtyp)
    with open(pfad, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        kopf = []
        for m in layout.moebel:
            kopf += [f"{m.name}_x", f"{m.name}_y", f"{m.name}_rot"]
        w.writerow(kopf + ids + ["machbar", "score"])
        for _ in range(anzahl):
            lay = zufallslayout(layout, rng)
            erg = bewerte(lay)
            zeile = []
            for m in lay.moebel:
                zeile += [round(m.x, 3), round(m.y, 3), m.rot]
            w.writerow(zeile + [round(erg.strafen[i], 4) for i in ids] + [int(erg.machbar), round(erg.score, 2)])
    print(f"{anzahl} Layouts nach {pfad} geschrieben.")
