# Auswertung FengshuiML

Erzeugt mit `auswertung.py` am 30.10.2026 17:25 (Zufalls-Seed 2026).

## 1. Optimierer (Simulated Annealing) vs. Zufall

| | Zufällige Anordnung | Optimierer |
|---|---|---|
| Anzahl Layouts | 400 | 6 Läufe |
| davon machbar (harte Regeln erfüllt) | 0% | 100% |
| Score Mittelwert | 31.4 | 53.2 |
| Score der machbaren (Mittelwert) | – (keines machbar) | 53.2 |
| Bester Zufallswert / schlechtester Optimierer-Lauf | 50.4 | 37.3 |
| Rechenzeit pro Lauf | – | 0.7 s |

Mit der Einstellung aus `main.py` (6 Neustarts × 3000 Schritte): Score 61.3, machbar, 12 s.

Zufällig an die Wände gestellte Möbel verletzen praktisch immer eine harte Regel (Überlappung, Tür, Laufweg) – ohne Suche gibt es also gar keine brauchbare Einrichtung.

Grafik: `1_optimierer_vs_zufall.png`

## 2. Minimal-Korrektur bestehender Einrichtungen

Ist-Zustände: 8 plausibel, aber nicht optimal eingerichtete Varianten deines Zimmers.

| Zimmer | Score vorher | Score nachher | Änderungen | davon < 30 cm |
|---|---|---|---|---|
| 1 | 35.1 ⚠ | 50.3 | 3 | 0 |
| 2 | 25.2 | 38.8 | 1 | 0 |
| 3 | 26.9 | 61.2 | 5 | 0 |
| 4 | 41.4 | 41.4 | 0 | 0 |
| 5 | 35.0 | 35.0 | 0 | 0 |
| 6 | 35.7 ⚠ | 41.5 | 2 | 0 |
| 7 | 24.0 | 33.9 | 1 | 0 |
| 8 | 44.3 ⚠ | 60.9 | 4 | 0 |

Ø Verbesserung: +11.9 Punkte, Ø 2.0 Änderungen, Mini-Verschiebungen insgesamt: 0  (⚠ = Ist-Zustand verletzt eine harte Regel)

Vorgeschlagene Änderungen mit Begründung:

- Zimmer 1: Schreibtisch: 0.21 m verschieben und drehen (unten → links) – weil: Schildkröte: feste Wand im Rücken (gelöst)
- Zimmer 1: Kleiderschrank: 1.11 m verschieben und drehen (unten → rechts) – weil: Kein hohes Möbel vor dem Fenster (gelöst)
- Zimmer 1: Monstera: 1.49 m verschieben – weil: Pflanzen: Licht ja, Bett nein (besser)
- Zimmer 2: Schreibtisch: 0.40 m verschieben und drehen (rechts → oben) – weil: Schildkröte: feste Wand im Rücken (besser)
- Zimmer 3: Bett: 1.71 m verschieben und drehen (rechts → links) – weil: Nicht in der Chi-Bahn Tür ↔ Fenster (besser)
- Zimmer 3: Schreibtisch: 1.72 m verschieben und drehen (oben → unten) – weil: Schildkröte: feste Wand im Rücken (gelöst)
- Zimmer 3: Kleiderschrank: 3.19 m verschieben und drehen (links → rechts) – weil: macht Platz für die anderen Änderungen
- Zimmer 3: Monstera: 2.93 m verschieben – weil: Pflanzen: Licht ja, Bett nein (gelöst)
- Zimmer 3: Spiegel: 4.69 m verschieben und drehen (rechts → links) – weil: Spiegel richtig platzieren (besser)
- Zimmer 4: keine Änderung (Umstellen lohnt sich nicht)
- Zimmer 5: keine Änderung (Umstellen lohnt sich nicht)
- Zimmer 6: Kleiderschrank: 3.44 m verschieben und drehen (unten → rechts) – weil: Kein hohes Möbel vor dem Fenster (gelöst)
- Zimmer 6: Spiegel: 1.61 m verschieben – weil: Spiegel richtig platzieren (besser)
- Zimmer 7: Schreibtisch: 0.27 m verschieben und drehen (oben → links) – weil: Tür im Blick (gelöst)
- Zimmer 8: Bett: 1.97 m verschieben und drehen (unten → links) – weil: Kein Fenster im Rücken (gelöst)
- Zimmer 8: Schreibtisch: 1.87 m verschieben und drehen (oben → unten) – weil: Tür im Blick (gelöst)
- Zimmer 8: Monstera: 1.30 m verschieben und drehen (rechts → unten) – weil: Pflanzen: Licht ja, Bett nein (gelöst)
- Zimmer 8: Spiegel: 0.58 m verschieben und drehen (unten → links) – weil: Spiegel richtig platzieren (besser)

## 3. Treffen die Regeln das Gefühl? (Noten aus dem Bewertungsbogen)

Die Regeln stammen aus dem Buch, ergänzt um Menschenverstand-Regeln für Lücken im Buch. Die Noten ändern die Regeln nicht – sie prüfen, ob die Reihenfolge nach Regel-Score zur Reihenfolge nach Gefühl passt (Rangkorrelation nach Spearman: 1 = gleiche Reihenfolge, 0 = kein Zusammenhang).

| Runde | Noten | Rangkorrelation ρ |
|---|---|---|
| runde2 | 8 | +0.27 |

```
Übereinstimmung Regeln ↔ Noten (Rangkorrelation, 8 Noten): +0.27
  (1 = Regeln treffen dein Gefühl perfekt, 0 = kein Zusammenhang, negativ = eher umgekehrt)

Größte Abweichungen – hier fehlt vielleicht eine Regel (Kommentare dazu lesen!):
  runde2 Vorschlag 1: Note 7, Regel-Score 55 → Mensch schlechter als Regeln
     verletzt laut Buch: K02 Kein Fenster im Rücken, C09 Spiegel spiegelt keine Tür und keinen Fernseher, K16 Bett zentral & symmetrisch
  runde2 Vorschlag 2: Note 8, Regel-Score 38 → Mensch besser als Regeln
     verletzt laut Buch: K07 Bett nicht an der Türwand, K05 Füße nicht zum großen Fenster, K02 Kein Fenster im Rücken
  runde2 Vorschlag 5: Note 7, Regel-Score 53 → Mensch schlechter als Regeln
     verletzt laut Buch: C02 Spiegel richtig platzieren, K06 Abstand zur Tür, C05 Zonen: Arbeiten vorn, Schlafen hinten
```

Grafik: `3_regeln_vs_noten.png`

## 4. Gradient Boosting (Ersatzmodell)

Siehe `auswertung/surrogat_bericht.md` (erzeugt mit `surrogat_trainieren.py`): Gradient Boosting lernt, den Regel-Score vorherzusagen – trainiert auf tausenden automatisch bewerteten Grundrissen, geprüft mit 10-facher Kreuzvalidierung.


## Grenzen

- Der Score misst die Einhaltung der Buchregeln, nicht eine nachgewiesene Wirkung (Feng Shui ist wissenschaftlich nicht belegt).
- Getestet an einem Zimmer (Maße aus `mein_zimmer.py`); andere Grundrisse können anders abschneiden.
- Wenige Noten von wenigen Personen: Teil 3 ist ein Hinweis, kein Beweis. Die Noten widersprachen sich zwischen Personen und teils bei einer Person (Noten vs. Kommentare) – deshalb lernt das System sie nicht, sondern nutzt sie zum Prüfen und um Lücken im Buch zu finden.
