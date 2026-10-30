"""
GRADIENT BOOSTING trainieren und auswerten (Ersatzmodell für die Regelbasis).

In PyCharm: Rechtsklick auf surrogat_trainieren.py -> Run   (dauert ca. 2–5 Minuten)
Braucht scikit-learn:  pip install scikit-learn   (PyCharm bietet das über requirements.txt an)

Ablauf
  1. Daten:   6000 Grundrisse deines Zimmers erzeugen, die Regelbasis bewertet jeden (= Labels, automatisch).
  2. Modelle: Mittelwert raten · Lineare Regression · Random Forest · Gradient Boosting
              jeweils mit 10-facher Kreuzvalidierung verglichen (MAE, R², Rangkorrelation).
              Dazu Klassifikation „machbar ja/nein“: Logistische Regression vs. Gradient Boosting.
  3. Lernkurve: Wie viele Trainingsbeispiele braucht Gradient Boosting?
  4. Merkmalswichtigkeit: Worauf achtet das Modell? (Permutation Importance)
  5. Nutzen:  Aus 2000 Kandidaten wählt das Modell 20 aus – sind die wirklich gut? Wie viel Zeit spart das?
  6. Speichern: daten/surrogat_modell.joblib, Bericht + Grafiken in auswertung/surrogat_*.
"""
from __future__ import annotations

import os
import time

import numpy as np

from fengshui.bewertung import bewerte
from fengshui.ml import spearman
from fengshui.optimierer import optimiere
from fengshui.surrogat import Surrogat, erzeuge_datensatz, merkmal_namen, nachbarn, vorauswahl
from mein_zimmer import erstelle_layout

ANZAHL = int(os.environ.get("SURR_N", 6000))
SEED = 2026
FOLDS = 10
ORDNER = "auswertung"
MODELL_DATEI = os.path.join("daten", "surrogat_modell.joblib")


def modelle_regression():
    from sklearn.dummy import DummyRegressor
    from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    return {
        "Mittelwert raten (Baseline)": DummyRegressor(),
        "Lineare Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=SEED),
        "Gradient Boosting": HistGradientBoostingRegressor(max_iter=400, learning_rate=0.06, max_leaf_nodes=31,
                                                           l2_regularization=1.0, random_state=SEED),
    }


def modelle_klassifikation():
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return {
        "Häufigste Klasse (Baseline)": DummyClassifier(strategy="most_frequent"),
        "Logistische Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "Gradient Boosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=SEED),
    }


def kreuzvalidierung_regression(X, y):
    from sklearn.model_selection import KFold, cross_val_predict
    kf = KFold(FOLDS, shuffle=True, random_state=SEED)
    erg, vorhersagen = {}, {}
    for name, m in modelle_regression().items():
        t = time.time()
        maes, r2s, rhos = [], [], []
        for tr, te in kf.split(X):
            m.fit(X[tr], y[tr])
            p = m.predict(X[te])
            maes.append(np.mean(np.abs(p - y[te])))
            r2s.append(1 - np.sum((p - y[te]) ** 2) / np.sum((y[te] - y[te].mean()) ** 2))
            rhos.append(spearman(p, y[te]) if np.std(p) > 0 else float("nan"))
        erg[name] = {"mae": (np.mean(maes), np.std(maes)), "r2": (np.mean(r2s), np.std(r2s)),
                     "rho": (np.mean(rhos), np.std(rhos)), "sekunden": time.time() - t}
        print(f"     {name:<30} MAE {np.mean(maes):5.2f} ± {np.std(maes):.2f}   R² {np.mean(r2s):5.2f}")
        if name in ("Lineare Regression", "Gradient Boosting"):
            vorhersagen[name] = cross_val_predict(m, X, y, cv=kf)
    return erg, vorhersagen


def kreuzvalidierung_klassifikation(X, y):
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
    from sklearn.model_selection import StratifiedKFold
    kf = StratifiedKFold(FOLDS, shuffle=True, random_state=SEED)
    erg = {}
    for name, m in modelle_klassifikation().items():
        acc, auc, f1 = [], [], []
        for tr, te in kf.split(X, y):
            m.fit(X[tr], y[tr])
            p = m.predict(X[te])
            prob = m.predict_proba(X[te])[:, 1]
            acc.append(accuracy_score(y[te], p))
            f1.append(f1_score(y[te], p, zero_division=0))
            auc.append(roc_auc_score(y[te], prob))
        erg[name] = {"acc": (np.mean(acc), np.std(acc)), "f1": (np.mean(f1), np.std(f1)),
                     "auc": (np.mean(auc), np.std(auc))}
        print(f"     {name:<30} Genauigkeit {np.mean(acc):.1%}   AUC {np.mean(auc):.2f}")
    return erg


def lernkurve(X, y):
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=SEED)
    groessen = [n for n in (250, 500, 1000, 2000, 3000, len(X_tr)) if n <= len(X_tr)]
    punkte = []
    for n in groessen:
        m = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.06, l2_regularization=1.0, random_state=SEED)
        m.fit(X_tr[:n], y_tr[:n])
        punkte.append((n, float(np.mean(np.abs(m.predict(X_te) - y_te))),
                       float(np.mean(np.abs(m.predict(X_tr[:n]) - y_tr[:n])))))
    return punkte


def wichtigkeit(X, y, namen):
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import train_test_split
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=SEED)
    m = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.06, l2_regularization=1.0, random_state=SEED)
    m.fit(X_tr, y_tr)
    r = permutation_importance(m, X_te, y_te, n_repeats=5, random_state=SEED, scoring="neg_mean_absolute_error",
                               n_jobs=-1)
    reihenfolge = np.argsort(-r.importances_mean)[:15]
    return [(namen[i], float(r.importances_mean[i])) for i in reihenfolge]


def nutzen(surrogat, basis):
    """Vorauswahl: Modell wählt 20 aus 2000 Kandidaten – Vergleich mit Zufall und mit dem echten Optimum."""
    (start, _), *_ = optimiere(basis, iterationen=500, neustarts=1, seed=7, anzahl_ergebnisse=1, ausgabe=False)
    kand = nachbarn(start, 2000, seed=11)
    t = time.time()
    echt = [bewerte(l) for l in kand]
    t_regeln = time.time() - t
    t = time.time()
    auswahl = vorauswahl(surrogat, kand, k=20)
    t_modell = time.time() - t
    wert = np.array([e.score if e.machbar else 0.0 for e in echt])      # unmachbar zählt als 0
    rng = np.random.default_rng(SEED)
    zufall = rng.choice(len(kand), 20, replace=False)
    top20 = set(np.argsort(-wert)[:20])
    return {
        "kandidaten": len(kand),
        "modell_mittel": float(wert[auswahl].mean()), "modell_bester": float(wert[auswahl].max()),
        "modell_machbar": sum(echt[i].machbar for i in auswahl),
        "zufall_mittel": float(wert[zufall].mean()), "zufall_machbar": sum(echt[i].machbar for i in zufall),
        "optimum": float(wert.max()), "treffer_top20": len(top20 & set(auswahl)),
        "t_regeln": t_regeln, "t_modell": t_modell,
        "ms_regeln": 1000 * t_regeln / len(kand), "ms_modell": 1000 * t_modell / len(kand),
    }


def grafiken(reg, vorh, y, kurve, wicht):
    import matplotlib.pyplot as plt
    namen = list(reg)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    m = [reg[n]["mae"][0] for n in namen]
    s = [reg[n]["mae"][1] for n in namen]
    farben = ["#bbb", "#8aa", "#6b9", "#1f7a5c"]
    ax.barh(namen, m, xerr=s, color=farben, capsize=3)
    for i, v in enumerate(m):
        ax.text(v + max(m) * 0.02, i, f"{v:.2f}", va="center", fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(f"Mittlerer Fehler in Score-Punkten ({FOLDS}-fache Kreuzvalidierung, kleiner = besser)")
    ax.set_title("Modellvergleich: Feng-Shui-Score vorhersagen")
    fig.tight_layout(); fig.savefig(os.path.join(ORDNER, "surrogat_modellvergleich.png"), dpi=140); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    for ax, n in zip(axs, ("Lineare Regression", "Gradient Boosting")):
        ax.scatter(y, vorh[n], s=4, alpha=0.3, color="#1f7a5c" if n == "Gradient Boosting" else "#8aa")
        ax.plot([y.min(), y.max()], [y.min(), y.max()], "k--", lw=1)
        ax.set_title(f"{n} (MAE {reg[n]['mae'][0]:.2f})")
        ax.set_xlabel("Echter Score (Regelbasis)")
    axs[0].set_ylabel("Vorhergesagter Score (nicht trainiert auf diesem Grundriss)")
    fig.tight_layout(); fig.savefig(os.path.join(ORDNER, "surrogat_vorhersage.png"), dpi=140); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot([k[0] for k in kurve], [k[1] for k in kurve], "o-", color="#1f7a5c", label="Testdaten")
    ax.plot([k[0] for k in kurve], [k[2] for k in kurve], "o--", color="#999", label="Trainingsdaten")
    ax.set_xlabel("Anzahl Trainingsbeispiele"); ax.set_ylabel("Mittlerer Fehler (Score-Punkte)")
    ax.set_title("Lernkurve Gradient Boosting"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(ORDNER, "surrogat_lernkurve.png"), dpi=140); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.barh([w[0] for w in wicht], [w[1] for w in wicht], color="#1f7a5c")
    ax.invert_yaxis()
    ax.set_xlabel("Wichtigkeit (wie viel schlechter wird die Vorhersage ohne dieses Merkmal)")
    ax.set_title("Worauf achtet Gradient Boosting?")
    fig.tight_layout(); fig.savefig(os.path.join(ORDNER, "surrogat_merkmale.png"), dpi=140); plt.close(fig)


def bericht(n, anteil_machbar, reg, kla, kurve, wicht, nut, dauer_daten) -> str:
    z = ["# Gradient Boosting als Ersatzmodell für die Regelbasis", "",
         f"Erzeugt mit `surrogat_trainieren.py` am {time.strftime('%d.%m.%Y %H:%M')} (Seed {SEED}).", "",
         "## Idee", "",
         "Die Regelbasis (Buch + Menschenverstand) bewertet automatisch erzeugte Grundrisse – das sind die Labels, "
         "ohne Handarbeit. Gradient Boosting lernt, diese Bewertung nur aus einfachen geometrischen Merkmalen "
         "(Positionen, Ausrichtung, Abstände zu Wänden, Tür, Fenster und zwischen den Möbeln) vorherzusagen. "
         "Die Regeln selbst ändern sich dadurch nicht: Das Modell ahmt sie nach und ist dafür viel schneller "
         "(Surrogatmodell / Wissensdestillation).", "",
         "## Daten", "",
         f"- {n} Grundrisse deines Zimmers (30 % zufällig, 70 % ausgehend von teil-optimierten Grundrissen mit "
         f"0–12 zufälligen Veränderungen), erzeugt in {dauer_daten:.0f} s",
         f"- davon machbar (alle harten Regeln erfüllt): {anteil_machbar:.0%}",
         f"- {len(merkmal_namen(erstelle_layout()))} Merkmale pro Grundriss", "",
         f"## Regression: Score vorhersagen ({FOLDS}-fache Kreuzvalidierung)", "",
         "| Modell | MAE (Score-Punkte) | R² | Rangkorrelation ρ | Rechenzeit |", "|---|---|---|---|---|"]
    for name, r in reg.items():
        rho = "–" if np.isnan(r["rho"][0]) else f"{r['rho'][0]:.3f}"
        z.append(f"| {name} | {r['mae'][0]:.2f} ± {r['mae'][1]:.2f} | {r['r2'][0]:.3f} | {rho} | "
                 f"{r['sekunden']:.0f} s |")
    z += ["", "MAE = mittlerer absoluter Fehler, R² = Anteil erklärter Streuung (1 = perfekt), ρ = trifft das Modell "
              "die Reihenfolge? ± = Standardabweichung über die 10 Folds.", "",
          "Grafiken: `surrogat_modellvergleich.png`, `surrogat_vorhersage.png`", "",
          f"## Klassifikation: machbar ja/nein ({FOLDS}-fache Kreuzvalidierung)", "",
          "| Modell | Genauigkeit | F1 (machbar) | ROC-AUC |", "|---|---|---|---|"]
    for name, r in kla.items():
        z.append(f"| {name} | {r['acc'][0]:.1%} | {r['f1'][0]:.2f} | {r['auc'][0]:.3f} |")
    z += ["", "## Lernkurve (Gradient Boosting, 20 % Testdaten)", "",
          "| Trainingsbeispiele | Fehler Testdaten | Fehler Trainingsdaten |", "|---|---|---|"]
    z += [f"| {n_} | {te:.2f} | {tr:.2f} |" for n_, te, tr in kurve]
    z += ["", "Liegt der Testfehler deutlich über dem Trainingsfehler, lernt das Modell teils auswendig "
              "(Overfitting); mehr Daten verkleinern die Lücke. Grafik: `surrogat_lernkurve.png`", "",
          "## Worauf achtet das Modell? (Permutation Importance, Top 15)", "",
          "| Merkmal | Wichtigkeit |", "|---|---|"]
    z += [f"| {name} | {w:.2f} |" for name, w in wicht]
    z += ["", "Grafik: `surrogat_merkmale.png`", "",
          "## Nutzen: Vorauswahl aus vielen Kandidaten", "",
          f"Rund um einen Grundriss wurden {nut['kandidaten']} Varianten erzeugt. Das Modell wählt 20 aus; "
          "danach prüft die echte Regelbasis nur diese 20.", "",
          "| | 20 vom Modell gewählt | 20 zufällig gewählt |", "|---|---|---|",
          f"| Ø echter Score (unmachbar = 0) | {nut['modell_mittel']:.1f} | {nut['zufall_mittel']:.1f} |",
          f"| davon machbar | {nut['modell_machbar']}/20 | {nut['zufall_machbar']}/20 |",
          f"| bester echter Score | {nut['modell_bester']:.1f} | – |", "",
          f"Bestes aller {nut['kandidaten']} Kandidaten: {nut['optimum']:.1f}. Von den echten Top 20 hat das Modell "
          f"{nut['treffer_top20']} gefunden.", "",
          f"Zeit: alle Kandidaten mit Regeln bewerten {nut['t_regeln']:.1f} s ({nut['ms_regeln']:.1f} ms pro Grundriss) – "
          f"Modell {nut['t_modell']:.2f} s ({nut['ms_modell']:.2f} ms pro Grundriss).", "",
          "## Grenzen", "",
          "- Das Modell kann nie besser sein als die Regelbasis, die es nachahmt – es ist schneller, nicht klüger.",
          "- Trainiert auf EIN Zimmer: Für einen anderen Grundriss oder andere Möbel muss es neu trainiert werden "
          "(die Merkmale hängen von den Möbeln ab).",
          "- Für die endgültige Entscheidung wird immer die echte Regelbasis benutzt; das Modell wählt nur vor.", ""]
    return "\n".join(z)


def main():
    try:
        import sklearn  # noqa: F401
    except ImportError:
        print("Bitte zuerst scikit-learn installieren:  pip install scikit-learn")
        return
    import matplotlib
    if os.environ.get("MPLBACKEND") is None:
        matplotlib.use("Agg")
    os.makedirs(ORDNER, exist_ok=True)
    os.makedirs("daten", exist_ok=True)
    basis = erstelle_layout()
    namen = merkmal_namen(basis)
    start = time.time()

    print(f"1/5  Datensatz: {ANZAHL} Grundrisse erzeugen und von der Regelbasis bewerten lassen …")
    t = time.time()
    X, y_score, y_machbar, _ = erzeuge_datensatz(basis, ANZAHL, seed=SEED)
    dauer_daten = time.time() - t
    print(f"     fertig ({dauer_daten:.0f} s), machbar: {y_machbar.mean():.0%}")

    print(f"2/5  Modellvergleich mit {FOLDS}-facher Kreuzvalidierung – Score (Regression) …")
    reg, vorh = kreuzvalidierung_regression(X, y_score)
    print("     … und machbar ja/nein (Klassifikation)")
    kla = kreuzvalidierung_klassifikation(X, y_machbar)

    print("3/5  Lernkurve und Merkmalswichtigkeit …")
    kurve = lernkurve(X, y_score)
    wicht = wichtigkeit(X, y_score, namen)

    print("4/5  Endgültiges Modell auf allen Daten trainieren und speichern …")
    from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
    r = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.06, l2_regularization=1.0, random_state=SEED)
    k = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=SEED)
    sur = Surrogat(r.fit(X, y_score), k.fit(X, y_machbar), namen)
    sur.speichern(MODELL_DATEI)

    print("5/5  Nutzen testen: Vorauswahl aus 2000 Kandidaten …")
    nut = nutzen(sur, basis)

    grafiken(reg, vorh, y_score, kurve, wicht)
    text = bericht(ANZAHL, float(y_machbar.mean()), reg, kla, kurve, wicht, nut, dauer_daten)
    with open(os.path.join(ORDNER, "surrogat_bericht.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print()
    print(text)
    print(f"\nFertig in {time.time() - start:.0f} s. Modell: {MODELL_DATEI}, Bericht + Grafiken: {ORDNER}/surrogat_*")


if __name__ == "__main__":
    main()
