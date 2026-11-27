"""
Regelkonflikte: Warum erreicht selbst der Optimierer nur ~55–60 von 100 Punkten?

Für jede weiche Regel, die im besten gefundenen Grundriss noch verletzt ist, macht die Analyse zwei Experimente:

  1. „Allein“:  Nur diese eine weiche Regel zählt (alle harten Regeln weiterhin). Ist sie dann immer noch
                verletzt, liegt es am Raum selbst (z. B. jede passende Wand hat ein Fenster) → RAUM.
  2. „Erzwingen“: Die Regel zählt 5-mal so viel. Der beste Grundriss, der sie erfüllt, zeigt den PREIS:
                So viel (gewichtete) Strafe kommt bei den anderen Regeln dazu. Die Regeln, die dabei schlechter
                werden, sind ihre Konfliktpartner → KONFLIKT.
                Ist der Preis kleiner als die eigene Strafe, war der Ausgangs-Grundriss gar nicht der beste –
                der Optimierer hatte etwas übersehen → SUCHE (der bessere Grundriss wird übernommen).

Jedes Experiment bekommt alle bisher gefundenen Grundrisse als zusätzliche Kandidaten. Darum ist jeder Preis
durch einen echten, machbaren Grundriss belegt und nicht bloß ein Zufall der Suche.

Außerdem: der **relative Score** = Score / Obergrenze. 61 Punkte klingen schlecht, sind aber vielleicht fast
alles, was in diesem Zimmer geht. Die **Obergrenze** zählt nur die Raum-Grenzen (Fall 1) – sie ist optimistisch,
weil sie annimmt, alle Konflikte ließen sich gleichzeitig lösen.

Die Regeln selbst werden nicht verändert – die Analyse rechnet nur mit veränderten Gewichten.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .bewertung import Ergebnis, bewerte
from .modell import Layout
from .optimierer import optimiere
from .regeln import anwendbare_regeln

SCHWELLE_VERLETZT = 0.05      # Strafe ab der eine Regel als „verletzt“ gilt
FAKTOR_ERZWINGEN = 5.0        # so viel stärker zählt die Regel im Experiment „Erzwingen“


def score_aus_summe(summe: float) -> float:
    """Gleiche Formel wie in bewertung.py: 100 / (1 + Σ Gewicht·Strafe / 5)."""
    return 100.0 / (1.0 + summe / 5.0)


def relativer_score(score: float, bestwert: float) -> float:
    """Score in Prozent eines Vergleichswerts (Bestwert oder Obergrenze desselben Zimmers), höchstens 100 %."""
    if bestwert <= 0:
        return 0.0
    return min(100.0, 100.0 * score / bestwert)


@dataclass
class RegelKonflikt:
    id: str
    titel: str
    gewicht: float
    strafe: float                        # im Ausgangs-Grundriss
    kostet_punkte: float                 # so viel Score bringt es, wenn nur diese Strafe wegfiele
    strafe_allein: float                 # Strafe, wenn nur diese Regel optimiert wird
    strafe_erzwungen: float              # Strafe im Experiment „Erzwingen“
    preis: Optional[float]               # zusätzliche gewichtete Strafe der anderen, um sie zu erfüllen
    partner: list[tuple[str, float]] = field(default_factory=list)   # (Regel-ID, Verschlechterung)
    art: str = ""                        # "raum" | "konflikt" | "suche"

    @property
    def erklaerung(self) -> str:
        if self.art == "raum":
            return "liegt am Raum: auch allein nicht erfüllbar"
        if self.art == "suche":
            return "der Optimierer hatte einen besseren Grundriss übersehen"
        namen = ", ".join(p for p, _ in self.partner[:3]) or "vielen kleinen Strafen"
        return f"Konflikt mit {namen} (Erfüllen kostet die anderen {self.preis:.2f} Strafpunkte)"


@dataclass
class Konfliktbericht:
    raum: str
    start_score: float                   # bester Score aus zwei normalen Optimierer-Durchgängen
    bestwert: float                      # bester Score nach der Analyse (kann höher sein, siehe „suche“)
    rauschen: float                      # Unterschied der zwei normalen Durchgänge
    obergrenze: float                    # Score, wenn nur die Raum-Grenzen übrig blieben
    konflikte: list[RegelKonflikt]
    bestes: Optional[tuple[Layout, Ergebnis]] = None

    def text(self) -> str:
        z = [f"Regelkonflikte – {self.raum}",
             f"  Optimierer (2 Durchgänge): {self.start_score:.1f}  (Unterschied der Durchgänge: {self.rauschen:.1f})",
             f"  Bester Score nach der Analyse: {self.bestwert:.1f}",
             f"  Obergrenze, wenn nur Raum-Grenzen übrig wären: {self.obergrenze:.1f}"
             f"  → {relativer_score(self.bestwert, self.obergrenze):.0f} % davon erreicht", ""]
        if not self.konflikte:
            z.append("  Im besten Grundriss ist keine weiche Regel verletzt.")
        for k in self.konflikte:
            z.append(f"  [{k.id}] {k.titel}: Strafe {k.strafe:.2f} × Gewicht {k.gewicht} "
                     f"(kostet {k.kostet_punkte:.1f} Punkte) – {k.erklaerung}")
        return "\n".join(z)

    def markdown(self) -> str:
        z = ["| Regel | Strafe × Gewicht | kostet Punkte | Strafe allein | Preis fürs Erfüllen | Ursache |",
             "|---|---|---|---|---|---|"]
        for k in self.konflikte:
            partner = ", ".join(f"{p} (+{g:.2f})" for p, g in k.partner[:3])
            ursache = {"raum": "**Raum**", "suche": "**Suche** (besserer Grundriss gefunden)",
                       "konflikt": f"**Konflikt** mit {partner or 'vielen kleinen Strafen'}"}[k.art]
            preis = "–" if k.preis is None else f"{k.preis:.2f}"
            z.append(f"| {k.id} {k.titel} | {k.strafe:.2f} × {k.gewicht} | {k.kostet_punkte:.1f} | "
                     f"{k.strafe_allein:.2f} | {preis} | {ursache} |")
        return "\n".join(z)


def _bestes(layout: Layout, gewichte: dict[str, float], iterationen: int, neustarts: int, seed: int,
            zusaetzlich: Optional[list[Layout]] = None) -> tuple[Layout, Ergebnis]:
    """Bester machbarer Grundriss für diese Gewichte. `zusaetzlich` = bekannte Grundrisse, die mit ins Rennen gehen."""
    ergebnisse = optimiere(layout, iterationen=iterationen, neustarts=neustarts, gewichte=gewichte,
                           seed=seed, anzahl_ergebnisse=neustarts, ausgabe=False)
    ergebnisse += [(lay, bewerte(lay, gewichte)) for lay in (zusaetzlich or [])]
    machbar = [le for le in ergebnisse if le[1].machbar]
    return min(machbar or ergebnisse, key=lambda le: le[1].kosten)


def _gewichtete_strafen(erg: Ergebnis, gewichte: dict[str, float]) -> dict[str, float]:
    return {rid: gewichte[rid] * erg.strafen.get(rid, 0.0) for rid in gewichte}


def analysiere_konflikte(layout: Layout, iterationen: int = 2000, neustarts: int = 4, seed: int = 2026,
                         gewichte: Optional[dict[str, float]] = None, max_regeln: int = 12,
                         fortschritt: Callable[[str], None] = print) -> Konfliktbericht:
    weich = [r for r in anwendbare_regeln(layout.raum.raumtyp) if r.kategorie != "hart"]
    basis = {r.id: (gewichte or {}).get(r.id, r.gewicht) for r in weich}
    titel = {r.id: r.titel for r in weich}

    fortschritt("Bester Grundriss mit allen Regeln (2 Durchgänge) …")
    lay_a, erg_a = _bestes(layout, basis, iterationen, neustarts, seed)
    lay_b, erg_b = _bestes(layout, basis, iterationen, neustarts, seed + 1)
    rauschen = abs(erg_a.score - erg_b.score)
    lay0, erg0 = (lay_a, erg_a) if erg_a.kosten <= erg_b.kosten else (lay_b, erg_b)
    w0 = _gewichtete_strafen(erg0, basis)
    summe0 = sum(w0.values())
    bekannt = [lay_a, lay_b]
    bester = (lay0, erg0)

    verletzt = sorted((rid for rid in basis if erg0.strafen.get(rid, 0) > SCHWELLE_VERLETZT and basis[rid] > 0),
                      key=lambda rid: -w0[rid])[:max_regeln]

    konflikte = []
    raum_rest = 0.0
    for i, rid in enumerate(verletzt, 1):
        fortschritt(f"  {i}/{len(verletzt)}  {rid} {titel[rid]} …")
        # 1. Allein: nur diese weiche Regel zählt
        allein = {k: (v if k == rid else 0.0) for k, v in basis.items()}
        lay_allein, erg_allein = _bestes(layout, allein, iterationen, neustarts, seed, bekannt)
        strafe_allein = erg_allein.strafen.get(rid, 0.0) if erg_allein.machbar else erg0.strafen[rid]
        # 2. Erzwingen: Regel zählt 5-mal – was kostet es die anderen?
        stark = dict(basis, **{rid: basis[rid] * FAKTOR_ERZWINGEN})
        lay_stark, erg_stark = _bestes(layout, stark, iterationen, neustarts, seed, bekannt + [lay_allein])
        bekannt += [lay_allein, lay_stark]

        for kand in (lay_allein, lay_stark):             # nebenbei besseren Grundriss für ALLE Regeln gefunden?
            e_k = bewerte(kand, basis)
            if e_k.machbar and e_k.kosten < bester[1].kosten - 1e-6:
                bester = (kand, e_k)

        # Preis: günstigster bekannter Grundriss, der die Regel (fast) so gut erfüllt wie allein möglich
        ziel = strafe_allein + SCHWELLE_VERLETZT
        preis, partner, strafe_erzw = None, [], bewerte(lay_stark, basis).strafen.get(rid, 0.0)
        for kand in (lay_stark, lay_allein):
            e_k = bewerte(kand, basis)
            if not e_k.machbar or e_k.strafen.get(rid, 0.0) > ziel:
                continue
            w_k = _gewichtete_strafen(e_k, basis)
            p = sum(w_k[k] - w0[k] for k in basis if k != rid)
            if preis is None or p < preis:
                preis = p
                partner = sorted(((k, w_k[k] - w0[k]) for k in basis if k != rid and w_k[k] - w0[k] > 0.1),
                                 key=lambda kg: -kg[1])

        if strafe_allein > SCHWELLE_VERLETZT:
            art = "raum"
            raum_rest += basis[rid] * strafe_allein
        elif preis is not None and preis < w0[rid] - (basis[rid] * strafe_allein):
            art = "suche"
        else:
            art = "konflikt"
        konflikte.append(RegelKonflikt(
            id=rid, titel=titel[rid], gewicht=basis[rid], strafe=erg0.strafen[rid],
            kostet_punkte=score_aus_summe(summe0 - w0[rid]) - score_aus_summe(summe0),
            strafe_allein=strafe_allein, strafe_erzwungen=strafe_erzw, preis=preis, partner=partner, art=art))

    return Konfliktbericht(raum=layout.raum.name, start_score=erg0.score, bestwert=bester[1].score,
                           rauschen=rauschen, obergrenze=max(score_aus_summe(raum_rest), bester[1].score),
                           konflikte=konflikte, bestes=bester)
