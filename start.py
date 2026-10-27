"""
▶ EINFACH STARTEN – Foto rein, korrigiertes Foto raus.

In PyCharm: Rechtsklick auf start.py → Run 'start'. Danach einfach Fotos in den Ordner
`fotos_rein` legen (z. B. per Drag & Drop im Finder). Das Programm

  1. erkennt selbst, welches Zimmer es ist (Schlafzimmer, Wohnzimmer, Büro, Küche, Bad …),
  2. vermisst den Raum aus dem Foto,
  3. findet, welche Möbel nach Feng Shui schlecht stehen,
  4. verschiebt nur diese – so wenig wie möglich,
  5. legt das korrigierte Foto in `fotos_raus` und öffnet es direkt.

Es läuft weiter und wartet auf neue Fotos, bis du oben auf ■ (Stop) klickst.
Erlaubt: .jpg, .jpeg, .png, .heic (iPhone), .tiff, .webp, .bmp. Fotos bleiben auf deinem Computer (nicht auf GitHub).
"""
import os
import subprocess
import sys
import time
import traceback

EINGANG = "fotos_rein"
AUSGANG = "fotos_raus"
ENDUNGEN = (".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff", ".bmp")
AUTOMATISCH_OEFFNEN = True
WARTEN_SEKUNDEN = 2


def oeffnen(pfad: str) -> None:
    """Ergebnis mit dem Standardprogramm des Computers anzeigen."""
    if not AUTOMATISCH_OEFFNEN:
        return
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", pfad], check=False)
        elif os.name == "nt":
            os.startfile(pfad)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", pfad], check=False)
    except Exception:
        pass


def erledigt(stamm: str) -> bool:
    return any(os.path.exists(os.path.join(AUSGANG, f"{stamm}{e}"))
               for e in ("_korrigiert.jpg", "_FEHLER.txt"))


def verarbeite(pfad: str) -> None:
    from fengshui.foto_korrektur import foto_korrigieren
    from fengshui.ml import Personalisierung

    stamm = os.path.splitext(os.path.basename(pfad))[0]
    print(f"\n📷 {os.path.basename(pfad)} – wird analysiert …")
    start = time.time()
    try:
        r = foto_korrigieren(pfad, "auto", ausgabe_ordner=AUSGANG, gewichte=Personalisierung().gewichte,
                             zeigen=False)
    except Exception as fehler:
        text = (f"Das Foto konnte nicht ausgewertet werden:\n{fehler}\n\n"
                "Tipps: aus einer Zimmerecke diagonal fotografieren, Weitwinkel (0,5×), Boden und mindestens "
                "zwei Wände im Bild, Raum hell, Handy gerade halten.\n\n" + traceback.format_exc())
        with open(os.path.join(AUSGANG, f"{stamm}_FEHLER.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        print(f"   ✗ Fehler: {fehler}  (Details in {AUSGANG}/{stamm}_FEHLER.txt)")
        return

    v = r["vermessung"]
    print(f"   Raum: {r['raumtyp']}, ca. {v.layout.raum.breite:.1f} × {v.layout.raum.tiefe:.1f} m "
          f"– fertig in {time.time() - start:.0f} s")
    print(f"   Score vorher {r['vorher'].score:.0f} → nachher {r['nachher'].score:.0f}")
    for zeile in r["legende"] or ["Alles gut – nichts muss verschoben werden."]:
        print("   ", zeile)
    with open(os.path.join(AUSGANG, f"{stamm}_bericht.txt"), "w", encoding="utf-8") as f:
        from fengshui.bewertung import bericht
        f.write(f"Raumtyp: {r['raumtyp']}\nScore vorher {r['vorher'].score:.0f} → nachher {r['nachher'].score:.0f}\n\n")
        f.write("\n".join(r["legende"]) + "\n\nHinweise zur Vermessung:\n")
        f.write("\n".join("• " + h for h in v.hinweise) + "\n\n")
        f.write(bericht(r["layout_neu"], r["nachher"]))
    oeffnen(r["dateien"]["vorher_nachher"])


def main():
    os.makedirs(EINGANG, exist_ok=True)
    os.makedirs(AUSGANG, exist_ok=True)
    print("=" * 64)
    print(f" Lege Fotos in den Ordner  '{os.path.abspath(EINGANG)}'")
    print(f" Ergebnisse erscheinen in  '{os.path.abspath(AUSGANG)}'")
    print(" Beim ersten Foto werden die KI-Modelle geladen (~600 MB, einmalig).")
    print(" Beenden: oben auf ■ (Stop) klicken.")
    print("=" * 64)
    oeffnen(os.path.abspath(EINGANG))      # Ordner im Finder öffnen, damit man Fotos hineinziehen kann
    gemeldet = False
    ignoriert: set[str] = set()
    while True:
        for f in os.listdir(EINGANG):
            if not f.startswith(".") and not f.lower().endswith(ENDUNGEN) and f not in ignoriert \
                    and os.path.isfile(os.path.join(EINGANG, f)):
                print(f"\n⚠ '{f}' wird übersprungen – kein Bildformat, das ich lesen kann "
                      f"(erlaubt: {', '.join(ENDUNGEN)})")
                ignoriert.add(f)
        neu = sorted(f for f in os.listdir(EINGANG)
                     if f.lower().endswith(ENDUNGEN) and not f.startswith(".")
                     and not erledigt(os.path.splitext(f)[0]))
        for name in neu:
            pfad = os.path.join(EINGANG, name)
            groesse = os.path.getsize(pfad)
            time.sleep(1)                      # warten, bis das Kopieren fertig ist
            if os.path.getsize(pfad) != groesse:
                continue
            verarbeite(pfad)
            gemeldet = False
        if not gemeldet:
            print("\n⏳ Warte auf neue Fotos …")
            gemeldet = True
        time.sleep(WARTEN_SEKUNDEN)


if __name__ == "__main__":
    main()
