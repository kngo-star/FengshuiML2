"""
Paarvergleichs-Studie: „Welches Zimmer gefällt dir besser?“ – Bogen erstellen, Antworten sammeln, auswerten.

In PyCharm (Run-Konfiguration mit Parametern) oder im Terminal:

  python paarvergleich.py erstellen runde3        1) 8 Vorschläge erzeugen + Bewertungsbogen
                                                     → ausgabe/runde3_bogen.html (eine Datei, läuft offline,
                                                       auch auf dem Handy – einfach verschicken)
  python paarvergleich.py hinzufuegen "PV1|…"     2) Antwort-Code einer Person speichern
                                                     → daten/runde3_paarvergleich.txt (eine Zeile pro Person)
  python paarvergleich.py auswerten runde3        3) Auswertung → auswertung/paarvergleich_runde3.md + .png
  python paarvergleich.py planung                 Wie viele Personen braucht die Studie? (Simulation)

Ohne Parameter: diese Hilfe.

Datenschutz: Im Bogen nur Kürzel statt Namen eingeben lassen. Die Antwortdatei landet sonst mit Namen auf GitHub.
"""
import base64
import io
import json
import os
import random
import sys
from datetime import datetime

from fengshui.paarvergleich import (Vergleich, auswerten, code_details, code_lesen, paarplan, wilson)

ANZAHL_VORSCHLAEGE = 8      # 8 Vorschläge = 28 mögliche Paare
PAARE_PRO_PERSON = 15       # + 2 Wiederholungen zur Kontrolle ≈ 5 Minuten
WIEDERHOLUNGEN = 2
BOGEN_VORLAGE = os.path.join("fengshui", "paarbogen.html")


def _pfade(runde):
    return (os.path.join("daten", f"{runde}_vorschlaege.json"),
            os.path.join("daten", f"{runde}_paarvergleich.txt"),
            os.path.join("ausgabe", f"{runde}_bogen.html"))


# ------------------------------------------------------------------ 1) erstellen
def _bild_als_daten_url(layout, titel) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from fengshui.visualisierung import zeichne
    puffer = io.BytesIO()
    raum = layout.raum
    fig, ax = plt.subplots(figsize=(6.5, 6.5 * raum.tiefe / raum.breite + 0.6))
    zeichne(layout, titel, ax=ax)               # eigene Figur übergeben – zeichne() schließt sie dann nicht
    fig.tight_layout()
    fig.savefig(puffer, format="png", dpi=90)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(puffer.getvalue()).decode()


def bogen_schreiben(runde: str, bilder: dict, ziel: str) -> None:
    with open(BOGEN_VORLAGE, encoding="utf-8") as f:
        html = f.read()
    daten = json.dumps({"runde": runde, "bilder": bilder, "anzahl": PAARE_PRO_PERSON,
                        "wiederholungen": WIEDERHOLUNGEN})
    start, ende = html.index("/*DATEN*/"), html.index("/*ENDE*/") + len("/*ENDE*/")
    html = html[:start] + daten + html[ende:]
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    with open(ziel, "w", encoding="utf-8") as f:
        f.write(html)


def erstellen(runde: str, seed=None):
    from fengshui.bewertung import bewerte
    from fengshui.ml import merkmale
    from lernen import vorschlaege
    from mein_zimmer import erstelle_layout

    datei, _, bogen = _pfade(runde)
    if os.path.exists(datei):
        sys.exit(f"✗ {datei} gibt es schon – anderen Rundennamen wählen (sonst passen alte Antworten nicht mehr).")
    rng = random.Random(seed)
    print(f"Erzeuge {ANZAHL_VORSCHLAEGE} verschiedene, machbare Vorschläge (dauert etwa eine Minute) …")
    layouts = vorschlaege(erstelle_layout(), ANZAHL_VORSCHLAEGE, None, rng)
    liste, bilder = [], {}
    for nr, lay in enumerate(layouts, 1):
        liste.append({"nr": nr, "raumtyp": lay.raum.raumtyp, "buch_score": round(bewerte(lay).score, 2),
                      "moebel": [{"name": m.name, "x": round(m.x, 3), "y": round(m.y, 3), "rot": m.rot}
                                 for m in lay.moebel],
                      "merkmale": merkmale(lay)})
        bilder[nr] = _bild_als_daten_url(lay, f"Zimmer {nr}")
    os.makedirs("daten", exist_ok=True)
    with open(datei, "w", encoding="utf-8") as f:
        json.dump({"runde": runde, "art": "paarvergleich", "raum": "Mein Zimmer (mein_zimmer.py)",
                   "erstellt": f"{datetime.now():%Y-%m-%d}",
                   "hinweis": "Alle Vorschläge erfüllen alle harten Regeln. Bewertet wird per Paarvergleich.",
                   "vorschlaege": liste}, f, ensure_ascii=False, indent=1)
    bogen_schreiben(runde, bilder, bogen)
    print(f"✓ {datei}\n✓ {bogen}  ({os.path.getsize(bogen) / 1e6:.1f} MB) – diese Datei an die Teilnehmenden schicken.")


# ------------------------------------------------------------------ 2) hinzufügen
def hinzufuegen(code: str):
    runde, person, vergleiche = code_lesen(code)
    datei, antworten, _ = _pfade(runde)
    if not os.path.exists(datei):
        sys.exit(f"✗ Runde {runde} unbekannt ({datei} fehlt).")
    nummern = {v["nr"] for v in _lade_vorschlaege(runde)}
    falsch = [v for v in vergleiche if v.links not in nummern or v.rechts not in nummern]
    if falsch:
        sys.exit(f"✗ Code enthält Vorschläge, die es in {runde} nicht gibt.")
    zeilen = []
    if os.path.exists(antworten):
        with open(antworten, encoding="utf-8") as f:
            zeilen = [z.rstrip("\n") for z in f if z.strip() and not z.startswith("#")]
    zeilen = [z for z in zeilen if code_lesen(z)[1] != person]       # gleiche Person: ersetzen
    zeilen.append(code.strip())
    with open(antworten, "w", encoding="utf-8") as f:
        f.write("# Antwort-Codes aus dem Paarvergleichs-Bogen, eine Zeile pro Person\n")
        f.write("\n".join(zeilen) + "\n")
    print(f"✓ {len(vergleiche)} Vergleiche von {person} gespeichert – jetzt {len(zeilen)} Personen in {antworten}.")


# ------------------------------------------------------------------ 3) auswerten
def _lade_vorschlaege(runde):
    with open(_pfade(runde)[0], encoding="utf-8") as f:
        return json.load(f)["vorschlaege"]


def _lade_antworten(runde):
    datei = _pfade(runde)[1]
    if not os.path.exists(datei):
        return [], []
    vergleiche, details = [], []
    with open(datei, encoding="utf-8") as f:
        for z in f:
            if z.strip() and not z.startswith("#"):
                vergleiche += code_lesen(z)[2]
                details.append(code_details(z))
    return vergleiche, details


def _grafik(a, datei):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    farbe, tinte, raster = "#257de0", "#222222", "#e7e7e7"
    nr = sorted(a.nummern, key=lambda n: a.buch_score[n])
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for n in nr:
        lo, hi = a.intervall[n]
        ax.plot([a.buch_score[n]] * 2, [lo, hi], color=farbe, lw=2, alpha=.45, solid_capstyle="round")
    ax.scatter([a.buch_score[n] for n in nr], [a.staerke[n] for n in nr], s=64, color=farbe,
               edgecolor="white", linewidth=2, zorder=3)
    for n in nr:
        ax.annotate(f"Zimmer {n}", (a.buch_score[n], a.staerke[n]), xytext=(6, 4), textcoords="offset points",
                    fontsize=8, color=tinte)
    ax.axhline(0, color="#999999", lw=1)
    ax.set_xlabel("Buch-Score (Regelbasis)", color=tinte)
    ax.set_ylabel("Beliebtheit (Bradley-Terry-Stärke)", color=tinte)
    ax.set_title(f"Regeln vs. Gefühl – ρ = {a.rho:+.2f}, {len(a.personen)} Personen", fontsize=11, color=tinte)
    ax.grid(color=raster, lw=.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(datei, dpi=140)
    plt.close(fig)


def bericht(runde: str, a, details) -> str:
    lo, hi = wilson(a.treffer, a.entschieden)
    gleich, wdh = a.konsistent
    einig, n_einig = a.einigkeit
    z = [f"# Paarvergleich {runde}", "",
         f"Erzeugt mit `paarvergleich.py auswerten {runde}` am {datetime.now():%d.%m.%Y %H:%M}.", "",
         f"- **{len(a.personen)} Personen**, {a.anzahl} Vergleiche "
         f"(Vorwissen: {', '.join(f'{k} {sum(d['vorwissen'] == k for d in details)}' for k in ('nein', 'etwas', 'gut'))})",
         "", "## Treffen die Buchregeln das Gefühl?", "",
         "| Kennzahl | Wert | Bedeutung |", "|---|---|---|",
         f"| Trefferquote der Regeln | **{a.trefferquote:.0%}** (95 %: {lo:.0%}–{hi:.0%}), "
         f"{a.treffer} von {a.entschieden} | Wie oft gewann das Zimmer mit dem höheren Buch-Score? 50 % = Zufall |",
         f"| Rangkorrelation ρ | {a.rho:+.2f} | Reihenfolge nach Beliebtheit vs. nach Buch-Score (1 = gleich) |",
         f"| Konsistenz (Wiederholungen) | {gleich} von {wdh} gleich | Entscheidet dieselbe Person ein Paar zweimal gleich? |",
         f"| Einigkeit zwischen Personen | {einig:.0%} ({n_einig} Paar-Paare) | 50 % = Zufall, 100 % = alle einig |",
         "",
         ("**Ergebnis:** Die Regeln treffen das Gefühl besser als Zufall (das 95-%-Intervall liegt über 50 %)."
          if lo > 0.5 else
          "**Ergebnis:** Die Regeln liegen vorerst nicht klar besser als Zufall (das 95-%-Intervall schließt 50 % ein) – "
          "mehr Personen nötig (siehe `python paarvergleich.py planung`) oder die Regeln treffen das Gefühl hier nicht."),
         "", "## Rangfolge nach Beliebtheit", "",
         "| Rang | Zimmer | Stärke (95 %) | Buch-Score |", "|---|---|---|---|"]
    for i, n in enumerate(sorted(a.nummern, key=lambda n: -a.staerke[n]), 1):
        lo_n, hi_n = a.intervall[n]
        z.append(f"| {i} | {n} | {a.staerke[n]:+.2f} ({lo_n:+.2f} … {hi_n:+.2f}) | {a.buch_score[n]:.1f} |")
    z += ["", f"Grafik: `paarvergleich_{runde}.png`. Stärke 0 = durchschnittlich; +0,7 heißt etwa: gewinnt gegen ein "
          "durchschnittliches Zimmer in 2 von 3 Fällen.", ""]
    g = a.gewichte
    if g and g.get("n"):
        z += ["## Welche Regeln erklären die Entscheidungen? (Machine Learning)", "",
              "Logistisches Modell: Unterschied der Regel-Strafen zweier Zimmer → Wahrscheinlichkeit, dass das linke "
              "gewinnt. Gewichte ≥ 0. **Nur Bericht – die Regeln werden nicht verändert.**", ""]
        if g.get("genauigkeit_modell") is not None:
            z += [f"Leave-one-person-out (Modell ohne die Person trainiert, ihre Entscheidungen vorhergesagt): "
                  f"Modell **{g['genauigkeit_modell']:.0%}**, Buch-Gewichte {g['genauigkeit_buch']:.0%} "
                  f"({g['n']} Entscheidungen, {g['personen']} Personen).", ""]
        else:
            z += ["(Für eine Prüfung mit Leave-one-person-out braucht es mindestens 2 Personen.)", ""]
        top = sorted(((k, w) for k, w in g["gewichte"].items() if w > 1e-3), key=lambda kw: -kw[1])[:10]
        if top:
            z += ["| Regel | Gewicht |", "|---|---|"] + [f"| {k} | {w:.2f} |" for k, w in top]
        else:
            z.append("Kein Regelunterschied erklärt die Entscheidungen (alle Gewichte 0).")
        z.append("")
    kommentare = [d for d in details if d["kommentar"]]
    if kommentare:
        z += ["## Kommentare", ""] + [f"- **{d['person']}:** {d['kommentar']}" for d in kommentare] + [""]
    z += ["## Grenzen", "",
          "- Alle Vorschläge stammen aus einem Zimmer (`mein_zimmer.py`).",
          "- Bei weniger als etwa 20 Personen sind die Intervalle breit; einzelne Ränge nicht überinterpretieren.",
          "- Das ML-Modell hat mehr Gewichte als Vorschläge – es zeigt Tendenzen, keine gesicherten Gewichte.",
          "- Gemessen wird Vorliebe, nicht eine Wirkung von Feng Shui."]
    return "\n".join(z) + "\n"


def auswerten_runde(runde: str):
    from fengshui.ml import weiche_regel_ids
    from fengshui.regeln import REGELN
    vorschlaege = _lade_vorschlaege(runde)
    vergleiche, details = _lade_antworten(runde)
    if not vergleiche:
        sys.exit(f"✗ Noch keine Antworten in {_pfade(runde)[1]} – erst mit `hinzufuegen` Codes speichern.")
    ids = set(weiche_regel_ids(vorschlaege[0]["raumtyp"]))
    buch = {r.id: r.gewicht for r in REGELN if r.id in ids}
    a = auswerten(vergleiche, vorschlaege, buch)
    os.makedirs("auswertung", exist_ok=True)
    md = os.path.join("auswertung", f"paarvergleich_{runde}.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write(bericht(runde, a, details))
    _grafik(a, os.path.join("auswertung", f"paarvergleich_{runde}.png"))
    lo, hi = wilson(a.treffer, a.entschieden)
    print(f"{len(a.personen)} Personen, {a.anzahl} Vergleiche: Trefferquote der Regeln {a.trefferquote:.0%} "
          f"(95 %: {lo:.0%}–{hi:.0%}), ρ = {a.rho:+.2f}")
    print(f"✓ {md}")


# ------------------------------------------------------------------ Planung
def simuliere_personen(vorschlaege, personen: int, treue: float, rng: random.Random) -> list[Vergleich]:
    """Virtuelle Testpersonen: wählen mit Wahrscheinlichkeit `treue` das Zimmer mit dem höheren Buch-Score."""
    nr = [v["nr"] for v in vorschlaege]
    buch = {v["nr"]: v["buch_score"] for v in vorschlaege}
    out = []
    for p in range(personen):
        for l, r in paarplan(nr, PAARE_PRO_PERSON, WIEDERHOLUNGEN, rng):
            besser_links = buch[l] >= buch[r]
            folgt = rng.random() < treue
            out.append(Vergleich(f"P{p}", l, r, 1.0 if besser_links == folgt else 0.0))
    return out


def planung(simulationen: int = 400):
    rng = random.Random(1)
    vorschlaege = [{"nr": i, "buch_score": s} for i, s in enumerate([60, 57, 54, 51, 48, 45, 42, 39], 1)]
    print("Wie viele Personen braucht man, damit die Trefferquote der Regeln sicher über Zufall (50 %) liegt?")
    print(f"(Simulation, {PAARE_PRO_PERSON}+{WIEDERHOLUNGEN} Vergleiche pro Person, {simulationen} Durchläufe je Feld)\n")
    treuen = (0.6, 0.65, 0.7, 0.8)
    print("Personen | " + " | ".join(f"Regeln stimmen in {t:.0%}" for t in treuen))
    for n in (5, 10, 15, 20, 30):
        zeile = []
        for t in treuen:
            erfolg = 0
            for _ in range(simulationen):
                v = simuliere_personen(vorschlaege, n, t, rng)
                treffer = sum((x.gewinner == (x.links if vorschlaege[x.links - 1]["buch_score"] >=
                                              vorschlaege[x.rechts - 1]["buch_score"] else x.rechts)) for x in v)
                erfolg += wilson(treffer, len(v))[0] > 0.5
            zeile.append(f"{erfolg / simulationen:>20.0%}")
        print(f"{n:>8} | " + " | ".join(zeile))
    print("\nLesebeispiel: Stimmen die Regeln in 65 % der Fälle mit dem Gefühl überein, zeigt die Studie das mit der")
    print("angegebenen Wahrscheinlichkeit. Ziel: ≥ 80 %. Achtung: Die Simulation nimmt an, dass alle Personen")
    print("unabhängig gleich ticken – echte Personen unterscheiden sich, darum lieber etwas mehr einplanen.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    befehl = sys.argv[1]
    if befehl == "erstellen":
        erstellen(sys.argv[2] if len(sys.argv) > 2 else "runde3")
    elif befehl == "hinzufuegen" and len(sys.argv) > 2:
        hinzufuegen(" ".join(sys.argv[2:]))
    elif befehl == "auswerten":
        auswerten_runde(sys.argv[2] if len(sys.argv) > 2 else "runde3")
    elif befehl == "planung":
        planung()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
