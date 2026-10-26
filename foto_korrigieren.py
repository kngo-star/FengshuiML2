"""
Foto deines Zimmers rein → dasselbe Foto mit den Möbeln an der besseren Position raus.

    python foto_korrigieren.py mein_zimmer.jpg --raum schlafzimmer

Ablauf: YOLOE erkennt Möbel → Tiefenmodell vermisst den Raum → Regelbasis findet Probleme →
Minimal-Korrektur verschiebt nur, was nötig ist → Möbel werden im Foto verschoben (Lücke per LaMa-KI gefüllt).
Ergebnisse in ./ausgabe/: foto_korrigiert.jpg, foto_aenderungen.jpg, foto_vorher_nachher.png

Hinweis: Gedrehte Möbel können aus einem Foto nicht realistisch gedreht werden – sie erscheinen als
grüner 3D-Umriss mit „drehen“. Möbel, die vom Bildrand abgeschnitten sind, bleiben stehen.
"""
import argparse

from fengshui.bewertung import bericht
from fengshui.foto_korrektur import foto_korrigieren
from fengshui.ml import Personalisierung
from fengshui.modell import Bewohner

FOTO = "mein_zimmer.jpg"
RAUMTYP = "auto"            # "auto" = selbst erkennen, sonst z. B. "schlafzimmer"
PAAR = False                # zwei Personen im Bett?
SUCHT_PARTNER = False
UMSTELL_AUFWAND = 4.0       # höher = es wird weniger verschoben (Punkte pro Meter Verschieben)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("foto", nargs="?", default=FOTO)
    ap.add_argument("--raum", default=RAUMTYP)
    ap.add_argument("--breite", type=float, default=None, help="bekannte Raumbreite in m (optional)")
    ap.add_argument("--von-tuer", action="store_true", help="Foto aus der Tür heraus aufgenommen")
    ap.add_argument("--aufwand", type=float, default=UMSTELL_AUFWAND)
    a = ap.parse_args()

    print(f"Analysiere {a.foto} … (erster Start lädt YOLOE, Tiefen- und LaMa-Modell)")
    r = foto_korrigieren(a.foto, a.raum, bewohner=Bewohner(paar=PAAR, sucht_partner=SUCHT_PARTNER),
                         gewichte=Personalisierung().gewichte, foto_von_tuer=a.von_tuer,
                         bekannte_breite=a.breite, preis_pro_meter=a.aufwand)
    v = r["vermessung"]
    print(f"\nRaum ca. {v.layout.raum.breite:.2f} × {v.layout.raum.tiefe:.2f} m")
    for h in v.hinweise:
        print("  •", h)
    print(f"\nScore vorher {r['vorher'].score:.0f} → nachher {r['nachher'].score:.0f}")
    print("\nÄnderungen:" if r["legende"] else "\nKeine Änderungen nötig.")
    for zeile in r["legende"]:
        print("  ", zeile)
    print("\n" + bericht(r["layout_neu"], r["nachher"]))
    print(f"\nErkannter Raumtyp: {r['raumtyp']}")
    print("Gespeichert:", ", ".join(r["dateien"].values()))


if __name__ == "__main__":
    main()
