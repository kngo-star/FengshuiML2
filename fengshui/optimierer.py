"""
Optimierer: findet automatisch gute Möbelanordnungen.

Verfahren: Simulated Annealing (stochastische Suche) mit mehreren Neustarts.
Zielfunktion = Kosten aus der Regelbasis (harte Regeln stark bestraft) – optional mit
persönlich gelernten Gewichten aus ml.py.
"""
from __future__ import annotations

import math
import random
from typing import Optional

from .bewertung import Ergebnis, bewerte
from .modell import ROT_VEKTOR, VEKTOR_ROT, WAND_NORMALE, WAENDE, Layout, Moebel


# ------------------------------------------------------------------ Platzierungshelfer
def an_wand_setzen(m: Moebel, layout: Layout, wand: str, pos: float) -> None:
    """Setzt Möbel mit der Rückseite an `wand`; `pos` = Mittelpunkt entlang der Wand."""
    raum = layout.raum
    n = WAND_NORMALE[wand]
    m.rot = VEKTOR_ROT[n]
    dx, dy = m.ausdehnung
    if wand == "unten":
        m.x, m.y = pos, dy / 2
    elif wand == "oben":
        m.x, m.y = pos, raum.tiefe - dy / 2
    elif wand == "links":
        m.x, m.y = dx / 2, pos
    else:
        m.x, m.y = raum.breite - dx / 2, pos


def _zufall_an_wand(m: Moebel, layout: Layout, rng: random.Random) -> None:
    wand = rng.choice(WAENDE)
    L = layout.raum.wandlaenge(wand)
    halb = m.breite / 2
    if L <= 2 * halb:
        pos = L / 2
    else:
        pos = rng.uniform(halb, L - halb)
    an_wand_setzen(m, layout, wand, pos)


def _klemmen(m: Moebel, layout: Layout) -> None:
    dx, dy = m.ausdehnung
    m.x = min(max(m.x, dx / 2), layout.raum.breite - dx / 2)
    m.y = min(max(m.y, dy / 2), layout.raum.tiefe - dy / 2)


def kinder_platzieren(layout: Layout) -> None:
    """Nachttische, Couchtisch, Bank am Fußende usw. relativ zum Elternmöbel setzen."""
    for k in layout.moebel:
        if not k.gehoert_zu:
            continue
        p = layout.nach_name(k.gehoert_zu)
        if p is None:
            continue
        fx, fy = p.vorne
        rx, ry = fy, -fx                       # "rechts" aus Sicht der Person
        k.rot = p.rot
        if k.seite in ("links", "rechts"):
            s = 1 if k.seite == "rechts" else -1
            # bündig mit der Rückseite (Kopfteil) des Elternmöbels
            vor = -(p.tiefe / 2 - k.tiefe / 2)
            quer = s * (p.breite / 2 + k.breite / 2 + k.abstand)
            k.x = p.x + fx * vor + rx * quer
            k.y = p.y + fy * vor + ry * quer
        elif k.seite == "vorne":
            vor = p.tiefe / 2 + k.abstand + k.tiefe / 2
            k.x, k.y = p.x + fx * vor, p.y + fy * vor
        elif k.seite == "hinten":
            vor = -(p.tiefe / 2 + k.abstand + k.tiefe / 2)
            k.x, k.y = p.x + fx * vor, p.y + fy * vor


def _beweglich(layout: Layout) -> list[Moebel]:
    return [m for m in layout.moebel if not m.fest and not m.gehoert_zu]


def zufallslayout(layout: Layout, rng: random.Random) -> Layout:
    neu = layout.kopie()
    for m in _beweglich(neu):
        _zufall_an_wand(m, neu, rng)
    kinder_platzieren(neu)
    return neu


def _nachbar(layout: Layout, rng: random.Random, temperatur_anteil: float) -> Layout:
    neu = layout.kopie()
    bew = _beweglich(neu)
    if not bew:
        return neu
    m = rng.choice(bew)
    zug = rng.random()
    if m.ist_wandobjekt:
        if zug < 0.5:
            _zufall_an_wand(m, neu, rng)
        else:
            # entlang der Wand schieben
            vx, vy = m.vorne
            schritt = rng.gauss(0, 0.5 * temperatur_anteil + 0.1)
            if vx == 0:
                m.x += schritt
            else:
                m.y += schritt
            _klemmen(m, neu)
    elif zug < 0.30:
        _zufall_an_wand(m, neu, rng)
    elif zug < 0.60:
        # entlang der Wand gleiten (Rückseite bleibt an der Wand)
        vx, vy = m.vorne
        schritt = rng.gauss(0, 0.6 * temperatur_anteil + 0.08)
        if vx == 0:
            m.x += schritt
        else:
            m.y += schritt
        _klemmen(m, neu)
    elif zug < 0.75:
        # freie Verschiebung (z.B. Esstisch in die Mitte, Sofa frei stehend)
        m.x += rng.gauss(0, 0.5 * temperatur_anteil + 0.05)
        m.y += rng.gauss(0, 0.5 * temperatur_anteil + 0.05)
        _klemmen(m, neu)
    elif zug < 0.87:
        m.rot = rng.choice([0, 90, 180, 270])
        _klemmen(m, neu)
    else:
        # zwei Möbel tauschen ihre Plätze
        andere = [o for o in bew if o is not m and not o.ist_wandobjekt]
        if andere:
            o = rng.choice(andere)
            m.x, o.x = o.x, m.x
            m.y, o.y = o.y, m.y
            m.rot, o.rot = o.rot, m.rot
            _klemmen(m, neu)
            _klemmen(o, neu)
    kinder_platzieren(neu)
    return neu


# ------------------------------------------------------------------ Simulated Annealing
def optimiere(layout: Layout, iterationen: int = 3000, neustarts: int = 6,
              gewichte: Optional[dict[str, float]] = None, seed: Optional[int] = None,
              anzahl_ergebnisse: int = 3, ausgabe: bool = True) -> list[tuple[Layout, Ergebnis]]:
    """Gibt die besten, voneinander verschiedenen Layouts zurück (bestes zuerst)."""
    rng = random.Random(seed)
    kandidaten: list[tuple[Layout, Ergebnis]] = []
    t_start, t_ende = 6.0, 0.03

    for lauf in range(neustarts):
        aktuell = zufallslayout(layout, rng)
        e_akt = bewerte(aktuell, gewichte)
        bestes, e_best = aktuell, e_akt
        for i in range(iterationen):
            anteil = 1 - i / iterationen
            T = t_start * (t_ende / t_start) ** (i / iterationen)
            neu = _nachbar(aktuell, rng, anteil)
            e_neu = bewerte(neu, gewichte)
            delta = e_neu.kosten - e_akt.kosten
            if delta < 0 or rng.random() < math.exp(-delta / T):
                aktuell, e_akt = neu, e_neu
                if e_akt.kosten < e_best.kosten:
                    bestes, e_best = aktuell, e_akt
        # Feinschliff: nur noch Verbesserungen annehmen (Hill Climbing mit kleinen Schritten)
        for _ in range(iterationen // 4):
            neu = _nachbar(bestes, rng, 0.1)
            e_neu = bewerte(neu, gewichte)
            if e_neu.kosten < e_best.kosten:
                bestes, e_best = neu, e_neu
        if ausgabe:
            status = "machbar" if e_best.machbar else "NICHT machbar"
            print(f"  Lauf {lauf + 1}/{neustarts}: Score {e_best.score:5.1f} ({status})")
        kandidaten.append((bestes, e_best))

    kandidaten.sort(key=lambda le: le[1].kosten)
    # nur deutlich verschiedene Layouts behalten
    vielfalt: list[tuple[Layout, Ergebnis]] = []
    for lay, erg in kandidaten:
        if all(_unterschied(lay, v[0]) > 0.5 for v in vielfalt):
            vielfalt.append((lay, erg))
        if len(vielfalt) >= anzahl_ergebnisse:
            break
    return vielfalt


def _unterschied(a: Layout, b: Layout) -> float:
    return sum(math.hypot(m.x - n.x, m.y - n.y) + (0.5 if m.rot != n.rot else 0)
               for m, n in zip(a.moebel, b.moebel))
