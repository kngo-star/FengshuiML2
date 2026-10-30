"""
Machine-Learning-Schritt: Bewerte vorgeschlagene Layouts mit 0–10.
Das Modell lernt daraus, welche Regeln DIR wichtig sind, und speichert
die Gewichte in meine_bewertungen.json. main.py benutzt sie danach automatisch.

In PyCharm: Run 'lernen' – die Bilder öffnen sich, die Note gibst du in der Konsole ein.
"""
import random

from fengshui.bewertung import bericht, bewerte
from fengshui.ml import Personalisierung
from fengshui.optimierer import deutlich_verschieden, optimiere
from fengshui.regeln import REGELN
from fengshui.visualisierung import zeichne
from mein_zimmer import erstelle_layout

ANZAHL_VORSCHLAEGE = 8


def _anderer_geschmack(gewichte, rng):
    """Zufällig veränderte Gewichte der weichen Regeln: ein „anderer Geschmack“ (manche Regeln egal, manche 3×)."""
    basis = {r.id: (gewichte or {}).get(r.id, r.gewicht) for r in REGELN if r.kategorie != "hart"}
    return {k: w * rng.choice([0.0, 0.5, 1.0, 2.0, 3.0]) for k, w in basis.items()}


def vorschlaege(layout, n, gewichte, rng):
    """n wirklich verschiedene, umsetzbare und logische Vorschläge zum Bewerten.

    Alle Vorschläge erfüllen sämtliche harten Regeln (nichts verdeckt, Schränke an der Wand, Tisch benutzbar …).
    Hälfte: die besten nach dem aktuellen Modell. Andere Hälfte: die besten für einen zufällig veränderten
    Geschmack – plausibel, aber mit anderen Schwerpunkten. So lernt das Modell, welche Regeln DIR wichtig sind.
    Zwei Vorschläge gelten nur als verschieden, wenn mindestens ein großes Möbel ≥ 1 m woanders steht oder
    anders gedreht ist.
    """
    liste = []

    def aufnehmen(lay):
        if bewerte(lay, gewichte).machbar and all(deutlich_verschieden(lay, x, min_weg=1.0) for x in liste):
            liste.append(lay)

    gute = optimiere(layout, iterationen=1200, neustarts=n, gewichte=gewichte, anzahl_ergebnisse=n,
                     seed=rng.randrange(10 ** 9), ausgabe=False)
    for lay, _ in gute:
        if len(liste) >= (n + 1) // 2:
            break
        aufnehmen(lay)
    versuche = 0
    while len(liste) < n and versuche < 40:
        versuche += 1
        lay, _ = optimiere(layout, iterationen=900, neustarts=1, gewichte=_anderer_geschmack(gewichte, rng),
                           anzahl_ergebnisse=1, seed=rng.randrange(10 ** 9), ausgabe=False)[0]
        aufnehmen(lay)
    rng.shuffle(liste)
    return liste


def main():
    layout = erstelle_layout()
    pers = Personalisierung()
    rng = random.Random()
    print(f"Bisher {len(pers.daten)} Bewertungen gespeichert.\n")
    for i, lay in enumerate(vorschlaege(layout, ANZAHL_VORSCHLAEGE, pers.gewichte, rng), 1):
        print(bericht(lay))
        zeichne(lay, f"Vorschlag {i} – wie fühlt sich das an?", zeigen=True)
        while True:
            eingabe = input(f"Note für Vorschlag {i} (0–10, leer = überspringen, q = fertig): ").strip()
            if eingabe in ("", "q"):
                break
            try:
                note = float(eingabe.replace(",", "."))
                if 0 <= note <= 10:
                    pers.bewertung_hinzufuegen(lay, note)
                    break
            except ValueError:
                pass
            print("Bitte eine Zahl zwischen 0 und 10.")
        if eingabe == "q":
            break

    if len(pers.daten) >= 3:
        pers.trainiere()
        print()
        print(pers.vergleich())
        print("\nGespeichert. Starte jetzt main.py – der Optimierer nutzt deine Gewichte.")
    else:
        print("Für das Training sind mindestens 3 Bewertungen nötig.")


if __name__ == "__main__":
    main()
