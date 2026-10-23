"""
Machine Learning: lernt aus DEINEN Bewertungen, wie wichtig dir jede Regel ist.

Idee (Buch, Kap. 1): "Wenn sich eine Regel für dich falsch anfühlt, ist sie nicht im Sinne
von Feng Shui – lass dein Gefühl der ultimative Maßstab sein."

Ablauf:
  1. Der Optimierer schlägt verschiedene Layouts vor.
  2. Du bewertest jedes mit 0–10.
  3. Merkmale = Strafen pro Regel (0..1). Modell:
         Bewertung ≈ b − Σ w_i · Strafe_i       mit  w_i ≥ 0
     Gelöst als nicht-negative, regularisierte Regression (Ridge in Richtung der
     Buch-Gewichte, damit wenige Bewertungen die Regelbasis nicht "umwerfen").
  4. Die gelernten Gewichte w_i werden gespeichert und vom Optimierer benutzt.

Zusätzlich: `exportiere_datensatz` erzeugt eine CSV mit Merkmalen + Score, falls du
eigene Modelle (z.B. scikit-learn) trainieren willst.
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


def weiche_regel_ids(raumtyp: str) -> list[str]:
    return [r.id for r in anwendbare_regeln(raumtyp) if r.kategorie != "hart"]


def merkmale(layout: Layout) -> dict[str, float]:
    erg = bewerte(layout)
    return {rid: erg.strafen[rid] for rid in weiche_regel_ids(layout.raum.raumtyp)}


class Personalisierung:
    def __init__(self, datei: str = "meine_bewertungen.json"):
        self.datei = datei
        self.daten: list[dict] = []
        self.gewichte: Optional[dict[str, float]] = None
        if os.path.exists(datei):
            with open(datei, encoding="utf-8") as f:
                inhalt = json.load(f)
            self.daten = inhalt.get("daten", [])
            self.gewichte = inhalt.get("gewichte")

    # ------------------------------------------------------------------
    def bewertung_hinzufuegen(self, layout: Layout, note: float) -> None:
        """note: 0 (fühlt sich furchtbar an) … 10 (perfekt)."""
        self.daten.append({"raumtyp": layout.raum.raumtyp, "merkmale": merkmale(layout), "note": float(note)})
        self.speichern()

    def speichern(self) -> None:
        with open(self.datei, "w", encoding="utf-8") as f:
            json.dump({"daten": self.daten, "gewichte": self.gewichte}, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    def trainiere(self, lambda_prior: float = 2.0, schritte: int = 4000, lernrate: float = 0.01) -> dict[str, float]:
        """Nicht-negative Ridge-Regression per projiziertem Gradientenabstieg."""
        if len(self.daten) < 3:
            raise ValueError("Mindestens 3 Bewertungen nötig (besser 8–15).")
        ids = sorted({k for d in self.daten for k in d["merkmale"]})
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
