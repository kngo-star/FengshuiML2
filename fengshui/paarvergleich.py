"""
Paarvergleich: „Welches der beiden Zimmer gefällt dir besser?“ statt Noten von 0 bis 10.

Warum? In Runde 1 und 2 widersprachen sich die Noten zwischen Personen (ρ = −0,26) und teils bei einer Person.
Noten hängen stark davon ab, wie streng jemand benotet. Ein direkter Vergleich A gegen B ist für Menschen viel
leichter und konsistenter – und genau das braucht man, um zu prüfen, ob die Buchregeln das Gefühl treffen.

Inhalt:
  paarplan()            welche Paare eine Person sieht (zufällig, ausgewogen, mit 2 Wiederholungen zur Kontrolle)
  code_lesen()          Antwort-Code aus dem Bewertungsbogen lesen  ("PV1|runde3|AB|3-1,2=5,…")
  bradley_terry()       Stärke jedes Vorschlags aus allen Vergleichen (Bradley-Terry-Modell, MM-Algorithmus)
  bootstrap()           Unsicherheit der Stärken (Personen neu ziehen)
  auswerten()           alles zusammen: Rangfolge, Trefferquote der Buchregeln, Konsistenz, Übereinstimmung
  lerne_gewichte()      ML: Welche Regeln erklären die Entscheidungen der Menschen? (logistisches Modell,
                        Gewichte ≥ 0, geprüft mit Leave-one-person-out). Wird nur BERICHTET – die Regeln
                        bleiben unverändert (siehe GEWICHTE_ANPASSEN in ml.py).

Nur numpy nötig.
"""
from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

CODE_VERSION = "PV1"


# ------------------------------------------------------------------ Daten
@dataclass
class Vergleich:
    person: str
    links: int          # Nummer des Vorschlags
    rechts: int
    ergebnis: float     # 1 = links gewinnt, 0 = rechts gewinnt, 0.5 = egal

    @property
    def gewinner(self) -> Optional[int]:
        return self.links if self.ergebnis == 1 else self.rechts if self.ergebnis == 0 else None


def paarplan(nummern: list[int], anzahl: int = 15, wiederholungen: int = 2,
             rng: Optional[random.Random] = None) -> list[tuple[int, int]]:
    """Paare für EINE Person: `anzahl` verschiedene Paare in zufälliger Reihenfolge und Seite,
    dazu `wiederholungen` schon gezeigte Paare mit vertauschten Seiten (Konsistenz-Kontrolle) am Ende."""
    rng = rng or random.Random()
    alle = list(itertools.combinations(nummern, 2))
    rng.shuffle(alle)
    paare = [(a, b) if rng.random() < 0.5 else (b, a) for a, b in alle[:anzahl]]
    kontrolle = [(b, a) for a, b in rng.sample(paare[: max(1, len(paare) // 2)],
                                                min(wiederholungen, max(1, len(paare) // 2)))]
    return paare + kontrolle


def code_schreiben(runde: str, person: str, vergleiche: list[tuple[int, int, float]]) -> str:
    """(links, rechts, ergebnis) → "PV1|runde3|AB|3-1,2=5"  (a-b: a gewinnt, a=b: egal)."""
    teile = []
    for l, r, e in vergleiche:
        teile.append(f"{l}={r}" if e == 0.5 else f"{l}-{r}" if e == 1 else f"{r}-{l}")
    return f"{CODE_VERSION}|{runde}|{person}|{','.join(teile)}"


def code_details(code: str) -> dict:
    """Zusatzangaben aus dem Code: Kürzel, Vorwissen ("KN~etwas") und freiwilliger Kommentar (5. Feld)."""
    from urllib.parse import unquote
    teile = code.strip().split("|")
    kuerzel, _, vorwissen = teile[2].partition("~") if len(teile) > 2 else ("", "", "")
    return {"person": kuerzel, "vorwissen": vorwissen or "?",
            "kommentar": unquote(teile[4]) if len(teile) > 4 else ""}


def code_lesen(code: str) -> tuple[str, str, list[Vergleich]]:
    """Gegenstück zu code_schreiben. Rückgabe: (runde, person, Vergleiche).
    Akzeptiert auch die Codes aus dem HTML-Bogen ("Kürzel~Vorwissen" und optional 5. Feld = Kommentar)."""
    teile = code.strip().split("|")
    if len(teile) not in (4, 5) or teile[0] != CODE_VERSION:
        raise ValueError(f"Unbekannter Antwort-Code: {code[:40]}…")
    runde, person, liste = teile[1], teile[2].partition("~")[0], teile[3]
    vergleiche = []
    for eintrag in filter(None, (e.strip() for e in liste.split(","))):
        if "=" in eintrag:
            a, b = eintrag.split("=")
            vergleiche.append(Vergleich(person, int(a), int(b), 0.5))
        else:
            a, b = eintrag.split("-")
            vergleiche.append(Vergleich(person, int(a), int(b), 1.0))
    return runde, person, vergleiche


# ------------------------------------------------------------------ Bradley-Terry
def bradley_terry(vergleiche: list[Vergleich], nummern: list[int], iterationen: int = 500,
                  prior: float = 0.5) -> dict[int, float]:
    """Stärke θ jedes Vorschlags (log-Skala, Mittelwert 0): P(i schlägt j) = 1 / (1 + exp(θj − θi)).

    MM-Algorithmus nach Hunter (2004). `prior` = virtuelle halbe Siege/Niederlagen gegen einen
    Durchschnitts-Gegner, damit Vorschläge ohne Sieg (oder ohne Niederlage) eine endliche Stärke bekommen.
    „Egal“ zählt als halber Sieg für beide.
    """
    idx = {n: i for i, n in enumerate(nummern)}
    k = len(nummern)
    siege = np.full(k, prior)
    paare = np.zeros((k, k))
    for v in vergleiche:
        i, j = idx[v.links], idx[v.rechts]
        siege[i] += v.ergebnis
        siege[j] += 1 - v.ergebnis
        paare[i, j] += 1
        paare[j, i] += 1
    p = np.ones(k)
    for _ in range(iterationen):
        nenner = (paare / (p[:, None] + p[None, :])).sum(axis=1) + 2 * prior / (p + 1.0)
        neu = siege / nenner
        neu /= math.exp(np.log(neu).mean())
        if np.max(np.abs(neu - p)) < 1e-9:
            p = neu
            break
        p = neu
    theta = np.log(p)
    return {n: float(theta[idx[n]] - theta.mean()) for n in nummern}


def bootstrap(vergleiche: list[Vergleich], nummern: list[int], wiederholungen: int = 300,
              seed: int = 0) -> dict[int, tuple[float, float]]:
    """95-%-Intervall der Stärken: Personen mit Zurücklegen neu ziehen (bei 1 Person: Vergleiche)."""
    rng = random.Random(seed)
    personen = sorted({v.person for v in vergleiche})
    nach_person = {p: [v for v in vergleiche if v.person == p] for p in personen}
    werte = {n: [] for n in nummern}
    for _ in range(wiederholungen):
        if len(personen) >= 3:
            stichprobe = [v for p in (rng.choice(personen) for _ in personen) for v in nach_person[p]]
        else:
            stichprobe = [rng.choice(vergleiche) for _ in vergleiche]
        for n, t in bradley_terry(stichprobe, nummern, iterationen=200).items():
            werte[n].append(t)
    return {n: (float(np.percentile(w, 2.5)), float(np.percentile(w, 97.5))) for n, w in werte.items()}


# ------------------------------------------------------------------ Kennzahlen
def _spearman(a, b) -> float:
    def raenge(x):
        x = np.asarray(x, float)
        r = np.empty(len(x))
        r[np.argsort(x, kind="mergesort")] = np.arange(len(x))
        for w in np.unique(x):                       # Gleichstände: mittlerer Rang
            m = x == w
            r[m] = r[m].mean()
        return r
    ra, rb = raenge(a), raenge(b)
    if ra.std() == 0 or rb.std() == 0:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def wilson(treffer: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """95-%-Intervall für einen Anteil (Wilson). Gut auch bei kleinen Zahlen."""
    if n == 0:
        return 0.0, 1.0
    p = treffer / n
    mitte = (p + z * z / (2 * n)) / (1 + z * z / n)
    breite = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, mitte - breite), min(1.0, mitte + breite)


def konsistenz(vergleiche: list[Vergleich]) -> tuple[int, int]:
    """Wiederholte Paare derselben Person: (gleich entschieden, wiederholt insgesamt). „Egal“ zählt nicht."""
    gesehen: dict[tuple[str, int, int], list[Optional[int]]] = {}
    for v in vergleiche:
        schluessel = (v.person, min(v.links, v.rechts), max(v.links, v.rechts))
        gesehen.setdefault(schluessel, []).append(v.gewinner)
    gleich = gesamt = 0
    for antworten in gesehen.values():
        a = [x for x in antworten if x is not None]
        for x, y in zip(a, a[1:]):
            gesamt += 1
            gleich += x == y
    return gleich, gesamt


def uebereinstimmung(vergleiche: list[Vergleich]) -> tuple[float, int]:
    """Wie oft entscheiden zwei VERSCHIEDENE Personen dasselbe Paar gleich? (Anteil, Anzahl Paar-Paare)
    50 % = Zufall, 100 % = alle sind sich einig."""
    je_paar: dict[tuple[int, int], dict[str, int]] = {}
    for v in vergleiche:
        if v.gewinner is None:
            continue
        je_paar.setdefault((min(v.links, v.rechts), max(v.links, v.rechts)), {})[v.person] = v.gewinner
    gleich = gesamt = 0
    for antworten in je_paar.values():
        for a, b in itertools.combinations(antworten.values(), 2):
            gesamt += 1
            gleich += a == b
    return (gleich / gesamt if gesamt else float("nan")), gesamt


# ------------------------------------------------------------------ ML: Regelgewichte aus Entscheidungen
def _fit_logistisch(X: np.ndarray, y: np.ndarray, l2: float, schritte: int = 3000, lr: float = 0.05) -> np.ndarray:
    """P(links gewinnt) = σ(X·β) mit β ≥ 0 (projizierter Gradientenabstieg, L2-Strafe)."""
    beta = np.zeros(X.shape[1])
    for _ in range(schritte):
        p = 1 / (1 + np.exp(-(X @ beta)))
        grad = X.T @ (p - y) / len(y) + l2 * beta
        beta = np.maximum(0.0, beta - lr * grad)
    return beta


def lerne_gewichte(vergleiche: list[Vergleich], merkmale: dict[int, dict[str, float]],
                   buch_gewichte: dict[str, float], l2: float = 0.05) -> dict:
    """Welche Regeln erklären, wie Menschen entscheiden?

    Merkmal je Regel = Strafe(rechts) − Strafe(links): Hat das rechte Zimmer mehr Strafe, spricht das für links.
    Ein Gewicht β ≥ 0 sagt, wie stark eine Regel die Entscheidung beeinflusst.

    Geprüft wird mit Leave-one-person-out: Modell ohne Person X trainieren, Entscheidungen von X vorhersagen.
    Verglichen mit dem Buch (Zimmer mit höherem Buch-Score gewinnt). Nur bei ≥ 2 Personen.
    """
    regeln = sorted(buch_gewichte)
    daten = [v for v in vergleiche if v.ergebnis != 0.5]
    if not daten:
        return {"gewichte": {}, "genauigkeit_modell": None, "genauigkeit_buch": None, "n": 0}

    def zeile(v):
        return [merkmale[v.rechts].get(r, 0.0) - merkmale[v.links].get(r, 0.0) for r in regeln]

    X = np.array([zeile(v) for v in daten])
    y = np.array([v.ergebnis for v in daten])
    w_buch = np.array([buch_gewichte[r] for r in regeln])

    personen = sorted({v.person for v in daten})
    acc_m = acc_b = None
    if len(personen) >= 2:
        treffer_m = treffer_b = 0
        for p in personen:
            test = np.array([v.person == p for v in daten])
            beta = _fit_logistisch(X[~test], y[~test], l2)
            treffer_m += int(((X[test] @ beta > 0) == (y[test] == 1)).sum())
            treffer_b += int(((X[test] @ w_buch > 0) == (y[test] == 1)).sum())
        acc_m, acc_b = treffer_m / len(y), treffer_b / len(y)
    beta = _fit_logistisch(X, y, l2)
    return {"gewichte": dict(zip(regeln, map(float, beta))), "genauigkeit_modell": acc_m,
            "genauigkeit_buch": acc_b, "n": len(y), "personen": len(personen)}


# ------------------------------------------------------------------ Gesamtauswertung
@dataclass
class Auswertung:
    nummern: list[int]
    staerke: dict[int, float]
    intervall: dict[int, tuple[float, float]]
    buch_score: dict[int, float]
    rho: float                                   # Rangkorrelation Stärke ↔ Buch-Score
    treffer: int                                 # Vergleiche, in denen der höhere Buch-Score gewann
    entschieden: int                             # Vergleiche ohne „egal“ und mit verschiedenem Buch-Score
    konsistent: tuple[int, int]
    einigkeit: tuple[float, int]
    personen: list[str]
    anzahl: int
    gewichte: dict = field(default_factory=dict)

    @property
    def trefferquote(self) -> float:
        return self.treffer / self.entschieden if self.entschieden else float("nan")


def auswerten(vergleiche: list[Vergleich], vorschlaege: list[dict], buch_gewichte: Optional[dict] = None,
              seed: int = 0) -> Auswertung:
    nummern = sorted(v["nr"] for v in vorschlaege)
    buch = {v["nr"]: v["buch_score"] for v in vorschlaege}
    staerke = bradley_terry(vergleiche, nummern)
    intervall = bootstrap(vergleiche, nummern, seed=seed)
    treffer = entschieden = 0
    for v in vergleiche:
        if v.ergebnis == 0.5 or abs(buch[v.links] - buch[v.rechts]) < 1e-9:
            continue
        entschieden += 1
        buch_sieger = v.links if buch[v.links] > buch[v.rechts] else v.rechts
        treffer += v.gewinner == buch_sieger
    gewichte = {}
    if buch_gewichte:
        gewichte = lerne_gewichte(vergleiche, {v["nr"]: v["merkmale"] for v in vorschlaege}, buch_gewichte)
    return Auswertung(
        nummern=nummern, staerke=staerke, intervall=intervall, buch_score=buch,
        rho=_spearman([staerke[n] for n in nummern], [buch[n] for n in nummern]),
        treffer=treffer, entschieden=entschieden, konsistent=konsistenz(vergleiche),
        einigkeit=uebereinstimmung(vergleiche), personen=sorted({v.person for v in vergleiche}),
        anzahl=len(vergleiche), gewichte=gewichte)
