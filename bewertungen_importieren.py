"""
Noten aus dem Bewertungsbogen ins Modell übernehmen und trainieren.

Beispiel (Terminal oder PyCharm-Run-Konfiguration mit Parametern):
    python bewertungen_importieren.py runde2 "1=7; 2=8; 3=5; 4=8; 5=7; 6=7; 7=7; 8=8"

Die Vorschläge einer Runde liegen in daten/<runde>_vorschlaege.json (mit den Regel-Merkmalen).
Die Noten landen in meine_bewertungen.json – das ist DEIN persönliches Modell.
Dieselbe Runde zweimal zu importieren ersetzt die alten Noten dieser Runde (keine Doppelten).
"""
import json
import os
import re
import sys

from fengshui.ml import Personalisierung, weiche_regel_ids


def noten_lesen(text: str) -> dict[int, float]:
    """'1=7; 2=8; 3=-' -> {1: 7.0, 2: 8.0}  ('-' = übersprungen)"""
    noten = {}
    for nr, wert in re.findall(r"(\d+)\s*[=:]\s*([\d.,]+|-)", text):
        if wert != "-":
            noten[int(nr)] = float(wert.replace(",", "."))
    return noten


def importieren(runde: str, noten: dict[int, float], datei: str = "meine_bewertungen.json") -> Personalisierung:
    with open(os.path.join("daten", f"{runde}_vorschlaege.json"), encoding="utf-8") as f:
        vorschlaege = {v["nr"]: v for v in json.load(f)["vorschlaege"]}
    pers = Personalisierung(datei)
    pers.daten = [d for d in pers.daten if d.get("runde") != runde]      # Runde neu importieren
    for nr, note in sorted(noten.items()):
        v = vorschlaege[nr]
        ids = weiche_regel_ids(v["raumtyp"])
        pers.daten.append({"raumtyp": v["raumtyp"], "merkmale": {k: v["merkmale"].get(k, 0.0) for k in ids},
                           "note": note, "runde": runde, "vorschlag": nr})
    pers.speichern()
    return pers


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    runde, text = sys.argv[1], " ".join(sys.argv[2:])
    noten = noten_lesen(text)
    pers = importieren(runde, noten)
    print(f"{len(noten)} Noten aus {runde} übernommen – insgesamt {len(pers.daten)} Bewertungen.")
    if len(pers.daten) >= 3:
        pers.trainiere()
        print()
        print(pers.vergleich())


if __name__ == "__main__":
    main()
