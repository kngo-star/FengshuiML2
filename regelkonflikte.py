"""
Welche Regeln blockieren sich gegenseitig? – und wie gut ist der Score wirklich?

In PyCharm: Rechtsklick auf regelkonflikte.py → Run 'regelkonflikte'  (ca. 1–2 Minuten)
Benutzt das Zimmer aus mein_zimmer.py. Ergebnis: Konsole + auswertung/regelkonflikte.md

Für jede Regel, die im besten Grundriss noch verletzt ist, sagt das Skript, WARUM:
  Raum      – auch allein nicht erfüllbar (z. B. jede passende Wand hat ein Fenster)
  Konflikt  – erfüllbar, kostet aber andere Regeln mehr, als es bringt (Partner und Preis werden genannt)
  Suche     – der Optimierer hatte einen besseren Grundriss übersehen
Dazu: relativer Score (Prozent der Obergrenze) und Obergrenze für dieses Zimmer.
"""
import os
import time
from datetime import datetime

from fengshui.konflikte import analysiere_konflikte, relativer_score
from mein_zimmer import erstelle_layout

ITERATIONEN = 2000
NEUSTARTS = 4
SEED = 2026
DATEI = os.path.join("auswertung", "regelkonflikte.md")


def main():
    layout = erstelle_layout()
    start = time.time()
    k = analysiere_konflikte(layout, iterationen=ITERATIONEN, neustarts=NEUSTARTS, seed=SEED)
    dauer = time.time() - start
    print()
    print(k.text())

    anzahl = {a: sum(x.art == a for x in k.konflikte) for a in ("raum", "konflikt", "suche")}
    z = ["# Regelkonflikte", "",
         f"Erzeugt mit `regelkonflikte.py` am {datetime.now():%d.%m.%Y %H:%M} (Seed {SEED}, "
         f"{NEUSTARTS} Läufe × {ITERATIONEN} Schritte pro Experiment, {dauer:.0f} s).", "",
         "## Wie gut ist der Score wirklich?", "",
         "| | Score |", "|---|---|",
         f"| Optimierer, zwei normale Durchgänge (bester) | {k.start_score:.1f} |",
         f"| Unterschied zwischen den beiden Durchgängen | {k.rauschen:.1f} |",
         f"| Bester Grundriss nach der Analyse | {k.bestwert:.1f} |",
         f"| Obergrenze, wenn nur die Grenzen des Raums übrig blieben | {k.obergrenze:.1f} |",
         f"| erreicht von der Obergrenze | {relativer_score(k.bestwert, k.obergrenze):.0f} % |", "",
         "100 Punkte gibt es nur, wenn keine einzige weiche Regel verletzt ist. In einem echten Zimmer geht das "
         "meist nicht – ein Score sollte darum immer **relativ zum Bestwert desselben Zimmers** gelesen werden "
         "(`relativer_score()` in `fengshui/konflikte.py`).", "",
         "## Warum sind diese Regeln im besten Grundriss verletzt?", "",
         f"{anzahl['raum']}× liegt es am Raum, {anzahl['konflikt']}× an einem Konflikt mit anderen Regeln, "
         f"{anzahl['suche']}× hatte der Optimierer einen besseren Grundriss übersehen.", "",
         k.markdown(), "",
         "- **Strafe allein** = Strafe, wenn nur diese Regel (plus die harten Regeln) optimiert wird. > 0 → im Raum nicht erfüllbar.",
         "- **Preis fürs Erfüllen** = so viel gewichtete Strafe kommt bei den anderen Regeln dazu, wenn man diese Regel "
         "erfüllt (bester bekannter Grundriss, der sie erfüllt). In Klammern die Regeln, die am meisten verlieren. "
         "Ist der Preis größer als die eigene Strafe × Gewicht, lohnt sich das Erfüllen nach dem Buch nicht.",
         "- **kostet Punkte** = so viel höher wäre der Score, wenn nur diese eine Strafe wegfiele.", "",
         "## Was man damit machen kann", "",
         "- **Raum:** nichts am Grundriss zu ändern – im Bericht die *Abhilfe* aus dem Buch zeigen "
         "(z. B. Vorhang, hohes Kopfteil).",
         "- **Konflikt:** Hier widersprechen sich Buchregeln in diesem Zimmer. Gute Kandidaten für die "
         "Paarvergleichs-Studie (`paarvergleich.py`): Welche der beiden Regeln ist Menschen wichtiger?",
         "- **Suche:** Der normale Optimierer findet nicht immer das Beste. In `main.py` mehr `NEUSTARTS` "
         "verwenden oder das Ergebnis dieser Analyse nehmen.", "",
         "## Grenzen", "",
         "- Der Optimierer ist zufallsbasiert. „Raum“ heißt: Er hat auch allein keine Lösung gefunden – sehr "
         "wahrscheinlich, aber nicht bewiesen.",
         "- Jeder Preis ist durch einen echten, machbaren Grundriss belegt; der wahre Preis kann aber kleiner sein.",
         "- Die Obergrenze ist optimistisch: Sie nimmt an, dass sich alle Konflikte gleichzeitig auflösen ließen.",
         "- Gilt für das Zimmer aus `mein_zimmer.py`; ein anderer Grundriss hat andere Konflikte."]
    os.makedirs("auswertung", exist_ok=True)
    with open(DATEI, "w", encoding="utf-8") as f:
        f.write("\n".join(z) + "\n")
    print(f"\nGespeichert: {DATEI}  ({dauer:.0f} s)")


if __name__ == "__main__":
    main()
