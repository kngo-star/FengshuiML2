# Auswertung FengshuiML

Erzeugt mit `auswertung.py` am 29.10.2026 16:21 (Zufalls-Seed 2026).

## 1. Optimierer (Simulated Annealing) vs. Zufall

| | Zufällige Anordnung | Optimierer |
|---|---|---|
| Anzahl Layouts | 400 | 6 Läufe |
| davon machbar (harte Regeln erfüllt) | 0% | 100% |
| Score Mittelwert | 31.4 | 47.5 |
| Score der machbaren (Mittelwert) | – (keines machbar) | 47.5 |
| Bester Zufallswert / schlechtester Optimierer-Lauf | 50.4 | 36.1 |
| Rechenzeit pro Lauf | – | 1.0 s |

Mit der Einstellung aus `main.py` (6 Neustarts × 3000 Schritte): Score 61.3, machbar, 18 s.

Zufällig an die Wände gestellte Möbel verletzen praktisch immer eine harte Regel (Überlappung, Tür, Laufweg) – ohne Suche gibt es also gar keine brauchbare Einrichtung.

Grafik: `1_optimierer_vs_zufall.png`

## 2. Minimal-Korrektur bestehender Einrichtungen

Ist-Zustände: 8 plausibel, aber nicht optimal eingerichtete Varianten deines Zimmers.

| Zimmer | Score vorher | Score nachher | Änderungen | davon < 30 cm |
|---|---|---|---|---|
| 1 | 32.0 | 47.8 | 2 | 0 |
| 2 | 24.5 | 31.5 | 1 | 0 |
| 3 | 34.3 | 34.3 | 0 | 0 |
| 4 | 47.3 | 58.3 | 2 | 0 |
| 5 | 35.0 | 35.0 | 0 | 0 |
| 6 | 35.3 | 53.1 | 3 | 0 |
| 7 | 39.2 ⚠ | 56.6 | 4 | 0 |
| 8 | 41.6 | 41.6 | 0 | 0 |

Ø Verbesserung: +8.6 Punkte, Ø 1.5 Änderungen, Mini-Verschiebungen insgesamt: 0  (⚠ = Ist-Zustand verletzt eine harte Regel)

Vorgeschlagene Änderungen mit Begründung:

- Zimmer 1: Schreibtisch: 0.58 m verschieben und drehen (rechts → links) – weil: Tür im Blick (gelöst)
- Zimmer 1: Kleiderschrank: 0.46 m verschieben und drehen (unten → rechts) – weil: Fenster & Ausblick nicht verstellen (gelöst)
- Zimmer 2: Schreibtisch: 0.21 m verschieben und drehen (oben → links) – weil: Tür im Blick (gelöst)
- Zimmer 3: keine Änderung (Umstellen lohnt sich nicht)
- Zimmer 4: Schreibtisch: 0.48 m verschieben und drehen (oben → links) – weil: Tür im Blick (gelöst)
- Zimmer 4: Kleiderschrank: 1.34 m verschieben – weil: Fenster & Ausblick nicht verstellen (gelöst)
- Zimmer 5: keine Änderung (Umstellen lohnt sich nicht)
- Zimmer 6: Bett: 1.52 m verschieben – weil: Abstand zur Tür (gelöst)
- Zimmer 6: Schreibtisch: 3.01 m verschieben – weil: Schildkröte: feste Wand im Rücken (gelöst)
- Zimmer 6: Kleiderschrank: 2.71 m verschieben und drehen (unten → rechts) – weil: Fenster & Ausblick nicht verstellen (gelöst)
- Zimmer 7: Bett: 2.03 m verschieben und drehen (unten → links) – weil: Kein Fenster im Rücken (gelöst)
- Zimmer 7: Schreibtisch: 2.21 m verschieben und drehen (rechts → unten) – weil: Laufwege frei (≥ 60 cm) (gelöst)
- Zimmer 7: Kleiderschrank: 2.68 m verschieben – weil: macht Platz für die anderen Änderungen
- Zimmer 7: Monstera: 0.50 m verschieben – weil: Pflanzen: Licht ja, Bett nein (besser)
- Zimmer 8: keine Änderung (Umstellen lohnt sich nicht)

## 3. Simulationsstudie: Lernt das Modell einen Geschmack?

6 virtuelle Testpersonen mit bekanntem Geschmack (zufällig: manche Regeln egal, manche bis 3× so wichtig wie im Buch) bewerten Layouts – mit Rauschen (±0.8 Noten) und halben Noten wie echte Menschen. Gemessen wird, wie gut das Modell die Reihenfolge von 60 *nicht* bewerteten Layouts trifft (Rangkorrelation nach Spearman, 1 = perfekt).

| Bewertungen | Personalisiert ρ | Nur Buch ρ | Personalisiert Fehler Ø | Nur Buch Fehler Ø |
|---|---|---|---|---|
| 5 | 0.78 ± 0.13 | 0.74 ± 0.13 | 1.04 | 1.15 |
| 8 | 0.82 ± 0.11 | 0.74 ± 0.13 | 0.99 | 1.12 |
| 12 | 0.83 ± 0.09 | 0.74 ± 0.13 | 0.96 | 1.11 |
| 20 | 0.89 ± 0.04 | 0.74 ± 0.13 | 0.86 | 1.01 |
| 30 | 0.92 ± 0.03 | 0.74 ± 0.13 | 0.81 | 1.02 |
| 40 | 0.94 ± 0.03 | 0.74 ± 0.13 | 0.79 | 1.01 |

Grafik: `3_lernkurve_simulation.png`

## 4. Eure echten Bewertungen (Leave-one-out-Kreuzvalidierung)

Noch keine `meine_bewertungen.json` – erst mit `lernen.py` bewerten, dann erneut ausführen.

## Grenzen

- Der Score misst die Einhaltung der Buchregeln, nicht eine nachgewiesene Wirkung (Feng Shui ist wissenschaftlich nicht belegt).
- Getestet an einem Zimmer (Maße aus `mein_zimmer.py`); andere Grundrisse können anders abschneiden.
- Die Simulationsstudie zeigt, dass das Verfahren funktioniert, *wenn* sich Geschmack als gewichtete Regel-Summe beschreiben lässt – ob das für echte Menschen gilt, zeigt erst Teil 4.
