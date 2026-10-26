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
    if m.ist_deckenobjekt:          # Pendelleuchte / Ventilator: irgendwo an der Decke
        m.x = rng.uniform(0.3, layout.raum.breite - 0.3)
        m.y = rng.uniform(0.3, layout.raum.tiefe - 0.3)
        return
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


def _stuehle_um_tisch(layout: Layout, tisch: Moebel, stuehle: list[Moebel]) -> None:
    """Stühle gleichmäßig an die beiden langen Tischseiten verteilen, Blick zum Tisch, keiner an den Ecken."""
    fx, fy = tisch.vorne
    rx, ry = fy, -fx
    lang_entlang_breite = tisch.breite >= tisch.tiefe
    if lang_entlang_breite:
        a_vec, n_vec, laenge, abst = (rx, ry), (fx, fy), tisch.breite, tisch.tiefe / 2
    else:
        a_vec, n_vec, laenge, abst = (fx, fy), (rx, ry), tisch.tiefe, tisch.breite / 2
    pro_seite = max(1, int(laenge // 0.55))           # ca. 55 cm Platz pro Person
    lang = stuehle[: 2 * pro_seite]
    kopf = stuehle[2 * pro_seite:]
    for vorz, gruppe in zip((1, -1), (lang[0::2], lang[1::2])):
        k = len(gruppe)
        for i, s in enumerate(gruppe):
            entlang = ((i + 1) / (k + 1) - 0.5) * laenge   # gleichmäßig, Abstand zu den Ecken
            raus = vorz * (abst + s.tiefe / 2 - 0.12)      # leicht unter den Tisch geschoben
            s.x = tisch.x + a_vec[0] * entlang + n_vec[0] * raus
            s.y = tisch.y + a_vec[1] * entlang + n_vec[1] * raus
            s.rot = VEKTOR_ROT[(-vorz * n_vec[0], -vorz * n_vec[1])]   # schaut zum Tisch
    for vorz, s in zip((1, -1), kopf):                    # übrige Stühle an die Kopfenden
        raus = vorz * (laenge / 2 + s.tiefe / 2 - 0.12)
        s.x = tisch.x + a_vec[0] * raus
        s.y = tisch.y + a_vec[1] * raus
        s.rot = VEKTOR_ROT[(-vorz * a_vec[0], -vorz * a_vec[1])]


def kinder_platzieren(layout: Layout) -> None:
    """Nachttische, Couchtisch, Bank am Fußende usw. relativ zum Elternmöbel setzen."""
    for tisch in layout.finde("esstisch"):
        stuehle = [k for k in layout.moebel if k.gehoert_zu == tisch.name and k.typ == "stuhl"]
        if stuehle:
            _stuehle_um_tisch(layout, tisch, stuehle)
    for k in layout.moebel:
        if not k.gehoert_zu or (k.typ == "stuhl" and (p := layout.nach_name(k.gehoert_zu)) and p.typ == "esstisch"):
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


# ------------------------------------------------------------------ Minimal-Korrektur
from dataclasses import dataclass as _dataclass, field as _field


@_dataclass
class Aenderung:
    name: str
    typ: str
    von: tuple[float, float]
    nach: tuple[float, float]
    rot_von: int
    rot_nach: int
    gruende: list[str] = _field(default_factory=list)

    @property
    def gedreht(self) -> bool:
        return self.rot_von % 360 != self.rot_nach % 360

    @property
    def strecke(self) -> float:
        return math.dist(self.von, self.nach)

    def text(self) -> str:
        t = f"{self.name}: {self.strecke:.2f} m verschieben"
        if self.gedreht:
            t += f" und drehen ({_RICHTUNG[self.rot_von % 360]} → {_RICHTUNG[self.rot_nach % 360]})"
        return t


_RICHTUNG = {0: "oben", 90: "rechts", 180: "unten", 270: "links"}


def _bewegungskosten(neu: Layout, ist: dict, preis_m: float, preis_drehung: float) -> float:
    k = 0.0
    for m in neu.moebel:
        a = ist.get(m.name)
        if a is None:
            continue
        k += preis_m * math.dist((m.x, m.y), (a[0], a[1]))
        if m.rot % 360 != a[2] % 360 and not m.gehoert_zu:
            k += preis_drehung
    return k


def korrigiere(ist: Layout, gewichte: Optional[dict[str, float]] = None, iterationen: int = 2500,
               neustarts: int = 3, preis_pro_meter: float = 4.0, preis_drehung: float = 3.0,
               seed: Optional[int] = None, ausgabe: bool = True):
    """Verbessert die JETZIGE Einrichtung mit möglichst wenig Umstellen.

    Jeder Meter Verschieben kostet `preis_pro_meter` Punkte, jede Drehung `preis_drehung` –
    ein Möbel wird also nur bewegt, wenn es dadurch deutlich besser wird.
    Rückgabe: (neues Layout, Ergebnis, Liste der Änderungen, Ergebnis vorher)
    """
    rng = random.Random(seed)
    ist_pos = {m.name: (m.x, m.y, m.rot) for m in ist.moebel}
    e_ist = bewerte(ist, gewichte)

    def kosten(lay, erg):
        return erg.kosten + _bewegungskosten(lay, ist_pos, preis_pro_meter, preis_drehung)

    bestes_g, k_best_g, e_best_g = ist.kopie(), kosten(ist, e_ist), e_ist

    # 1) Systematisch: jedes bewegliche Möbel probeweise an jede Wand / jede Position (10-cm-Raster)
    for _ in range(2):
        verbessert = False
        for m in _beweglich(bestes_g):
            if m.ist_deckenobjekt:
                continue
            for wand in WAENDE:
                L = bestes_g.raum.wandlaenge(wand)
                halb = m.breite / 2
                pos = halb
                while pos <= L - halb + 1e-9:
                    for tausch in (False, True):     # einzelnen Nachttisch auch auf die andere Seite
                        test = bestes_g.kopie()
                        kinder = [k for k in test.moebel if k.gehoert_zu == m.name and k.seite in ("links", "rechts")]
                        if tausch:
                            if len(kinder) != 1:
                                continue
                            kinder[0].seite = "rechts" if kinder[0].seite == "links" else "links"
                        an_wand_setzen(test.nach_name(m.name), test, wand, pos)
                        kinder_platzieren(test)
                        e_t = bewerte(test, gewichte)
                        k_t = kosten(test, e_t)
                        if k_t < k_best_g - 1e-6:
                            bestes_g, k_best_g, e_best_g, verbessert = test, k_t, e_t, True
                    pos += 0.1
        if not verbessert:
            break
    start = bestes_g.kopie()

    # 2) Simulated Annealing zum Feinschliff
    t_start, t_ende = 3.0, 0.02
    for lauf in range(neustarts):
        aktuell, e_akt = start.kopie(), e_best_g
        k_akt = kosten(aktuell, e_akt)
        bestes, k_best, e_best = aktuell, k_akt, e_akt
        for i in range(iterationen):
            anteil = 1 - i / iterationen
            T = t_start * (t_ende / t_start) ** (i / iterationen)
            neu = _nachbar(aktuell, rng, 0.25 + 0.5 * anteil)
            e_neu = bewerte(neu, gewichte)
            k_neu = kosten(neu, e_neu)
            if k_neu < k_akt or rng.random() < math.exp(-(k_neu - k_akt) / T):
                aktuell, e_akt, k_akt = neu, e_neu, k_neu
                if k_akt < k_best:
                    bestes, k_best, e_best = aktuell, k_akt, e_akt
        if ausgabe:
            print(f"  Lauf {lauf + 1}/{neustarts}: Score {e_best.score:5.1f}"
                  f"{'' if e_best.machbar else ' (NICHT machbar)'}")
        if k_best < k_best_g:
            bestes_g, k_best_g, e_best_g = bestes, k_best, e_best

    # Unnötige Mini-Bewegungen zurücknehmen (Möbel zurückstellen, wenn es nichts verschlechtert)
    for m in bestes_g.moebel:
        a = ist_pos[m.name]
        if (m.x, m.y, m.rot) == a or m.gehoert_zu:
            continue
        test = bestes_g.kopie()
        t = test.nach_name(m.name)
        t.x, t.y, t.rot = a
        kinder_platzieren(test)
        e_t = bewerte(test, gewichte)
        if e_t.machbar and kosten(test, e_t) <= k_best_g + 1e-6:
            bestes_g, k_best_g, e_best_g = test, kosten(test, e_t), e_t

    aenderungen = []
    for m in bestes_g.moebel:
        x0, y0, r0 = ist_pos[m.name]
        if m.gehoert_zu:        # Nachttisch & Co. drehen nur, wenn das Elternmöbel gedreht wird
            p = bestes_g.nach_name(m.gehoert_zu)
            if p is not None and p.rot % 360 == ist_pos[p.name][2] % 360:
                r0 = m.rot
        if math.dist((m.x, m.y), (x0, y0)) > 0.08 or (r0 % 360 != m.rot % 360):
            gruende = sorted({b.text for bs in e_ist.befunde.values() for b in bs if b.moebel == m.name})
            if m.gehoert_zu and not gruende:
                gruende = [f"wandert mit {m.gehoert_zu}"]
            aenderungen.append(Aenderung(m.name, m.typ, (round(x0, 2), round(y0, 2)), (round(m.x, 2), round(m.y, 2)),
                                         r0, m.rot, gruende))
    return bestes_g, e_best_g, aenderungen, e_ist
