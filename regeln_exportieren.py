"""
Exportiert die komplette Regelbasis:
  regelbasis.md   – lesbarer Katalog aller Buchregeln (WENN → DANN, Warum, Abhilfe, Prüfung)
  regelbasis.json – maschinenlesbar (für Programme, ML oder ein Sprachmodell)
"""
import json
from collections import defaultdict
from dataclasses import asdict

from fengshui import wissen
from fengshui.buchregeln import BUCHREGELN, abdeckung
from fengshui.regeln import REGELN

ART_NAME = {"grundriss": "🟢 Grundriss (automatisch)", "foto": "🔵 Foto (automatisch)",
            "profil": "🟣 Profil (aus deinen Angaben)", "tipp": "⚪ Tipp"}
PRIO_NAME = {1: "wichtig", 2: "mittel", 3: "klein"}


def main():
    ab = abdeckung()
    z = ["# Feng-Shui-Regelbasis", "",
         "Alle Regeln aus dem Buch, sinngemäß als **WENN → DANN**-Regeln erfasst (Quelle: `fengshui/buchregeln.py`).",
         "",
         f"**{ab['gesamt']} Buchregeln** – davon {ab.get('grundriss', 0)} im Grundriss, {ab.get('foto', 0)} im Foto "
         f"und {ab.get('profil', 0)} über das Profil automatisch geprüft ({ab['automatisch']} gesamt); "
         f"{ab.get('tipp', 0)} erscheinen als Tipp im Bericht.", "",
         "Prüfart: " + " · ".join(ART_NAME.values()), ""]
    nach_kapitel = defaultdict(list)
    for r in BUCHREGELN:
        nach_kapitel[r.kapitel].append(r)
    z.append("## Inhalt")
    z += [f"- [{k}](#{k.lower().replace(' ', '-').replace('–', '').replace('&', '')}) ({len(v)})"
          for k, v in nach_kapitel.items()]
    z.append("")
    for kap, regeln in nach_kapitel.items():
        z += [f"## {kap}", ""]
        for r in regeln:
            raeume = "alle Räume" if "alle" in r.raeume else ", ".join(r.raeume)
            z.append(f"### {r.id} · {r.thema}  ({PRIO_NAME[r.prio]}, {ART_NAME[r.art]})")
            z.append(f"- **WENN** {r.wenn}")
            z.append(f"- **DANN** {r.dann}")
            if r.warum:
                z.append(f"- **Warum:** {r.warum}")
            if r.abhilfe:
                z.append(f"- **Abhilfe:** {r.abhilfe}")
            details = [f"Räume: {raeume}"]
            if r.pruefung:
                details.append("Prüfung: " + ", ".join(f"`{p}`" for p in r.pruefung))
            if r.profil:
                details.append("Profil: " + ", ".join(f"`{k} {op} {v}`" if v is not None else f"`{k}`"
                                                      for k, op, v in r.profil))
            z.append(f"- <sub>{' · '.join(details)}</sub>")
            z.append("")
    z += ["## Anhang: Automatische Prüfungen im Code", "",
          "| ID | Kategorie | Gewicht | Prüfung | Buchregeln |", "|---|---|---|---|---|"]
    for c in REGELN:
        buch = [r.id for r in BUCHREGELN if f"grundriss:{c.id}" in r.pruefung]
        z.append(f"| {c.id} | {c.kategorie} | {c.gewicht} | **{c.titel}** | {', '.join(buch)} |")
    with open("regelbasis.md", "w", encoding="utf-8") as f:
        f.write("\n".join(z) + "\n")

    daten = {
        "beschreibung": "Feng-Shui-Regelbasis (Form-Schule) als WENN-DANN-Regeln. Felder: wenn = Bedingung, "
                        "dann = Empfehlung, warum = Begründung, abhilfe = Alternative, prio 1-3, "
                        "pruefung = automatische Prüfung im Code, profil = Bedingungen auf den Nutzerangaben.",
        "abdeckung": ab,
        "buchregeln": [{**asdict(r), "art": r.art} for r in BUCHREGELN],
        "pruefungen": [{"id": c.id, "titel": c.titel, "beschreibung": c.beschreibung, "kategorie": c.kategorie,
                        "gewicht": c.gewicht, "raumtypen": sorted(c.raumtypen) if c.raumtypen else None}
                       for c in REGELN],
        "wissen": {"elemente": wissen.ELEMENTE, "erzeugung": wissen.ERZEUGUNG, "kontrolle": wissen.KONTROLLE,
                   "himmelsrichtung": wissen.HIMMELSRICHTUNG, "raum_profil": wissen.RAUM_PROFIL,
                   "licht": wissen.LICHT, "pflanzen": wissen.PFLANZEN, "spiegel": wissen.SPIEGEL,
                   "stauraum": wissen.STAURAUM, "objekte": wissen.OBJEKTE, "moebel": wissen.MOEBEL_WISSEN},
    }
    with open("regelbasis.json", "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)
    print(f"{ab['gesamt']} Buchregeln ({ab['automatisch']} automatisch geprüft) und {len(REGELN)} Code-Prüfungen "
          f"-> regelbasis.md und regelbasis.json")


if __name__ == "__main__":
    main()
