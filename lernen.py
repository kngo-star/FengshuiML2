"""
Machine-Learning-Schritt: Bewerte vorgeschlagene Layouts mit 0–10.
Das Modell lernt daraus, welche Regeln DIR wichtig sind, und speichert
die Gewichte in meine_bewertungen.json. main.py benutzt sie danach automatisch.

In PyCharm: Run 'lernen' – die Bilder öffnen sich, die Note gibst du in der Konsole ein.
"""
import random

from fengshui.bewertung import bericht
from fengshui.ml import Personalisierung
from fengshui.optimierer import deutlich_verschieden, optimiere
from fengshui.visualisierung import zeichne
from mein_zimmer import erstelle_layout

ANZAHL_VORSCHLAEGE = 8


def vorschlaege(layout, n, gewichte, rng):
    """n wirklich verschiedene, umsetzbare Vorschläge zum Bewerten.

    Hälfte „gut“ (gründlich optimiert), Hälfte „mittel“ (kurz optimiert, also plausibel, aber mit Schwächen) –
    so lernt das Modell Kontraste. Zwei Vorschläge gelten nur als verschieden, wenn mindestens ein großes
    Möbel ≥ 1 m woanders steht oder anders gedreht ist (keine Mini-Verschiebungen als „neuer“ Vorschlag).
    """
    liste = []

    def aufnehmen(lay, erg):
        if erg.machbar and all(deutlich_verschieden(lay, x, min_weg=1.0) for x in liste):
            liste.append(lay)

    gute = optimiere(layout, iterationen=1200, neustarts=n, gewichte=gewichte, anzahl_ergebnisse=n,
                     seed=rng.randrange(10 ** 9), ausgabe=False)
    for lay, erg in gute:
        if len(liste) >= (n + 1) // 2:
            break
        aufnehmen(lay, erg)
    versuche = 0
    while len(liste) < n and versuche < 60:
        versuche += 1
        lay, erg = optimiere(layout, iterationen=rng.choice([40, 80, 150, 300]), neustarts=1, gewichte=gewichte,
                             anzahl_ergebnisse=1, seed=rng.randrange(10 ** 9), ausgabe=False)[0]
        aufnehmen(lay, erg)
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
