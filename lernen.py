"""
Machine-Learning-Schritt: Bewerte vorgeschlagene Layouts mit 0–10.
Das Modell lernt daraus, welche Regeln DIR wichtig sind, und speichert
die Gewichte in meine_bewertungen.json. main.py benutzt sie danach automatisch.

In PyCharm: Run 'lernen' – die Bilder öffnen sich, die Note gibst du in der Konsole ein.
"""
import random

from fengshui.bewertung import bericht, bewerte
from fengshui.ml import Personalisierung
from fengshui.optimierer import optimiere, zufallslayout, _nachbar
from fengshui.visualisierung import zeichne
from mein_zimmer import erstelle_layout

ANZAHL_VORSCHLAEGE = 8


def vorschlaege(layout, n, gewichte, rng):
    """Mischung aus guten Layouts und leicht 'verdorbenen' Varianten – so lernt das Modell Kontraste."""
    gute = optimiere(layout, iterationen=1200, neustarts=max(2, n // 2), gewichte=gewichte,
                     anzahl_ergebnisse=n // 2, ausgabe=False)
    liste = [lay for lay, _ in gute]
    versuche = 0
    while len(liste) < n and versuche < 500:
        versuche += 1
        basis = rng.choice(liste) if liste else zufallslayout(layout, rng)
        v = basis
        for _ in range(rng.randint(2, 6)):
            v = _nachbar(v, rng, 0.8)
        if bewerte(v).machbar:          # nur umsetzbare Varianten zum Bewerten zeigen
            liste.append(v)
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
