"""Exportiert die komplette Regelbasis als Markdown-Katalog und JSON."""
import json

from fengshui import wissen
from fengshui.regeln import REGELN


def main():
    zeilen = ["# Feng-Shui-Regelbasis", "",
              "| ID | Kategorie | Gewicht | Regel | Gilt für | Quelle |", "|---|---|---|---|---|---|"]
    for r in REGELN:
        zeilen.append(f"| {r.id} | {r.kategorie} | {r.gewicht} | **{r.titel}** – {r.beschreibung} | "
                      f"{', '.join(sorted(r.raumtypen)) if r.raumtypen else 'alle'} | {r.quelle} |")
    with open("regelbasis.md", "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen) + "\n")

    daten = {
        "regeln": [{"id": r.id, "titel": r.titel, "beschreibung": r.beschreibung, "quelle": r.quelle,
                    "kategorie": r.kategorie, "gewicht": r.gewicht,
                    "raumtypen": sorted(r.raumtypen) if r.raumtypen else None} for r in REGELN],
        "wissen": {"elemente": wissen.ELEMENTE, "erzeugung": wissen.ERZEUGUNG, "kontrolle": wissen.KONTROLLE,
                   "himmelsrichtung": wissen.HIMMELSRICHTUNG, "raum_profil": wissen.RAUM_PROFIL,
                   "licht": wissen.LICHT, "pflanzen": wissen.PFLANZEN, "spiegel": wissen.SPIEGEL,
                   "stauraum": wissen.STAURAUM, "objekte": wissen.OBJEKTE, "moebel": wissen.MOEBEL_WISSEN},
    }
    with open("regelbasis.json", "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)
    print(f"{len(REGELN)} Regeln -> regelbasis.md und regelbasis.json")


if __name__ == "__main__":
    main()
