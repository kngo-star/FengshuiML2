"""
EVALUATION – Zahlen und Grafiken für den Projektbericht.

In PyCharm: Rechtsklick auf auswertung.py -> Run 'auswertung'   (dauert ca. 1–2 Minuten)

Ergebnis im Ordner `auswertung/`:
    bericht_auswertung.md          alle Zahlen als Tabellen (zum Übernehmen in den Bericht)
    1_optimierer_vs_zufall.png     Wie gut ist die Suche (Simulated Annealing) im Vergleich zu Zufall?
    2_korrektur.png                Wie stark verbessert die Minimal-Korrektur ein Zimmer – mit wie vielen Änderungen?
    3_regeln_vs_noten.png          Treffen die Regeln das Gefühl? (Noten aus dem Bewertungsbogen)

Das Gradient-Boosting-Modell hat ein eigenes Skript: surrogat_trainieren.py (-> auswertung/surrogat_*).
"""
from __future__ import annotations

import json
import math
import os
import random
import time

import numpy as np

from fengshui.bewertung import bewerte
from fengshui.ml import pruefe, regel_score, spearman
from fengshui.optimierer import korrigiere, optimiere, zufallslayout
from mein_zimmer import erstelle_layout

ORDNER = "auswertung"
SEED = 2026


# ------------------------------------------------------------------ 1. Optimierer
def teil1_optimierer(basis, rng):
    print("1/3  Optimierer vs. Zufall …")
    zufall = [bewerte(zufallslayout(basis, rng)) for _ in range(400)]
    t = time.time()
    opt = []
    for i in range(6):
        (lay, e), *_ = optimiere(basis, iterationen=1000, neustarts=1, seed=SEED + i, anzahl_ergebnisse=1,
                                 ausgabe=False)
        opt.append(e)
    dauer = (time.time() - t) / len(opt)
    t = time.time()
    (_, e_voll), *_ = optimiere(basis, iterationen=3000, neustarts=6, seed=SEED, anzahl_ergebnisse=1, ausgabe=False)
    dauer_voll = time.time() - t
    z_mach = [e.score for e in zufall if e.machbar]
    erg = {
        "zufall_n": len(zufall),
        "zufall_machbar_anteil": len(z_mach) / len(zufall),
        "zufall_score_mittel": float(np.mean([e.score for e in zufall])),
        "zufall_machbar_score_mittel": float(np.mean(z_mach)) if z_mach else float("nan"),
        "zufall_score_max": float(max(e.score for e in zufall)),
        "opt_n": len(opt),
        "opt_machbar_anteil": sum(e.machbar for e in opt) / len(opt),
        "opt_score_mittel": float(np.mean([e.score for e in opt])),
        "opt_score_min": float(min(e.score for e in opt)),
        "opt_sekunden": dauer,
        "voll_score": e_voll.score, "voll_machbar": e_voll.machbar, "voll_sekunden": dauer_voll,
    }
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist([e.score for e in zufall], bins=30, color="#bbb", label=f"Zufällige Anordnung (n={len(zufall)}, davon machbar: {len(z_mach) / len(zufall):.0%})")
    for i, e in enumerate(opt):
        ax.axvline(e.score, color="#2a7", lw=2, label="Optimierer, kurz (1 × 1000 Schritte)" if i == 0 else None)
    ax.axvline(e_voll.score, color="#165", lw=3, ls="--", label="Optimierer wie in main.py (6 × 3000)")
    ax.set_xlabel("Feng-Shui-Score (0–100, nach Buchregeln)")
    ax.set_ylabel("Anzahl Layouts")
    ax.set_title("Optimierer vs. Zufall")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(ORDNER, "1_optimierer_vs_zufall.png"), dpi=140)
    plt.close(fig)
    return erg


# ------------------------------------------------------------------ 2. Korrektur
def teil2_korrektur(basis):
    print("2/3  Minimal-Korrektur …")
    zeilen = []
    for i in range(8):
        # „Ist-Zustand“: kurz optimiert = plausibel eingerichtet, aber mit typischen Fehlern
        ist, _ = optimiere(basis, iterationen=150, neustarts=1, seed=100 + i, anzahl_ergebnisse=1, ausgabe=False)[0]
        neu, e_neu, aend, e_ist = korrigiere(ist, iterationen=800, neustarts=2, seed=i, ausgabe=False)
        haupt = [a for a in aend if not (a.gruende and a.gruende[0].startswith("wandert mit"))]
        zeilen.append({
            "vorher": e_ist.score, "nachher": e_neu.score,
            "machbar_vorher": e_ist.machbar, "machbar_nachher": e_neu.machbar,
            "aenderungen": len(haupt),
            "mini": sum(1 for a in haupt if a.strecke < 0.30 and not a.gedreht),
            "texte": [a.text() + (f" – weil: {a.gruende[0]}" if a.gruende else "") for a in haupt],
        })
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    for k, z in enumerate(zeilen):
        ax.annotate("", xy=(k, z["nachher"]), xytext=(k, z["vorher"]),
                    arrowprops=dict(arrowstyle="->", color="#2a7" if z["nachher"] > z["vorher"] + 0.5 else "#999", lw=2))
        ax.plot(k, z["vorher"], "o", color="#c55")
        ax.text(k, max(z["vorher"], z["nachher"]) + 1.5, f'{z["aenderungen"]} Änd.', ha="center", fontsize=8)
    ax.set_xticks(range(len(zeilen)), [f"Zimmer {k + 1}" for k in range(len(zeilen))], rotation=30)
    ax.set_ylabel("Score")
    ax.set_title("Minimal-Korrektur: Score vorher (rot) → nachher, mit Anzahl Änderungen")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(os.path.join(ORDNER, "2_korrektur.png"), dpi=140)
    plt.close(fig)
    return zeilen


# ------------------------------------------------------------------ 3. Regeln vs. Menschen
def teil3_menschen(datei="meine_bewertungen.json"):
    """Treffen die Regeln (Buch + Menschenverstand) das Gefühl? Die Noten PRÜFEN nur, sie ändern nichts."""
    print("3/3  Regeln vs. eure Noten …")
    if not os.path.exists(datei):
        return None
    with open(datei, encoding="utf-8") as f:
        daten = json.load(f).get("daten", [])
    if len(daten) < 3:
        return {"n": len(daten)}
    scores = [regel_score(d["merkmale"]) for d in daten]
    noten = [d["note"] for d in daten]
    erg = {"n": len(daten), "rho": spearman(scores, noten), "text": pruefe(daten, top=3)}
    runden = sorted({d.get("runde", "?") for d in daten})
    erg["runden"] = []
    for r in runden:
        idx = [i for i, d in enumerate(daten) if d.get("runde", "?") == r]
        erg["runden"].append((r, len(idx), spearman([scores[i] for i in idx], [noten[i] for i in idx])))
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.scatter(scores, noten, color="#2a7")
    for d, x, y in zip(daten, scores, noten):
        ax.annotate(str(d.get("vorschlag", "")), (x, y), textcoords="offset points", xytext=(4, 3), fontsize=8)
    ax.set_xlabel("Regel-Score (Buch + Menschenverstand)")
    ax.set_ylabel("Deine Note")
    ax.set_ylim(0, 10.5)
    ax.set_title(f"Regeln vs. Gefühl – Rangkorrelation {erg['rho']:+.2f}")
    fig.tight_layout()
    fig.savefig(os.path.join(ORDNER, "3_regeln_vs_noten.png"), dpi=140)
    plt.close(fig)
    return erg


# ------------------------------------------------------------------ Bericht
def bericht(t1, t2, t3) -> str:
    z = ["# Auswertung FengshuiML", "",
         f"Erzeugt mit `auswertung.py` am {time.strftime('%d.%m.%Y %H:%M')} (Zufalls-Seed {SEED}).", ""]
    z += ["## 1. Optimierer (Simulated Annealing) vs. Zufall", "",
          "| | Zufällige Anordnung | Optimierer |", "|---|---|---|",
          f"| Anzahl Layouts | {t1['zufall_n']} | {t1['opt_n']} Läufe |",
          f"| davon machbar (harte Regeln erfüllt) | {t1['zufall_machbar_anteil']:.0%} | {t1['opt_machbar_anteil']:.0%} |",
          f"| Score Mittelwert | {t1['zufall_score_mittel']:.1f} | {t1['opt_score_mittel']:.1f} |",
          f"| Score der machbaren (Mittelwert) | "
          f"{'– (keines machbar)' if math.isnan(t1['zufall_machbar_score_mittel']) else format(t1['zufall_machbar_score_mittel'], '.1f')}"
          f" | {t1['opt_score_mittel']:.1f} |",
          f"| Bester Zufallswert / schlechtester Optimierer-Lauf | {t1['zufall_score_max']:.1f} | {t1['opt_score_min']:.1f} |",
          f"| Rechenzeit pro Lauf | – | {t1['opt_sekunden']:.1f} s |", "",
          f"Mit der Einstellung aus `main.py` (6 Neustarts × 3000 Schritte): Score {t1['voll_score']:.1f}, "
          f"{'machbar' if t1['voll_machbar'] else 'NICHT machbar'}, {t1['voll_sekunden']:.0f} s.", "",
          "Zufällig an die Wände gestellte Möbel verletzen praktisch immer eine harte Regel (Überlappung, Tür, "
          "Laufweg) – ohne Suche gibt es also gar keine brauchbare Einrichtung.", "",
          "Grafik: `1_optimierer_vs_zufall.png`", ""]
    z += ["## 2. Minimal-Korrektur bestehender Einrichtungen", "",
          "Ist-Zustände: 8 plausibel, aber nicht optimal eingerichtete Varianten deines Zimmers.", "",
          "| Zimmer | Score vorher | Score nachher | Änderungen | davon < 30 cm |", "|---|---|---|---|---|"]
    for k, r in enumerate(t2, 1):
        z.append(f"| {k} | {r['vorher']:.1f}{'' if r['machbar_vorher'] else ' ⚠'} | {r['nachher']:.1f} | "
                 f"{r['aenderungen']} | {r['mini']} |")
    z += ["", f"Ø Verbesserung: {np.mean([r['nachher'] - r['vorher'] for r in t2]):+.1f} Punkte, "
              f"Ø {np.mean([r['aenderungen'] for r in t2]):.1f} Änderungen, "
              f"Mini-Verschiebungen insgesamt: {sum(r['mini'] for r in t2)}  (⚠ = Ist-Zustand verletzt eine harte Regel)", "",
          "Vorgeschlagene Änderungen mit Begründung:", ""]
    for k, r in enumerate(t2, 1):
        for t in r["texte"]:
            z.append(f"- Zimmer {k}: {t}")
        if not r["texte"]:
            z.append(f"- Zimmer {k}: keine Änderung (Umstellen lohnt sich nicht)")
    z += ["", "## 3. Treffen die Regeln das Gefühl? (Noten aus dem Bewertungsbogen)", "",
          "Die Regeln stammen aus dem Buch, ergänzt um Menschenverstand-Regeln für Lücken im Buch. Die Noten ändern "
          "die Regeln nicht – sie prüfen, ob die Reihenfolge nach Regel-Score zur Reihenfolge nach Gefühl passt "
          "(Rangkorrelation nach Spearman: 1 = gleiche Reihenfolge, 0 = kein Zusammenhang).", ""]
    if t3 is None:
        z.append("Noch keine `meine_bewertungen.json` – erst bewerten (Bewertungsbogen oder `lernen.py`).")
    elif "rho" not in t3:
        z.append(f"Erst {t3['n']} Noten – für eine Aussage braucht es mindestens 3.")
    else:
        z += ["| Runde | Noten | Rangkorrelation ρ |", "|---|---|---|"]
        z += [f"| {r} | {n} | {rho:+.2f} |" for r, n, rho in t3["runden"]]
        z += ["", "```", t3["text"], "```", "", "Grafik: `3_regeln_vs_noten.png`"]
    z += ["", "## 4. Gradient Boosting (Ersatzmodell)", "",
          "Siehe `auswertung/surrogat_bericht.md` (erzeugt mit `surrogat_trainieren.py`): Gradient Boosting lernt, "
          "den Regel-Score vorherzusagen – trainiert auf tausenden automatisch bewerteten Grundrissen, geprüft mit "
          "10-facher Kreuzvalidierung.", ""]
    z += ["", "## Grenzen", "",
          "- Der Score misst die Einhaltung der Buchregeln, nicht eine nachgewiesene Wirkung (Feng Shui ist "
          "wissenschaftlich nicht belegt).",
          "- Getestet an einem Zimmer (Maße aus `mein_zimmer.py`); andere Grundrisse können anders abschneiden.",
          "- Wenige Noten von wenigen Personen: Teil 3 ist ein Hinweis, kein Beweis. Die Noten widersprachen sich "
          "zwischen Personen und teils bei einer Person (Noten vs. Kommentare) – deshalb lernt das System sie nicht, "
          "sondern nutzt sie zum Prüfen und um Lücken im Buch zu finden.", ""]
    return "\n".join(z)


def main():
    os.makedirs(ORDNER, exist_ok=True)
    import matplotlib
    if os.environ.get("MPLBACKEND") is None:
        matplotlib.use("Agg")
    rng = random.Random(SEED)
    basis = erstelle_layout()
    start = time.time()
    t1 = teil1_optimierer(basis, rng)
    t2 = teil2_korrektur(basis)
    t3 = teil3_menschen()
    text = bericht(t1, t2, t3)
    with open(os.path.join(ORDNER, "bericht_auswertung.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print()
    print(text)
    print(f"\nFertig in {time.time() - start:.0f} s. Alles liegt im Ordner '{ORDNER}/'.")


if __name__ == "__main__":
    main()
