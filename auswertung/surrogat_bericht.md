# Gradient Boosting als Ersatzmodell für die Regelbasis

Erzeugt mit `surrogat_trainieren.py` am 30.10.2026 18:23 (Seed 2026).

## Idee

Die Regelbasis (Buch + Menschenverstand) bewertet automatisch erzeugte Grundrisse – das sind die Labels, ohne Handarbeit. Gradient Boosting lernt, diese Bewertung nur aus einfachen geometrischen Merkmalen (Positionen, Ausrichtung, Abstände zu Wänden, Tür, Fenster und zwischen den Möbeln) vorherzusagen. Die Regeln selbst ändern sich dadurch nicht: Das Modell ahmt sie nach und ist dafür viel schneller (Surrogatmodell / Wissensdestillation).

## Daten

- 6000 Grundrisse deines Zimmers (30 % zufällig, 70 % ausgehend von teil-optimierten Grundrissen mit 0–12 zufälligen Veränderungen), erzeugt in 19 s
- davon machbar (alle harten Regeln erfüllt): 9%
- 72 Merkmale pro Grundriss

## Regression: Score vorhersagen (10-fache Kreuzvalidierung)

| Modell | MAE (Score-Punkte) | R² | Rangkorrelation ρ | Rechenzeit |
|---|---|---|---|---|
| Mittelwert raten (Baseline) | 5.77 ± 0.13 | -0.002 | – | 0 s |
| Lineare Regression | 3.51 ± 0.12 | 0.618 | 0.815 | 0 s |
| Random Forest | 1.71 ± 0.06 | 0.895 | 0.933 | 75 s |
| Gradient Boosting | 1.18 ± 0.05 | 0.951 | 0.968 | 17 s |

MAE = mittlerer absoluter Fehler, R² = Anteil erklärter Streuung (1 = perfekt), ρ = trifft das Modell die Reihenfolge? ± = Standardabweichung über die 10 Folds.

Grafiken: `surrogat_modellvergleich.png`, `surrogat_vorhersage.png`

## Klassifikation: machbar ja/nein (10-fache Kreuzvalidierung)

| Modell | Genauigkeit | F1 (machbar) | ROC-AUC |
|---|---|---|---|
| Häufigste Klasse (Baseline) | 90.8% | 0.00 | 0.500 |
| Logistische Regression | 95.1% | 0.74 | 0.976 |
| Gradient Boosting | 98.6% | 0.92 | 0.997 |

## Lernkurve (Gradient Boosting, 20 % Testdaten)

| Trainingsbeispiele | Fehler Testdaten | Fehler Trainingsdaten |
|---|---|---|
| 250 | 2.51 | 0.11 |
| 500 | 2.11 | 0.05 |
| 1000 | 1.76 | 0.06 |
| 2000 | 1.49 | 0.18 |
| 3000 | 1.38 | 0.30 |
| 4800 | 1.22 | 0.44 |

Liegt der Testfehler deutlich über dem Trainingsfehler, lernt das Modell teils auswendig (Overfitting); mehr Daten verkleinern die Lücke. Grafik: `surrogat_lernkurve.png`

## Worauf achtet das Modell? (Permutation Importance, Top 15)

| Merkmal | Wichtigkeit |
|---|---|
| Bett: Winkel zur Tür | 1.80 |
| Abstand Bett–Schreibtisch | 1.39 |
| Abstand Bett–Kleiderschrank | 0.88 |
| Schreibtisch: Rückseite bis Wand | 0.68 |
| Bett: Rückseite bis Wand | 0.56 |
| Schreibtisch: Abstand zum Fenster | 0.41 |
| Schreibtisch: Winkel zur Tür | 0.31 |
| Kleiderschrank: Abstand zum Fenster | 0.26 |
| Bett: Abstand zur Tür | 0.24 |
| Abstand Bett–Monstera | 0.22 |
| Schreibtisch: x (relativ) | 0.20 |
| Bett: y (relativ) | 0.19 |
| Bett: x (relativ) | 0.15 |
| Kleiderschrank: Abstand zur Tür | 0.15 |
| Schreibtisch: Vorderseite bis Wand | 0.15 |

Grafik: `surrogat_merkmale.png`

## Nutzen: Vorauswahl aus vielen Kandidaten

Rund um einen Grundriss wurden 2000 Varianten erzeugt. Das Modell wählt 20 aus; danach prüft die echte Regelbasis nur diese 20.

| | 20 vom Modell gewählt | 20 zufällig gewählt |
|---|---|---|
| Ø echter Score (unmachbar = 0) | 55.2 | 11.0 |
| davon machbar | 20/20 | 5/20 |
| bester echter Score | 58.8 | – |

Bestes aller 2000 Kandidaten: 58.8. Von den echten Top 20 hat das Modell 12 gefunden.

Zeit: alle Kandidaten mit Regeln bewerten 1.6 s (0.8 ms pro Grundriss) – Modell 0.10 s (0.05 ms pro Grundriss).

## Grenzen

- Das Modell kann nie besser sein als die Regelbasis, die es nachahmt – es ist schneller, nicht klüger.
- Trainiert auf EIN Zimmer: Für einen anderen Grundriss oder andere Möbel muss es neu trainiert werden (die Merkmale hängen von den Möbeln ab).
- Für die endgültige Entscheidung wird immer die echte Regelbasis benutzt; das Modell wählt nur vor.
