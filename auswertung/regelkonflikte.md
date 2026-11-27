# Regelkonflikte

Erzeugt mit `regelkonflikte.py` am 27.11.2026 10:00 (Seed 2026, 4 Läufe × 2000 Schritte pro Experiment, 128 s).

## Wie gut ist der Score wirklich?

| | Score |
|---|---|
| Optimierer, zwei normale Durchgänge (bester) | 61.3 |
| Unterschied zwischen den beiden Durchgängen | 0.1 |
| Bester Grundriss nach der Analyse | 61.3 |
| Obergrenze, wenn nur die Grenzen des Raums übrig blieben | 83.3 |
| erreicht von der Obergrenze | 74 % |

100 Punkte gibt es nur, wenn keine einzige weiche Regel verletzt ist. In einem echten Zimmer geht das meist nicht – ein Score sollte darum immer **relativ zum Bestwert desselben Zimmers** gelesen werden (`relativer_score()` in `fengshui/konflikte.py`).

## Warum sind diese Regeln im besten Grundriss verletzt?

3× liegt es am Raum, 3× an einem Konflikt mit anderen Regeln, 0× hatte der Optimierer einen besseren Grundriss übersehen.

| Regel | Strafe × Gewicht | kostet Punkte | Strafe allein | Preis fürs Erfüllen | Ursache |
|---|---|---|---|---|---|
| K06 Abstand zur Tür | 0.53 × 2.0 | 9.1 | 0.00 | 2.01 | **Konflikt** mit K02 (+1.50), C09 (+0.72), C03 (+0.33) |
| C05 Zonen: Arbeiten vorn, Schlafen hinten | 0.50 × 1.5 | 6.2 | 0.00 | 1.71 | **Konflikt** mit K02 (+1.50), C09 (+0.72), C03 (+0.33) |
| C01 Nicht in der Chi-Bahn Tür ↔ Fenster | 0.25 × 2.0 | 4.0 | 0.18 | 0.13 | **Raum** |
| C02 Spiegel richtig platzieren | 0.20 × 2.0 | 3.2 | 0.20 | 0.00 | **Raum** |
| L03 Drei von vier Ecken beleuchten | 0.30 × 0.8 | 1.9 | 0.30 | -0.00 | **Raum** |
| K16 Bett zentral & symmetrisch | 0.35 × 0.6 | 1.6 | 0.00 | 11.50 | **Konflikt** mit K01 (+3.00), K03 (+2.25), C02 (+1.60) |

- **Strafe allein** = Strafe, wenn nur diese Regel (plus die harten Regeln) optimiert wird. > 0 → im Raum nicht erfüllbar.
- **Preis fürs Erfüllen** = so viel gewichtete Strafe kommt bei den anderen Regeln dazu, wenn man diese Regel erfüllt (bester bekannter Grundriss, der sie erfüllt). In Klammern die Regeln, die am meisten verlieren. Ist der Preis größer als die eigene Strafe × Gewicht, lohnt sich das Erfüllen nach dem Buch nicht.
- **kostet Punkte** = so viel höher wäre der Score, wenn nur diese eine Strafe wegfiele.

## Was man damit machen kann

- **Raum:** nichts am Grundriss zu ändern – im Bericht die *Abhilfe* aus dem Buch zeigen (z. B. Vorhang, hohes Kopfteil).
- **Konflikt:** Hier widersprechen sich Buchregeln in diesem Zimmer. Gute Kandidaten für die Paarvergleichs-Studie (`paarvergleich.py`): Welche der beiden Regeln ist Menschen wichtiger?
- **Suche:** Der normale Optimierer findet nicht immer das Beste. In `main.py` mehr `NEUSTARTS` verwenden oder das Ergebnis dieser Analyse nehmen.

## Grenzen

- Der Optimierer ist zufallsbasiert. „Raum“ heißt: Er hat auch allein keine Lösung gefunden – sehr wahrscheinlich, aber nicht bewiesen.
- Jeder Preis ist durch einen echten, machbaren Grundriss belegt; der wahre Preis kann aber kleiner sein.
- Die Obergrenze ist optimistisch: Sie nimmt an, dass sich alle Konflikte gleichzeitig auflösen ließen.
- Gilt für das Zimmer aus `mein_zimmer.py`; ein anderer Grundriss hat andere Konflikte.
