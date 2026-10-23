"""
Startskript: Zimmer automatisch nach Feng-Shui-Regeln einrichten.

In PyCharm: Rechtsklick auf main.py -> Run 'main'
Dein Zimmer trägst du in mein_zimmer.py ein.
"""
import os

from fengshui.ausstattung import drucke_ausstattung
from fengshui.bewertung import bericht, bewerte
from fengshui.ml import Personalisierung
from fengshui.optimierer import optimiere
from fengshui.visualisierung import zeichne, zeichne_mehrere
from mein_zimmer import PROFIL, erstelle_layout

ITERATIONEN = 3000     # mehr = gründlicher, aber langsamer
NEUSTARTS = 6
SEED = None            # Zahl eintragen für reproduzierbare Ergebnisse


def main():
    layout = erstelle_layout()

    # Persönlich gelernte Gewichte verwenden, falls vorhanden (siehe lernen.py)
    pers = Personalisierung()
    gewichte = pers.gewichte
    if gewichte:
        print("→ Verwende deine persönlich gelernten Regel-Gewichte (meine_bewertungen.json)\n")

    # Falls im Layout schon Positionen stehen (z.B. deine aktuelle Einrichtung): erst bewerten
    if any(m.x or m.y for m in layout.moebel):
        print(bericht(layout, gewichte=gewichte))
        print()

    print(f"Suche gute Anordnungen ({NEUSTARTS} Läufe × {ITERATIONEN} Schritte) …")
    ergebnisse = optimiere(layout, iterationen=ITERATIONEN, neustarts=NEUSTARTS,
                           gewichte=gewichte, seed=SEED)

    os.makedirs("ausgabe", exist_ok=True)
    for i, (lay, erg) in enumerate(ergebnisse, 1):
        print()
        print(f"################ VARIANTE {i} ################")
        print(bericht(lay, erg))
        zeichne(lay, f"Variante {i} – Score {erg.score:.1f}", datei=f"ausgabe/variante_{i}.png", zeigen=False)

    print()
    print("=== Ausstattungs-Check (Farben, Licht, Bett, Pflanzen, Ordnung) ===")
    print(drucke_ausstattung(layout.raum, PROFIL))

    print("\nBilder gespeichert in ./ausgabe/")
    zeichne_mehrere(ergebnisse, datei="ausgabe/alle_varianten.png", zeigen=True)


if __name__ == "__main__":
    main()
