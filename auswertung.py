"""
EVALUATION – Zahlen und Grafiken für den Projektbericht.

In PyCharm: Rechtsklick auf auswertung.py -> Run 'auswertung'   (dauert ca. 2–4 Minuten)

Ergebnis im Ordner `auswertung/`:
    bericht_auswertung.md          alle Zahlen als Tabellen (zum Übernehmen in den Bericht)
    1_optimierer_vs_zufall.png     Wie gut ist die Suche (Simulated Annealing) im Vergleich zu Zufall?
    2_korrektur.png                Wie stark verbessert die Minimal-Korrektur ein Zimmer – mit wie vielen Änderungen?
    3_lernkurve_simulation.png     Lernt das Präferenz-Modell den Geschmack einer Person? (Simulationsstudie)
    4_echte_bewertungen.png        Wie gut sagt das Modell EURE Noten voraus? (Kreuzvalidierung, ab 8 Bewertungen)

Die vier Teile entsprechen den Evaluationsfragen:
  1. Findet der Optimierer gute, machbare Anordnungen?            -> Score + Anteil machbar, Laufzeit
  2. Schlägt die Korrektur sinnvolle Änderungen vor?               -> Score vorher/nachher, Anzahl Änderungen,
                                                                      Mini-Verschiebungen (< 30 cm) = 0?
  3. Funktioniert das Lernverfahren grundsätzlich?                -> „virtuelle Testperson“ mit bekanntem Geschmack:
                                                                      findet das Modell ihn aus wenigen Noten wieder?
  4. Bringt Personalisierung bei echten Menschen etwas?           -> Leave-one-out-Kreuzvalidierung auf euren Noten,
                                                                      Vergleich mit dem reinen Buch-Modell
"""
from __future__ import annotations

import contextlib
import io
import json
import math
import os
import random
import tempfile
import time

import numpy as np

from fengshui.bewertung import bewerte
from fengshui.ml import Personalisierung, merkmale, weiche_regel_ids
from fengshui.optimierer import korrigiere, optimiere, zufallslayout
from fengshui.regeln import REGELN
from mein_zimmer import erstelle_layout

ORDNER = "auswertung"
SEED = 2026
BUCH = {r.id: r.gewicht for r in REGELN}
TITEL = {r.id: r.titel for r in REGELN}


# ------------------------------------------------------------------ Hilfen
def _still(f, *a, **kw):
    """Funktion ohne Konsolenausgabe ausführen."""
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **kw)


def _raenge(x):
    x = np.asarray(x, float)
    order = x.argsort()
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    for v in np.unique(x):                     # gleiche Werte -> mittlerer Rang
        idx = x == v
        if idx.sum() > 1:
            r[idx] = r[idx].mean()
    return r


def spearman(a, b) -> float:
    """Rangkorrelation: 1 = Reihenfolge perfekt getroffen, 0 = Zufall."""
    ra, rb = _raenge(a), _raenge(b)
    if ra.std() == 0 or rb.std() == 0:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def _matrix(daten, ids):
    S = np.array([[d["merkmale"].get(k, 0.0) for k in ids] for d in daten])
    y = np.array([d["note"] for d in daten])
    return S, y


def trainiere_personal(train, lambda_prior=2.0) -> dict:
    """Das Lernverfahren aus ml.py – ohne die echte meine_bewertungen.json anzufassen."""
    with tempfile.TemporaryDirectory() as tmp:
        p = Personalisierung(os.path.join(tmp, "x.json"))
        p.daten = list(train)
        return _still(p.trainiere, lambda_prior=lambda_prior)


def vorhersage(train, test, gewichte):
    """Note ≈ b − a · Σ w_i·Strafe_i ; a, b per kleinster Quadrate auf den Trainingsdaten (a ≥ 0)."""
    ids = sorted(gewichte)
    w = np.array([gewichte[k] for k in ids])
    S_tr, y_tr = _matrix(train, ids)
    S_te, _ = _matrix(test, ids)
    x = S_tr @ w
    if x.std() < 1e-9:
        a = 0.0
    else:
        a = max(0.0, -np.cov(x, y_tr)[0, 1] / x.var(ddof=1))
    b = y_tr.mean() + a * x.mean()
    return b - a * (S_te @ w)


def buch_gewichte(ids):
    return {k: BUCH[k] for k in ids}


# ------------------------------------------------------------------ 1. Optimierer
def teil1_optimierer(basis, rng):
    print("1/4  Optimierer vs. Zufall …")
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
    print("2/4  Minimal-Korrektur …")
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


# ------------------------------------------------------------------ 3. Simulationsstudie
def _layout_pool(basis, rng, n):
    """Plausible, machbare Layouts unterschiedlicher Qualität (wie beim Bewerten in lernen.py)."""
    pool = []
    while len(pool) < n:
        lay, e = optimiere(basis, iterationen=rng.choice([20, 40, 80, 160, 320]), neustarts=1,
                           seed=rng.randrange(10 ** 9), anzahl_ergebnisse=1, ausgabe=False)[0]
        if e.machbar:
            pool.append(merkmale(lay))
    return pool


def _virtuelle_person(ids, rng):
    """Geschmack mit bekannten Gewichten: manche Regeln egal (×0), manche doppelt/dreifach so wichtig."""
    return {k: BUCH[k] * rng.choice([0.0, 0.5, 1.0, 1.0, 2.0, 3.0]) for k in ids}


def _noten(pool, w_echt, rng, rauschen=0.8):
    ids = sorted(w_echt)
    S = np.array([[m.get(k, 0.0) for k in ids] for m in pool])
    x = S @ np.array([w_echt[k] for k in ids])
    skala = 6.0 / max(1e-6, np.percentile(x, 90))      # beste ≈ 10, schlechteste ≈ 3–4
    y = 10 - skala * x + np.array([rng.gauss(0, rauschen) for _ in x])
    y = np.clip(np.round(y * 2) / 2, 0, 10)          # halbe Noten wie bei Menschen
    wahr = 10 - skala * x                              # „wahrer“ Geschmack ohne Tagesform
    return [{"merkmale": m, "note": float(n)} for m, n in zip(pool, y)], wahr


def teil3_simulation(basis, rng):
    print("3/4  Simulationsstudie Präferenzlernen (virtuelle Testpersonen) …")
    ids = weiche_regel_ids(basis.raum.raumtyp)
    pool = _layout_pool(basis, rng, 140)
    anzahlen = [5, 8, 12, 20, 30, 40]
    personen = 6
    res = {n: {"personal": [], "buch": [], "mae_personal": [], "mae_buch": []} for n in anzahlen}
    for p in range(personen):
        w_echt = _virtuelle_person(ids, rng)
        daten, wahr = _noten(pool, w_echt, rng)
        idx = list(range(len(daten)))
        rng.shuffle(idx)
        test_idx = idx[:60]
        test = [daten[i] for i in test_idx]
        for n in anzahlen:
            train = [daten[i] for i in idx[60:60 + n]]
            g_pers = trainiere_personal(train)
            for name, g in (("personal", g_pers), ("buch", buch_gewichte(g_pers))):
                pred = vorhersage(train, test, g)
                res[n][name].append(spearman(pred, [wahr[i] for i in test_idx]))
                res[n]["mae_" + name].append(float(np.mean(np.abs(pred - [d["note"] for d in test]))))
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, farbe, label in (("personal", "#2a7", "Personalisiert (lernt aus Noten)"),
                               ("buch", "#888", "Nur Buch-Gewichte")):
        m = [np.mean(res[n][name]) for n in anzahlen]
        s = [np.std(res[n][name]) for n in anzahlen]
        ax.errorbar(anzahlen, m, yerr=s, marker="o", color=farbe, label=label, capsize=3)
    ax.set_xlabel("Anzahl Bewertungen")
    ax.set_ylabel("Rangkorrelation mit dem wahren Geschmack")
    ax.set_ylim(0, 1)
    ax.set_title(f"Lernkurve – {personen} virtuelle Testpersonen, je 60 Test-Layouts")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(ORDNER, "3_lernkurve_simulation.png"), dpi=140)
    plt.close(fig)
    return anzahlen, res, personen


# ------------------------------------------------------------------ 4. Echte Bewertungen
def teil4_echt(datei="meine_bewertungen.json"):
    print("4/4  Eure echten Bewertungen …")
    if not os.path.exists(datei):
        return None
    with open(datei, encoding="utf-8") as f:
        daten = json.load(f).get("daten", [])
    if len(daten) < 8:
        return {"n": len(daten)}
    ids = sorted({k for d in daten for k in d["merkmale"]})
    pred_p, pred_b, echt = [], [], []
    for i in range(len(daten)):                       # Leave-one-out: jede Note einmal vorhersagen
        train = daten[:i] + daten[i + 1:]
        g = trainiere_personal(train)
        pred_p.append(vorhersage(train, [daten[i]], g)[0])
        pred_b.append(vorhersage(train, [daten[i]], buch_gewichte(ids))[0])
        echt.append(daten[i]["note"])
    echt = np.array(echt)
    mittelwert = [np.mean([d["note"] for j, d in enumerate(daten) if j != i]) for i in range(len(daten))]
    erg = {
        "n": len(daten),
        "mae_personal": float(np.mean(np.abs(np.array(pred_p) - echt))),
        "mae_buch": float(np.mean(np.abs(np.array(pred_b) - echt))),
        "mae_mittelwert": float(np.mean(np.abs(np.array(mittelwert) - echt))),
        "rho_personal": spearman(pred_p, echt),
        "rho_buch": spearman(pred_b, echt),
    }
    g = trainiere_personal(daten)
    unterschiede = sorted(((g[k] - BUCH[k], k) for k in g), key=lambda x: -abs(x[0]))[:8]
    erg["groesste_abweichungen"] = [(k, TITEL[k], BUCH[k], g[k]) for _, k in unterschiede]
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(echt, pred_b, color="#888", label=f"Nur Buch (Fehler Ø {erg['mae_buch']:.2f})")
    ax.scatter(echt, pred_p, color="#2a7", label=f"Personalisiert (Fehler Ø {erg['mae_personal']:.2f})")
    ax.plot([0, 10], [0, 10], "k--", lw=1)
    ax.set_xlabel("Eure Note")
    ax.set_ylabel("Vorhergesagte Note (ohne diese Note trainiert)")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_title(f"Leave-one-out mit {len(daten)} Bewertungen")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(ORDNER, "4_echte_bewertungen.png"), dpi=140)
    plt.close(fig)
    return erg


# ------------------------------------------------------------------ Bericht
def bericht(t1, t2, t3, t4) -> str:
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
    anzahlen, res, personen = t3
    z += ["", "## 3. Simulationsstudie: Lernt das Modell einen Geschmack?", "",
          f"{personen} virtuelle Testpersonen mit bekanntem Geschmack (zufällig: manche Regeln egal, manche bis 3× "
          "so wichtig wie im Buch) bewerten Layouts – mit Rauschen (±0.8 Noten) und halben Noten wie echte Menschen. "
          "Gemessen wird, wie gut das Modell die Reihenfolge von 60 *nicht* bewerteten Layouts trifft "
          "(Rangkorrelation nach Spearman, 1 = perfekt).", "",
          "| Bewertungen | Personalisiert ρ | Nur Buch ρ | Personalisiert Fehler Ø | Nur Buch Fehler Ø |",
          "|---|---|---|---|---|"]
    for n in anzahlen:
        r = res[n]
        z.append(f"| {n} | {np.mean(r['personal']):.2f} ± {np.std(r['personal']):.2f} | "
                 f"{np.mean(r['buch']):.2f} ± {np.std(r['buch']):.2f} | "
                 f"{np.mean(r['mae_personal']):.2f} | {np.mean(r['mae_buch']):.2f} |")
    z += ["", "Grafik: `3_lernkurve_simulation.png`", ""]
    z += ["## 4. Eure echten Bewertungen (Leave-one-out-Kreuzvalidierung)", ""]
    if t4 is None:
        z.append("Noch keine `meine_bewertungen.json` – erst mit `lernen.py` bewerten, dann erneut ausführen.")
    elif "mae_personal" not in t4:
        z.append(f"Erst {t4['n']} Bewertungen – für eine aussagekräftige Kreuzvalidierung braucht es mindestens 8.")
    else:
        z += [f"Jede der {t4['n']} Noten wird vorhergesagt, ohne dass das Modell sie beim Training gesehen hat.", "",
              "| Modell | Fehler Ø (Notenpunkte) | Rangkorrelation ρ |", "|---|---|---|",
              f"| Immer den Mittelwert raten | {t4['mae_mittelwert']:.2f} | – |",
              f"| Nur Buch-Gewichte | {t4['mae_buch']:.2f} | {t4['rho_buch']:.2f} |",
              f"| Personalisiert | {t4['mae_personal']:.2f} | {t4['rho_personal']:.2f} |", "",
              "Größte Unterschiede zwischen Buch und eurem Geschmack:", "",
              "| Regel | Buch | Gelernt |", "|---|---|---|"]
        z += [f"| {k} {t} | {b:.1f} | {g:.1f} |" for k, t, b, g in t4["groesste_abweichungen"]]
        z += ["", "Grafik: `4_echte_bewertungen.png`"]
    z += ["", "## Grenzen", "",
          "- Der Score misst die Einhaltung der Buchregeln, nicht eine nachgewiesene Wirkung (Feng Shui ist "
          "wissenschaftlich nicht belegt).",
          "- Getestet an einem Zimmer (Maße aus `mein_zimmer.py`); andere Grundrisse können anders abschneiden.",
          "- Die Simulationsstudie zeigt, dass das Verfahren funktioniert, *wenn* sich Geschmack als gewichtete "
          "Regel-Summe beschreiben lässt – ob das für echte Menschen gilt, zeigt erst Teil 4.", ""]
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
    t3 = teil3_simulation(basis, rng)
    t4 = teil4_echt()
    text = bericht(t1, t2, t3, t4)
    with open(os.path.join(ORDNER, "bericht_auswertung.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print()
    print(text)
    print(f"\nFertig in {time.time() - start:.0f} s. Alles liegt im Ordner '{ORDNER}/'.")


if __name__ == "__main__":
    main()
