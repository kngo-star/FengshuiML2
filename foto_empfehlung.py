"""
Foto deines Zimmers -> YOLO erkennt die Möbel -> Feng-Shui-Empfehlungen.

In PyCharm: unten FOTO und RAUMTYP setzen, dann Run 'foto_empfehlung'.
Oder im Terminal:  python foto_empfehlung.py mein_zimmer.jpg --raum schlafzimmer --optimieren

Beim ersten Start lädt ultralytics die Modellgewichte automatisch herunter (~25–50 MB).
Tipps fürs Foto: aus der Tür heraus fotografieren (das ist auch der "erste Eindruck"),
Weitwinkel, Raum hell, möglichst viel vom Bett/Schreibtisch und den Fenstern im Bild.
"""
import argparse
import os

from fengshui.ausstattung import drucke_ausstattung
from fengshui.bewertung import bericht
from fengshui.foto import (erkenne, foto_empfehlungen, speichere_erkennungen, text_bericht,
                           zeichne_erkennungen, zu_moebelliste, zu_profil)

FOTO = "mein_zimmer.jpg"
RAUMTYP = "schlafzimmer"          # schlafzimmer | buero | wohnzimmer | esszimmer | kinderzimmer | studio
MODELL = "yoloe-11s-seg.pt"       # YOLOE mit Text-Prompts (erkennt Schrank, Spiegel, Fenster …)
                                  # Alternativen: "yoloe-11m-seg.pt" (genauer), "yolov8s-world.pt", "yolo11n.pt" (nur COCO)
CONF = 0.2                        # Mindest-Sicherheit; höher = weniger, aber sicherere Erkennungen
OPTIMIEREN = False                # True: erkannte Möbel + Raummaße aus mein_zimmer.py -> Optimierer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("foto", nargs="?", default=FOTO)
    ap.add_argument("--raum", default=RAUMTYP)
    ap.add_argument("--modell", default=MODELL)
    ap.add_argument("--conf", type=float, default=CONF)
    ap.add_argument("--optimieren", action="store_true", default=OPTIMIEREN)
    a = ap.parse_args()

    if not os.path.exists(a.foto):
        raise SystemExit(f"Foto '{a.foto}' nicht gefunden – lege es in den Projektordner oder gib den Pfad an.")

    os.makedirs("ausgabe", exist_ok=True)
    print(f"Analysiere {a.foto} mit {a.modell} …")
    erk, groesse = erkenne(a.foto, a.modell, a.conf)
    speichere_erkennungen(erk, groesse, "ausgabe/erkennungen.json")
    zeichne_erkennungen(a.foto, erk, "ausgabe/foto_erkennung.jpg")

    hinweise = foto_empfehlungen(erk, groesse, a.raum)
    print()
    print(text_bericht(erk, hinweise))

    profil = {k: v for k, v in zu_profil(erk, a.raum).items() if v is not None}
    from mein_zimmer import erstelle_layout
    layout = erstelle_layout()
    layout.raum.raumtyp = a.raum
    print("\n=== Ausstattungs-Check (aus dem Foto abgeleitet) ===")
    print(drucke_ausstattung(layout.raum, profil))

    moebel = zu_moebelliste(erk)
    print("\n=== Erkannte Möbel als Liste für mein_zimmer.py (Standardmaße – bitte nachmessen!) ===")
    for m in moebel:
        extra = f', gehoert_zu="{m.gehoert_zu}", seite="{m.seite}"' if m.gehoert_zu else ""
        print(f'    Moebel("{m.typ}", breite={m.breite}, tiefe={m.tiefe}, hoehe={m.hoehe}, name="{m.name}"{extra}),')

    if a.optimieren and moebel:
        from fengshui.optimierer import optimiere
        from fengshui.visualisierung import zeichne_mehrere
        layout.moebel = moebel
        print(f"\nOptimiere mit den Raummaßen aus mein_zimmer.py ({layout.raum.breite} × {layout.raum.tiefe} m) …")
        erg = optimiere(layout)
        print(bericht(*erg[0]))
        zeichne_mehrere(erg, datei="ausgabe/foto_vorschlaege.png", zeigen=True)

    print("\nGespeichert: ausgabe/foto_erkennung.jpg, ausgabe/erkennungen.json")


if __name__ == "__main__":
    main()
