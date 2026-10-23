"""
Zimmer aus EINEM Foto vermessen – keine Meter-Eingabe nötig.

YOLOE erkennt Möbel, Türen und Fenster, "Depth Anything V2 (Metric Indoor)" schätzt die
Entfernung jedes Pixels in Metern. Daraus entstehen Raummaße und ein Grundriss deiner
JETZIGEN Einrichtung, der sofort bewertet und optimiert wird.

    python zimmer_aus_foto.py mein_zimmer.jpg --raum schlafzimmer
    python zimmer_aus_foto.py mein_zimmer.jpg --breite 3.6      # eine bekannte Länge macht es genauer

Erster Start lädt zwei Modelle herunter (~30 MB YOLOE + ~400 MB Tiefenmodell).
Bestes Foto: aus einer Zimmerecke diagonal in die gegenüberliegende Ecke, Weitwinkel (0,5×),
auf Brusthöhe, Handy gerade, Raum hell.
"""
import argparse
import os

from fengshui.bewertung import bericht, bewerte
from fengshui.foto import foto_empfehlungen, text_bericht, zeichne_erkennungen
from fengshui.foto3d import als_python_code, zeichne_vermessung, zimmer_aus_foto
from fengshui.optimierer import optimiere
from fengshui.visualisierung import zeichne_mehrere

FOTO = "mein_zimmer.jpg"
RAUMTYP = "schlafzimmer"
KAMERA_IN_ECKE = True     # du standest beim Fotografieren in einer Zimmerecke
FOTO_VON_TUER = False     # du standest in der Tür (Tür ist hinter dir, nicht im Bild)
BEKANNTE_BREITE = None    # optional: eine gemessene Länge in m (verbessert die Genauigkeit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("foto", nargs="?", default=FOTO)
    ap.add_argument("--raum", default=RAUMTYP)
    ap.add_argument("--breite", type=float, default=BEKANNTE_BREITE, help="bekannte Raumbreite in m")
    ap.add_argument("--tiefe", type=float, default=None, help="bekannte Raumtiefe in m")
    ap.add_argument("--von-tuer", action="store_true", default=FOTO_VON_TUER)
    ap.add_argument("--nicht-ecke", action="store_true")
    ap.add_argument("--fov", type=float, default=None, help="horizontaler Blickwinkel in Grad, falls EXIF fehlt")
    a = ap.parse_args()

    os.makedirs("ausgabe", exist_ok=True)
    print(f"Vermesse {a.foto} … (Tiefenschätzung kann auf CPU ~30 s dauern)")
    v, erk, _ = zimmer_aus_foto(a.foto, a.raum, kamera_in_ecke=not a.nicht_ecke, foto_von_tuer=a.von_tuer,
                                fov_grad=a.fov, bekannte_breite=a.breite, bekannte_tiefe=a.tiefe)
    r = v.layout.raum
    print(f"\n=== Raum: {r.breite:.2f} m × {r.tiefe:.2f} m, Höhe ≈ {r.hoehe:.2f} m ===")
    for h in v.hinweise:
        print("  •", h)

    import tempfile
    gerade = os.path.join(tempfile.gettempdir(), "fengshui_foto_gerade.jpg")   # EXIF-gedrehtes Foto
    zeichne_erkennungen(gerade, erk, "ausgabe/foto_erkennung.jpg")
    zeichne_vermessung(v, datei="ausgabe/vermessung.png", zeigen=True)

    print("\n=== Deine JETZIGE Einrichtung ===")
    print(bericht(v.layout))
    from PIL import Image
    groesse = Image.open(gerade).size
    print()
    print(text_bericht(erk, foto_empfehlungen(erk, groesse, a.raum)))

    print("\n=== Bessere Anordnungen ===")
    erg = optimiere(v.fuer_optimierer())
    print(bericht(*erg[0]))
    zeichne_mehrere(erg, datei="ausgabe/foto_vorschlaege.png", zeigen=True)

    print("\n=== Zum Übernehmen/Korrigieren in mein_zimmer.py ===")
    print(als_python_code(v.layout))


if __name__ == "__main__":
    main()
