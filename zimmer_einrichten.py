"""
🛋 LEERES ZIMMER EINRICHTEN – Foto eines leeren Raums rein, eingerichtetes Zimmer + Einkaufsliste raus.

In PyCharm: Foto als `leeres_zimmer.jpg` in den Projektordner legen, dann
Rechtsklick auf zimmer_einrichten.py → Run 'zimmer_einrichten'.

Kein Foto zur Hand? Einfach starten: Dann wird ein nachgebautes leeres Demo-Zimmer benutzt
(ohne KI-Modelle, in etwa 20 Sekunden fertig) – gut zum Ausprobieren und für die Präsentation.

Was herauskommt (Ordner `ausgabe/`):
    …_eingerichtet.jpg           dein Foto mit Möbeln und Deko (maßstabsgetreue 3D-Skizze)
    …_eingerichtet_nummern.jpg   dasselbe mit Nummern – jede Nummer ist ein Produkt der Einkaufsliste
    …_vorher.jpg                 das leere Zimmer zum Vergleich
    …_grundriss.png              Grundriss mit denselben Nummern
    …_einkaufsliste.html         Einkaufsliste mit Begründung (Buchregel) und Shop-Links  ← öffnet sich
    …_uebersicht.png             alles auf einem Blatt

Die Shop-Links stehen in affiliate.json (deine Partner-Kennungen), die Produkte in produkte.json.

    python zimmer_einrichten.py foto.jpg --raum wohnzimmer --stil hell --budget guenstig
    python zimmer_einrichten.py --demo --raum esszimmer
"""
import argparse
import os
import subprocess
import sys

from fengshui.einrichten import RAUMTYPEN, richte_foto_ein, zimmer_einrichten
from fengshui.katalog import BUDGETS, STILE
from fengshui.ml import Personalisierung
from fengshui.modell import Bewohner

FOTO = "leeres_zimmer.jpg"
RAUMTYP = "schlafzimmer"          # schlafzimmer | gaestezimmer | kinderzimmer | wohnzimmer | esszimmer | buero | studio
STIL = "natur"                    # natur (Eiche, Beige) | hell (Birke, Hellgrau) | dunkel (Nussbaum, Anthrazit)
BUDGET = "mittel"                 # guenstig | mittel | gehoben
PAAR = False                      # zwei Personen im Bett? → breiteres Bett
PFLANZEN_SIND_FREUNDE = False     # Buch: im Schlafzimmer nur Pflanzen, wenn sie dir Ruhe geben
MIT_TV = True                     # Wohnzimmer: Lowboard für den Fernseher einplanen?
BEKANNTE_BREITE = None            # optional: gemessene Raumbreite in m (macht die Maße genauer)
KI_BILD = False                   # experimentell: fotorealistischeres Bild mit generativer KI (braucht GPU)


def oeffnen(pfad: str) -> None:
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", pfad], check=False)
        elif os.name == "nt":
            os.startfile(pfad)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", pfad], check=False)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description="Leeres Zimmer nach Feng Shui einrichten")
    ap.add_argument("foto", nargs="?", default=FOTO)
    ap.add_argument("--raum", default=RAUMTYP, choices=RAUMTYPEN)
    ap.add_argument("--stil", default=STIL, choices=list(STILE))
    ap.add_argument("--budget", default=BUDGET, choices=list(BUDGETS))
    ap.add_argument("--breite", type=float, default=BEKANNTE_BREITE, help="bekannte Raumbreite in m")
    ap.add_argument("--demo", action="store_true", help="nachgebautes leeres Zimmer statt Foto")
    ap.add_argument("--nicht-oeffnen", action="store_true")
    a = ap.parse_args()

    bewohner = Bewohner(paar=PAAR, pflanzen_sind_freunde=PFLANZEN_SIND_FREUNDE)
    gewichte = Personalisierung().gewichte
    demo = a.demo or not os.path.exists(a.foto)
    if demo:
        if not a.demo:
            print(f"Kein Foto '{a.foto}' gefunden – ich nehme das nachgebaute Demo-Zimmer.\n")
        from fengshui.demo_zimmer import demo_vermessung
        rgb, v, _ = demo_vermessung(a.raum)
        print("Richte das Demo-Zimmer ein …")
        r = richte_foto_ein(rgb, v, a.raum, a.stil, a.budget, bewohner, gewichte, stamm=f"demo_{a.raum}",
                            mit_tv=MIT_TV)
    else:
        print(f"Vermesse {a.foto} … (beim ersten Mal werden die KI-Modelle geladen, ~450 MB)")
        r = zimmer_einrichten(a.foto, a.raum, a.stil, a.budget, bewohner=bewohner, gewichte=gewichte,
                              bekannte_breite=a.breite, mit_tv=MIT_TV, realistisch=KI_BILD)

    e = r["einrichtung"]
    print()
    print(e.text())
    print("\nDateien:")
    for name, pfad in r["dateien"].items():
        print(f"  {pfad}")
    if not a.nicht_oeffnen:
        oeffnen(os.path.abspath(r["dateien"]["einkaufsliste.html"]))


if __name__ == "__main__":
    main()
