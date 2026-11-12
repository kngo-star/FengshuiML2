"""
LEERES ZIMMER EINRICHTEN – Foto eines leeren Raums rein, eingerichtetes Zimmer + Einkaufsliste raus.

Ablauf
------
1. Vermessen:   foto3d.py bestimmt aus dem Foto Raumgröße, Tür, Fenster und die Kamera.
2. Auswählen:   Je nach Raumtyp und Raumgröße wird aus dem Produktkatalog (produkte.json) eine Einrichtung
                zusammengestellt – nach den Regeln der Buch-Regelbasis (z. B. gepolstertes Kopfteil, zwei runde
                Nachttische, runder Couchtisch, keine Pflanzen/Spiegel/Bildschirme im Schlafzimmer, mehrere
                niedrige Lichtquellen, alle fünf Elemente im Raum).
3. Platzieren:  Der vorhandene Optimierer (optimierer.py) stellt die Möbel mit der Regelbasis (regeln.py)
                so, dass Kommandoposition, Chi-Fluss, Laufwege usw. stimmen. Passt etwas nicht in den Raum,
                wird das unwichtigste Stück weggelassen.
4. Zeichnen:    render3d.py zeichnet die Möbel maßstabsgetreu ins Foto.
5. Einkaufen:   katalog.py schreibt die nummerierte Einkaufsliste mit Shop-Links (Affiliate) und der
                Begründung zu jedem Produkt.

Ehrliche Grenzen
----------------
• Das Bild ist eine 3D-Skizze im Foto, kein Foto-Realismus (optional: fengshui/realistisch.py).
• Die Links führen zur Shop-Suche nach einem passenden Produkt-Typ, solange in produkte.json kein
  bestimmtes Produkt verlinkt ist. Preise sind grobe Richtpreise.
• Maße aus einem Foto sind auf etwa ±10–20 cm genau – vor dem Kauf nachmessen.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from .bewertung import Ergebnis, bewerte
from .katalog import (ELEMENT_NAME, STILE, Position, Produkt, einkaufsliste_daten, einkaufsliste_html,
                      einkaufsliste_text, hex_zu_rgb, lade_produkte, lade_shops)
from .modell import VEKTOR_WAND, Bewohner, Layout, Moebel
from .optimierer import kinder_platzieren, optimiere

RAUMTYPEN = ("schlafzimmer", "gaestezimmer", "kinderzimmer", "wohnzimmer", "esszimmer", "buero", "studio")
ELEMENTE = ("holz", "feuer", "erde", "metall", "wasser")


# ====================================================================== 1. Auswahl
@dataclass
class Wunsch:
    """Ein Stück der Einrichtung, bevor es platziert ist."""
    pid: str                               # Produkt-ID aus produkte.json
    name: str                              # Name im Grundriss
    prio: int = 1                          # 1 = muss, 2 = soll, 3 = schön zu haben (wird zuerst weggelassen)
    gehoert_zu: Optional[str] = None       # hängt an diesem Möbel (Nachttisch → Bett)
    seite: Optional[str] = None            # "links" | "rechts" | "vorne" | "auf" | "unter"
    abstand: float = 0.02
    quer: bool = False                     # Teppich quer legen (lange Seite quer zum Möbel)
    menge: int = 1                         # nur für Zubehör ohne eigenes Möbel im Grundriss


def _teppich(raum, wunschgroesse: list[str], produkte: dict) -> Optional[str]:
    """Größten Teppich aus der Wunschliste nehmen, der gut in den Raum passt."""
    kurz = min(raum.breite, raum.tiefe)
    for pid in wunschgroesse:
        if max(produkte[pid].masse[0], produkte[pid].masse[1]) <= kurz - 0.4:
            return pid
    return None


def _plan(raum, bewohner: Bewohner, produkte: dict, mit_tv: bool = True) -> list[Wunsch]:
    """Einrichtungsplan für den Raumtyp – jede Entscheidung folgt einer Regel aus der Buch-Regelbasis."""
    A = raum.breite * raum.tiefe
    kurz, lang = min(raum.breite, raum.tiefe), max(raum.breite, raum.tiefe)
    fenster = len(raum.fenster)
    rt = raum.raumtyp
    W = Wunsch
    w: list[Wunsch] = []

    if rt in ("schlafzimmer", "gaestezimmer"):
        if bewohner.paar:
            bett = "bett-180" if (A >= 15 and kurz >= 3.4) else "bett-160"
        else:
            bett = "bett-90" if A < 8 else "bett-120" if A < 10 else "bett-140" if A < 17 else "bett-160"
        bb = produkte[bett].masse[0]
        w += [W(bett, "Bett", 1),
              W("nachttisch-rund", "Nachttisch links", 1, "Bett", "links"),
              W("nachttisch-rund", "Nachttisch rechts", 2, "Bett", "rechts"),
              W("schrank-100" if A < 9 else "schrank-150" if A < 15 else "schrank-200", "Kleiderschrank", 1),
              W("tischleuchte", "Leuchte links", 2, "Nachttisch links", "auf"),
              W("tischleuchte", "Leuchte rechts", 2, "Nachttisch rechts", "auf")]
        t = _teppich(raum, ["teppich-200x290"] if bb > 1.75 else ["teppich-160x230", "teppich-140x200"]
                     if bb > 1.15 else ["teppich-140x200"], produkte)
        if t:
            w.append(W(t, "Teppich", 2, "Bett", "unter", abstand=0.55, quer=True))
        if A >= 11:
            w.append(W("kommode-100", "Kommode", 3))
        w.append(W("bild-landschaft", "Bild", 3))
        if A >= 10:
            w.append(W("stehleuchte", "Stehleuchte", 3))
        if bewohner.pflanzen_sind_freunde:                     # Buch: sonst keine Pflanzen im Schlafzimmer
            w.append(W("pflanze-monstera", "Monstera", 3))
        if fenster:
            w.append(W("vorhang-verdunkelung", "Vorhänge", 2, menge=fenster))
        w.append(W("bettwaesche-hell", "Bettwäsche", 2))

    elif rt == "kinderzimmer":
        w += [W("bett-90", "Bett", 1),
              W("nachttisch-rund", "Nachttisch", 2, "Bett", "links"),
              W("schrank-100", "Kleiderschrank", 1),
              W("schreibtisch-100", "Schreibtisch", 2),
              W("stuhl-buero", "Schreibtischstuhl", 2, "Schreibtisch"),
              W("tischleuchte", "Nachtlicht", 2, "Nachttisch", "auf")]
        t = _teppich(raum, ["teppich-140x200"], produkte)
        if t:
            w.append(W(t, "Teppich", 3, "Bett", "unter", abstand=0.9, quer=False))
        w += [W("regal-niedrig", "Regal", 3), W("stehleuchte", "Stehleuchte", 3),
              W("pflanze-geldbaum", "Geldbaum", 3), W("bild-landschaft", "Bild", 3)]
        if fenster:
            w.append(W("vorhang-verdunkelung", "Vorhänge", 2, menge=fenster))
        w.append(W("bettwaesche-hell", "Bettwäsche", 2))

    elif rt == "wohnzimmer":
        sofa = "sofa-3" if (A >= 16 and lang >= 3.8) else "sofa-2"
        st = produkte[sofa].masse[1]
        w += [W(sofa, "Sofa", 1),
              W("couchtisch-rund", "Couchtisch", 1, "Sofa", "vorne", abstand=0.45),
              W("sessel", "Sessel", 2)]
        t = _teppich(raum, ["teppich-200x290", "teppich-160x230"] if A >= 16 else ["teppich-160x230"], produkte)
        if t:
            w.append(W(t, "Teppich", 2, "Sofa", "unter", abstand=st / 2 + 0.45 + 0.3, quer=True))
        w.append(W("sideboard-160" if A >= 14 else "kommode-100", "Sideboard", 2))
        w += [W("stehleuchte", "Stehleuchte", 2),
              W("pflanze-monstera", "Monstera", 2),
              W("pflanze-geldbaum", "Geldbaum", 3, "Monstera", "rechts", abstand=0.1),
              W("tischleuchte", "Tischleuchte", 3, "Sideboard", "auf"),
              W("pendelleuchte-rund", "Pendelleuchte", 3, "Couchtisch", "auf")]
        if mit_tv:
            w.append(W("tv-lowboard", "TV-Lowboard", 3))
        w += [W("spiegel-wand", "Spiegel", 3), W("bild-landschaft", "Bild", 3)]
        if A >= 22:
            w.append(W("sessel", "Sessel 2", 3))
        if fenster:
            w.append(W("vorhang-leicht", "Vorhänge", 2, menge=fenster))
        w.append(W("obstschale", "Obstschale", 3, "Couchtisch"))

    elif rt == "esszimmer":
        gross = A >= 16 and kurz >= 3.6
        tisch, n = ("esstisch-rund-130" if gross else "esstisch-rund-110"), 4      # gerade Anzahl, rundherum
        w.append(W(tisch, "Esstisch", 1))
        w += [W("stuhl-ess", f"Stuhl {i + 1}", 1, "Esstisch") for i in range(n)]
        w += [W("pendelleuchte-rund", "Pendelleuchte", 2, "Esstisch", "auf"),
              W("sideboard-160" if lang >= 3.4 else "kommode-100", "Sideboard", 2),
              W("pflanze-monstera", "Monstera", 2)]
        t = _teppich(raum, ["teppich-rund-200", "teppich-rund-160"] if gross else ["teppich-rund-200"], produkte)
        if t and produkte[t].masse[0] >= produkte[tisch].masse[0] + 0.8:
            w.append(W(t, "Teppich", 3, "Esstisch", "unter", abstand=0.0))
        w += [W("tischleuchte", "Tischleuchte", 3, "Sideboard", "auf"),
              W("stehleuchte", "Stehleuchte", 3),
              W("spiegel-wand", "Spiegel", 3),
              W("bild-froehlich", "Bild", 3)]
        if fenster:
            w.append(W("vorhang-leicht", "Vorhänge", 3, menge=fenster))
        w.append(W("obstschale", "Obstschale", 2, "Esstisch"))

    elif rt == "buero":
        tisch = "schreibtisch-120" if A < 8 else "schreibtisch-140" if A < 13 else "schreibtisch-160"
        w += [W(tisch, "Schreibtisch", 1),
              W("stuhl-buero", "Schreibtischstuhl", 1, "Schreibtisch"),
              W("regal-niedrig", "Regal", 2),
              W("stehleuchte-uplight", "Deckenfluter", 2),
              W("pflanze-monstera", "Monstera", 2),
              W("tischleuchte", "Tischleuchte", 3, "Regal", "auf"),
              W("pflanze-geldbaum", "Geldbaum", 3, "Monstera", "rechts", abstand=0.1),
              W("bild-landschaft", "Bild", 3),
              W("pinnwand", "Pinnwand", 3)]
        if A >= 10:
            w.append(W("kommode-100", "Kommode", 3))
        if A >= 12:
            w.append(W("sessel", "Lesesessel", 3))

    elif rt == "studio":
        st = produkte["sofa-2"].masse[1]
        w += [W("bett-140", "Bett", 1),
              W("nachttisch-rund", "Nachttisch links", 2, "Bett", "links"),
              W("nachttisch-rund", "Nachttisch rechts", 3, "Bett", "rechts"),
              W("sofa-2", "Sofa", 1),
              W("couchtisch-rund", "Couchtisch", 2, "Sofa", "vorne", abstand=0.45),
              W("schrank-150" if A >= 20 else "schrank-100", "Kleiderschrank", 1),
              W("tischleuchte", "Leuchte links", 2, "Nachttisch links", "auf"),
              W("stehleuchte", "Stehleuchte", 2)]
        t = _teppich(raum, ["teppich-160x230"], produkte)
        if t:
            w.append(W(t, "Teppich", 3, "Sofa", "unter", abstand=st / 2 + 0.45 + 0.3, quer=True))
        w += [W("sessel", "Sessel", 3), W("bild-landschaft", "Bild", 3)]
        if fenster:
            w.append(W("vorhang-verdunkelung", "Vorhänge", 2, menge=fenster))
        w.append(W("bettwaesche-hell", "Bettwäsche", 2))
    else:
        raise ValueError(f"Einrichten gibt es für: {', '.join(RAUMTYPEN)} – nicht für '{rt}'.")
    return w


# ====================================================================== 2. Platzierung
@dataclass
class Einrichtung:
    layout: Layout
    ergebnis: Ergebnis
    positionen: list[Position]
    aussehen: dict = field(default_factory=dict)        # Möbelname -> Farben/Variante fürs Bild
    deko: list = field(default_factory=list)            # Vorhänge (nur im Bild, kein Möbel im Grundriss)
    elemente: dict = field(default_factory=dict)        # Element -> Produkte
    hinweise: list[str] = field(default_factory=list)
    weggelassen: list[str] = field(default_factory=list)
    neu: set = field(default_factory=set)               # Namen der neu gestellten Möbel
    stil: str = "natur"
    budget: str = "mittel"

    @property
    def nummern(self) -> dict[str, int]:
        return {name: p.nr for p in self.positionen for name in p.moebel}

    def summe(self) -> float:
        return sum(p.preis(self.budget) for p in self.positionen)

    def text(self, shops: Optional[dict] = None) -> str:
        r = self.layout.raum
        z = [f"EINRICHTUNG ({r.raumtyp}, {r.breite:.2f} × {r.tiefe:.2f} m) – Feng-Shui-Score {self.ergebnis.score:.0f}/100"
             + ("" if self.ergebnis.machbar else "  ⚠ nicht alle praktischen Regeln erfüllt"), ""]
        z.append("DIE FÜNF ELEMENTE")
        for el in ELEMENTE:
            z.append(f"  {ELEMENT_NAME[el]:<7} {', '.join(self.elemente.get(el, [])) or '–'}")
        z.append("")
        z.append(einkaufsliste_text(self.positionen, shops or lade_shops(), self.stil, self.budget))
        if self.hinweise:
            z += ["", "HINWEISE"] + [f"  • {h}" for h in self.hinweise]
        return "\n".join(z)


def _moebel_aus(wunsch: Wunsch, p: Produkt) -> Moebel:
    b, t, h = p.masse
    if wunsch.quer:
        b, t = max(b, t), min(b, t)
    typ = p.typ
    m = Moebel(typ, breite=b, tiefe=t, hoehe=h, name=wunsch.name, rund=p.rund)
    if wunsch.gehoert_zu:
        m.gehoert_zu, m.seite, m.abstand = wunsch.gehoert_zu, wunsch.seite, wunsch.abstand
    return m


def _abhaengige(wuensche: list[Wunsch], name: str) -> set[str]:
    weg = {name}
    geaendert = True
    while geaendert:
        geaendert = False
        for w in wuensche:
            if w.gehoert_zu in weg and w.name not in weg:
                weg.add(w.name)
                geaendert = True
    return weg


def _wand_konflikte(lay: Layout, abstand: float = 0.25, fenster_abstand: float = 0.45) -> float:
    """Praktisch (steht nicht im Buch): Bilder/Spiegel hängen nicht übereinander und nicht hinter dem Vorhang."""
    from . import geometrie as g
    k = 0.0
    wand = [m for m in lay.moebel if m.ist_wandobjekt]
    spannen = []
    for m in wand:
        r = (-m.vorne[0], -m.vorne[1])
        spannen.append((VEKTOR_WAND[r], *g.spanne_quer(m, r)))
    for i, (w1, a1, b1) in enumerate(spannen):
        for w2, a2, b2 in spannen[i + 1:]:
            if w1 == w2 and min(b1, b2) - max(a1, a2) > -abstand:
                k += 1.0
        for f in lay.raum.fenster:
            if f.wand == w1 and min(b1, f.bis) - max(a1, f.von) > -fenster_abstand:
                k += 1.0
    for m in lay.moebel:                    # das TV-Möbel steht mit dem Rücken an einer Wand, nicht quer im Raum
        if m.typ == "tv" and not m.fest:
            k += min(2.0, g.abstand_zur_wand(m, lay.raum, m.hinten) / 0.3)
    return k


def _ort(m: Moebel, layout: Layout) -> str:
    raum = layout.raum
    if m.gehoert_zu:
        wie = {"links": "links neben", "rechts": "rechts neben", "vorne": "vor", "auf": "auf/über",
               "unter": "unter"}.get(m.seite or "", "bei")
        return f"{wie} {m.gehoert_zu}"
    if m.ist_deckenobjekt:
        return "an der Decke"
    x1, y1, x2, y2 = m.rechteck
    abst = {"unten": y1, "oben": raum.tiefe - y2, "links": x1, "rechts": raum.breite - x2}
    wand = VEKTOR_WAND[m.hinten]
    if abst[wand] < 0.15:
        entlang = m.x if wand in ("unten", "oben") else m.y
        return f"an der Wand „{wand}“, Mitte {entlang:.1f} m vom Wandanfang"
    naechste = min(abst, key=abst.get)
    if abst[naechste] < 0.15:
        return f"an der Wand „{naechste}“"
    return "frei im Raum"


def einrichten(basis: Layout, stil: str = "natur", budget: str = "mittel",
               gewichte: Optional[dict] = None, iterationen: int = 3000, neustarts: int = 6,
               seed: Optional[int] = None, sichtbar: Optional[Callable] = None, sichtbar_gewicht: float = 4.0,
               mit_tv: bool = True, produkte: Optional[dict] = None, ausgabe: bool = True,
               max_runden: int = 8) -> Einrichtung:
    """Richtet den Raum in `basis` ein (leer oder mit schon vorhandenen Möbeln, die stehen bleiben).

    sichtbar: optionale Funktion Rechteck -> Anteil 0..1, der im Foto zu sehen ist. Möbel werden dann
              (mit kleinem Gewicht) lieber dorthin gestellt, wo das Foto sie zeigen kann. Die Feng-Shui-Regeln
              haben immer Vorrang.
    """
    if stil not in STILE:
        raise ValueError(f"Stil '{stil}' gibt es nicht – möglich: {', '.join(STILE)}")
    produkte = produkte or lade_produkte()
    raum = basis.raum
    if raum.raumtyp not in RAUMTYPEN:
        raise ValueError(f"Einrichten gibt es für: {', '.join(RAUMTYPEN)} – nicht für '{raum.raumtyp}'.")
    hinweise: list[str] = []

    # ---- vorhandene Möbel bleiben stehen; ihre Typen werden nicht noch einmal gekauft
    bestand = [m.kopie() for m in basis.moebel]
    for m in bestand:
        m.fest = True
    vorhandene_typen = {m.typ for m in bestand}
    wuensche = _plan(raum, basis.bewohner, produkte, mit_tv)
    umbenennen: dict[str, str] = {}
    for w in list(wuensche):
        p = produkte[w.pid]
        if p.typ != "zubehoer" and p.typ in vorhandene_typen and not w.gehoert_zu:
            alt = next(m for m in bestand if m.typ == p.typ)
            umbenennen[w.name] = alt.name
            wuensche.remove(w)
            hinweise.append(f"{alt.name} ist schon da – kein neues Stück vom Typ „{p.typ}“ eingeplant.")
    for w in list(wuensche):
        p = produkte[w.pid]
        if p.typ != "zubehoer" and p.typ in vorhandene_typen and w.gehoert_zu:
            wuensche.remove(w)                                  # z. B. Nachttische, wenn schon welche da sind
            continue
        if w.gehoert_zu in umbenennen:
            w.gehoert_zu = umbenennen[w.gehoert_zu]

    def zusatz(lay: Layout) -> float:
        k = 3.0 * _wand_konflikte(lay)
        if sichtbar is not None and sichtbar_gewicht > 0:
            for m in lay.moebel:
                if m.fest or m.gehoert_zu or m.ist_deckenobjekt:
                    continue
                k += sichtbar_gewicht * (0.5 if m.ist_wandobjekt else 1.0) * max(0.0, 0.7 - sichtbar(m.rechteck))
        return k

    # ---- platzieren; wenn es nicht passt, das unwichtigste Stück weglassen und noch einmal
    weggelassen: list[str] = []
    lay, erg = None, None
    for runde in range(max_runden):
        moebel = [m.kopie() for m in bestand]
        for w in wuensche:
            p = produkte[w.pid]
            if p.typ != "zubehoer":
                moebel.append(_moebel_aus(w, p))
        start = Layout(raum, moebel, basis.bewohner)
        kinder_platzieren(start)
        if ausgabe:
            print(f"  Stelle {sum(1 for m in moebel if not m.fest)} Stücke nach der Regelbasis … "
                  f"(Runde {runde + 1})")
        lay, erg = optimiere(start, iterationen=iterationen, neustarts=neustarts, gewichte=gewichte,
                             seed=None if seed is None else seed + runde, anzahl_ergebnisse=1, ausgabe=False,
                             zusatzkosten=zusatz)[0]
        if erg.machbar:
            break
        kandidaten = [w for w in wuensche if produkte[w.pid].typ != "zubehoer" and w.prio > 1]
        if not kandidaten:
            hinweise.append("Der Raum ist sehr klein: Nicht alle praktischen Regeln (z. B. 60 cm Laufweg) "
                            "lassen sich erfüllen. Bitte den Grundriss prüfen.")
            break
        raus = max(kandidaten, key=lambda w: (w.prio, wuensche.index(w)))
        weg = _abhaengige(wuensche, raus.name)
        weggelassen += [w.name for w in wuensche if w.name in weg]
        wuensche = [w for w in wuensche if w.name not in weg]
    if weggelassen:
        hinweise.append("Aus Platzgründen weggelassen: " + ", ".join(weggelassen) + ".")

    # ---- Aussehen (Farben) und Deko fürs Bild
    palette = {k: hex_zu_rgb(v[0]) for k, v in STILE[stil].items()}
    aussehen: dict[str, dict] = {}
    deko: list[dict] = []
    nach_name = {m.name: m for m in lay.moebel}
    for w in wuensche:
        p = produkte[w.pid]
        if p.typ == "zubehoer":
            if p.variante == "stuhl_am_tisch" and w.gehoert_zu in nach_name:
                aussehen.setdefault(w.gehoert_zu, {}).update(stuhl=p.farbe(stil), stuhl_name=w.name)
            elif p.variante == "vorhang":
                farbe = palette["textil"] if p.id == "vorhang-leicht" else tuple(int(c * 0.82) for c in palette["stoff"])
                deko += [{"art": "vorhang", "fenster": f, "farbe": farbe} for f in raum.fenster]
            elif p.id == "obstschale" and w.gehoert_zu in nach_name:
                aussehen.setdefault(w.gehoert_zu, {})["schale"] = True
            continue
        a = aussehen.setdefault(w.name, {})
        a.update(farbe=p.farbe(stil), variante=p.variante, textil=palette["textil"], metall=palette["metall"],
                 akzent=palette["stoff_akzent"], rahmen=palette["holz"] if p.typ != "bild" else (250, 249, 246))

    # ---- fünf Elemente: fehlt eines, kommt ein kleiner Akzent dazu (Buch: alle fünf sollen vertreten sein)
    def elemente_von(ws):
        el: dict[str, list[str]] = {e: [] for e in ELEMENTE}
        for w in ws:
            p = produkte[w.pid]
            if p.element in el and w.name not in el[p.element]:
                el[p.element].append(w.name)
        return el

    schlaf = raum.raumtyp in ("schlafzimmer", "gaestezimmer", "studio")
    akzent = {"wasser": "kissen-dunkelblau", "metall": "schale-metall", "feuer": "vase-terrakotta",
              "erde": "schale-keramik", "holz": "schale-holz" if schlaf else "pflanze-geldbaum"}
    for el, namen in elemente_von(wuensche).items():
        if not namen:
            pid = akzent[el]
            if produkte[pid].typ == "zubehoer":
                wuensche.append(Wunsch(pid, produkte[pid].name.split(" (")[0], 3))
            else:
                wuensche.append(Wunsch("schale-holz", produkte["schale-holz"].name, 3))
    # warme, gleiche Leuchtmittel für alle Lampen
    lampen = sum(1 for w in wuensche if produkte[w.pid].typ in ("tischleuchte", "stehleuchte", "pendelleuchte"))
    if lampen:
        wuensche.append(Wunsch("leuchtmittel-2700k", "Leuchtmittel", 2, menge=lampen))
    elemente = elemente_von(wuensche)

    # ---- Einkaufsliste: gleiche Produkte zusammenfassen, in sinnvoller Reihenfolge nummerieren
    reihenfolge: list[str] = []
    gruppen: dict[str, Position] = {}
    for w in sorted(wuensche, key=lambda w: (produkte[w.pid].typ == "zubehoer", w.prio)):
        p = produkte[w.pid]
        if w.pid not in gruppen:
            gruppen[w.pid] = Position(0, p, 0)
            reihenfolge.append(w.pid)
        pos = gruppen[w.pid]
        pos.menge += w.menge
        if p.typ != "zubehoer" or p.variante == "stuhl_am_tisch":
            pos.moebel.append(w.name)
    positionen = []
    for nr, pid in enumerate(reihenfolge, 1):
        pos = gruppen[pid]
        pos.nr = nr
        erste = nach_name.get(pos.moebel[0]) if pos.moebel else None
        if erste is not None:
            pos.ort = _ort(erste, lay) if len(pos.moebel) == 1 else ", ".join(pos.moebel)
        positionen.append(pos)

    if not lay.raum.tueren:
        hinweise.append("Im Foto wurde keine Tür gefunden. Ohne Tür fehlen die Regeln zur Kommandoposition – "
                        "am besten so fotografieren, dass die Tür im Bild ist, oder aus der Tür heraus.")
    return Einrichtung(lay, erg, positionen, aussehen, deko, elemente, hinweise, weggelassen,
                       {w.name for w in wuensche if produkte[w.pid].typ != "zubehoer"}, stil, budget)


# ====================================================================== 3. Foto → Ergebnisdateien
def richte_foto_ein(rgb, v, raumtyp: str = "schlafzimmer", stil: str = "natur", budget: str = "mittel",
                    bewohner: Optional[Bewohner] = None, gewichte: Optional[dict] = None,
                    ausgabe_ordner: str = "ausgabe", stamm: str = "zimmer", zeigen: bool = False,
                    shops: Optional[dict] = None, realistisch: bool = False, **optionen) -> dict:
    """Kern der Funktion: Foto (als Array) + Vermessung → eingerichtetes Foto, Grundriss, Einkaufsliste.

    Getrennt von `zimmer_einrichten`, damit es sich ohne KI-Modelle testen lässt (siehe demo_zimmer.py).
    """
    import numpy as np
    from PIL import Image
    from .render3d import beschrifte, moebel_sichtbar, zeichne_ins_foto

    os.makedirs(ausgabe_ordner, exist_ok=True)
    shops = shops or lade_shops()
    basis = v.fuer_optimierer()
    basis.raum.raumtyp = raumtyp
    if bewohner is not None:
        basis.bewohner = bewohner
    e = einrichten(basis, stil, budget, gewichte, sichtbar=v.sichtbar, **optionen)

    r = zeichne_ins_foto(rgb, v, e.layout, e.aussehen, e.deko, nur=e.neu)
    pr, sz = r["projektion"], r["szene"]
    mit_nummern = beschrifte(r["bild"], pr, sz, e.nummern, r["tiefe"])

    # was ist im Foto zu sehen?
    nach_name = {m.name: m for m in e.layout.moebel}
    ausserhalb = []
    for pos in e.positionen:
        echte = [nach_name[n] for n in pos.moebel if n in nach_name]
        if not echte:
            continue
        zu_sehen = [m.name for m in echte if moebel_sichtbar(pr, r["tiefe"], sz, m)]
        pos.im_foto = bool(zu_sehen)
        ausserhalb += [m.name for m in echte if m.name not in zu_sehen]
    if ausserhalb:
        e.hinweise.append("Nicht im Foto sichtbar (neben/hinter der Kamera oder verdeckt – siehe Grundriss): "
                          + ", ".join(ausserhalb) + ".")
    e.hinweise.append("Maße aus einem Foto sind auf etwa ±10–20 cm genau. Vor dem Kauf nachmessen.")
    e.hinweise += [h for h in v.hinweise if "Kamerahöhe gemessen" not in h]

    d = {k: os.path.join(ausgabe_ordner, f"{stamm}_{k}") for k in
         ("eingerichtet.jpg", "eingerichtet_nummern.jpg", "vorher.jpg", "grundriss.png", "einkaufsliste.html",
          "einkaufsliste.txt", "einkaufsliste.json", "uebersicht.png")}
    Image.fromarray(r["bild"]).save(d["eingerichtet.jpg"], quality=92)
    Image.fromarray(mit_nummern).save(d["eingerichtet_nummern.jpg"], quality=92)
    Image.fromarray(r["foto"]).save(d["vorher.jpg"], quality=92)
    zeichne_grundriss(e, d["grundriss.png"], v)

    raum = e.layout.raum
    titel = f"Dein {raum.raumtyp.capitalize()} – eingerichtet nach Feng Shui"
    unter = (f"Raum ca. {raum.breite:.1f} × {raum.tiefe:.1f} m · Stil „{stil}“ · Budget „{budget}“ · "
             f"Feng-Shui-Score {e.ergebnis.score:.0f}/100")
    kacheln = [("Feng-Shui-Score", f"{e.ergebnis.score:.0f}/100"), ("Produkte", str(len(e.positionen))),
               ("Richtpreis gesamt", f"CHF {e.summe():,.0f}".replace(",", "’")),
               ("Raumfläche", f"{raum.breite * raum.tiefe:.0f} m²")]
    seite = einkaufsliste_html(
        e.positionen, shops, stil, budget, titel, unter,
        bilder=[(os.path.basename(d["vorher.jpg"]), "Vorher: das leere Zimmer"),
                (os.path.basename(d["eingerichtet_nummern.jpg"]), "Nachher: Nummern = Einkaufsliste"),
                (os.path.basename(d["grundriss.png"]), "Grundriss mit denselben Nummern")],
        kacheln=kacheln, elemente={el: e.elemente.get(el, []) for el in ELEMENTE}, hinweise=e.hinweise)
    with open(d["einkaufsliste.html"], "w", encoding="utf-8") as f:
        f.write(seite)
    with open(d["einkaufsliste.txt"], "w", encoding="utf-8") as f:
        f.write(e.text(shops))
    with open(d["einkaufsliste.json"], "w", encoding="utf-8") as f:
        json.dump({"raumtyp": raum.raumtyp, "raum_m": [raum.breite, raum.tiefe], "score": round(e.ergebnis.score, 1),
                   "stil": stil, "budget": budget, "summe_chf": e.summe(),
                   "positionen": einkaufsliste_daten(e.positionen, shops, stil, budget)},
                  f, ensure_ascii=False, indent=1)
    uebersicht(r["foto"], mit_nummern, e, d["uebersicht.png"], v, zeigen=zeigen)

    if realistisch:                       # optional + experimentell: generative KI (siehe realistisch.py)
        try:
            from .realistisch import verschoenere
            H, W = r["bild"].shape[:2]
            yy = np.clip((np.arange(H) * v.tiefe.shape[0] / H).astype(int), 0, v.tiefe.shape[0] - 1)
            xx = np.clip((np.arange(W) * v.tiefe.shape[1] / W).astype(int), 0, v.tiefe.shape[1] - 1)
            ki = verschoenere(r["bild"], r["foto"], r["maske"], r["tiefe"], v.tiefe[yy][:, xx], raum.raumtyp, stil)
            d["eingerichtet_ki.jpg"] = os.path.join(ausgabe_ordner, f"{stamm}_eingerichtet_ki.jpg")
            Image.fromarray(ki).save(d["eingerichtet_ki.jpg"], quality=92)
        except Exception as fehler:       # das KI-Bild ist ein Extra – der Rest ist schon gespeichert
            print(f"  (KI-Bild nicht erzeugt: {fehler.__class__.__name__}: {fehler})")
    return {"einrichtung": e, "bild": r["bild"], "bild_nummern": mit_nummern, "foto": r["foto"],
            "tiefe": r["tiefe"], "maske": r["maske"], "vermessung": v, "dateien": d,
            "raumtyp": raum.raumtyp}


def zimmer_einrichten(pfad: str, raumtyp: str = "schlafzimmer", stil: str = "natur", budget: str = "mittel",
                      ausgabe_ordner: str = "ausgabe", bewohner: Optional[Bewohner] = None,
                      gewichte: Optional[dict] = None, kamera_in_ecke: bool = True, foto_von_tuer: bool = True,
                      bekannte_breite: Optional[float] = None, zeigen: bool = False, vermessung=None,
                      **optionen) -> dict:
    """Foto eines leeren Zimmers rein → eingerichtetes Foto + Grundriss + Einkaufsliste raus.

    foto_von_tuer=True: Wird im Foto keine Tür gefunden, nimmt das Programm an, dass du in der Tür standest.
    vermessung: schon vorhandenes Ergebnis von foto3d.zimmer_aus_foto (spart die Rechenzeit ein zweites Mal).
    """
    from .foto3d import kamera_aus_foto, zimmer_aus_foto

    v = vermessung
    if v is None:
        v, _, _ = zimmer_aus_foto(pfad, raumtyp, kamera_in_ecke=kamera_in_ecke, bekannte_breite=bekannte_breite)
    if foto_von_tuer:
        tuer_hinter_kamera(v)
    _, rgb = kamera_aus_foto(pfad)
    stamm = os.path.splitext(os.path.basename(pfad))[0]
    return richte_foto_ein(rgb, v, raumtyp, stil, budget, bewohner, gewichte, ausgabe_ordner, stamm,
                           zeigen=zeigen, **optionen)


def tuer_hinter_kamera(v) -> bool:
    """Keine Tür im Foto? Dann stand die Person vermutlich in der Tür: Tür in die Wand hinter der Kamera setzen."""
    from .modell import WAND_NORMALE, Oeffnung
    raum = v.layout.raum
    if raum.tueren:
        return False
    rueck = (-v.kamera_blick[0], -v.kamera_blick[1])
    wand = max(WAND_NORMALE, key=lambda w: -(WAND_NORMALE[w][0] * rueck[0] + WAND_NORMALE[w][1] * rueck[1]))
    pos = v.kamera_pos[0] if wand in ("unten", "oben") else v.kamera_pos[1]
    L = raum.wandlaenge(wand)
    von = min(max(pos - 0.45, 0.05), max(0.05, L - 0.95))
    raum.oeffnungen.append(Oeffnung("tuer", wand, round(von, 2), 0.9))
    v.hinweise.append(f"Keine Tür im Foto gefunden – angenommen: Du standest in der Tür (Wand „{wand}“).")
    return True


# ====================================================================== Grafiken
def zeichne_grundriss(e: Einrichtung, datei: Optional[str] = None, v=None, ax=None):
    """Grundriss mit den Nummern der Einkaufsliste (und dem Kamerastandort, falls ein Foto vorliegt)."""
    import matplotlib
    import matplotlib.pyplot as plt
    from .visualisierung import zeichne

    raum = e.layout.raum
    eigene = ax is None
    if eigene:
        fig, ax = plt.subplots(figsize=(6.5, 6.5 * raum.tiefe / max(raum.breite, 0.1) + 0.7))
    zeichne(e.layout, f"Grundriss – Score {e.ergebnis.score:.0f}/100", ax=ax, chi=True)
    for name, nr in e.nummern.items():
        m = e.layout.nach_name(name)
        if m is None:
            continue
        ax.text(m.x, m.y + 0.13, str(nr), color="white", fontsize=7, fontweight="bold", ha="center", va="center",
                zorder=12, bbox=dict(boxstyle="circle,pad=0.22", fc="#7a5c3a", ec="white", lw=0.8))
    if v is not None:
        kx, ky = v.kamera_pos
        ax.plot(kx, ky, marker="^", ms=10, color="#e63946", zorder=9)
        ax.annotate("", xy=(kx + v.kamera_blick[0] * 0.5, ky + v.kamera_blick[1] * 0.5), xytext=(kx, ky),
                    arrowprops=dict(arrowstyle="->", color="#e63946", lw=1.6), zorder=9)
        ax.text(kx, ky - 0.17, "Kamera", color="#e63946", fontsize=7, ha="center")
    if eigene:
        fig.tight_layout()
        if datei:
            fig.savefig(datei, dpi=140)
        plt.close(fig)
    return ax


def uebersicht(foto, bild, e: Einrichtung, datei: Optional[str] = None, v=None, zeigen: bool = False):
    """Ein Blatt: leer | eingerichtet | Grundriss, darunter die Einkaufsliste in Kurzform."""
    import textwrap
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[4.6, 2.7], width_ratios=[1, 1, 0.8])
    for i, (b, t) in enumerate([(foto, "Vorher: leeres Zimmer"),
                                (bild, f"Nachher: eingerichtet – Feng-Shui-Score {e.ergebnis.score:.0f}/100")]):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(b)
        ax.set_title(t, fontsize=13, fontweight="bold")
        ax.axis("off")
    zeichne_grundriss(e, v=v, ax=fig.add_subplot(gs[0, 2]))

    zeilen = [f"EINKAUFSLISTE  (Stil „{e.stil}“, Budget „{e.budget}“, Richtpreis gesamt ca. CHF {e.summe():.0f})", ""]
    for p in e.positionen:
        regel = f"  [{', '.join(p.produkt.buch[:2])}]" if p.produkt.buch else ""
        zeilen.append(f"{p.nr:>2}. {p.menge}× {p.produkt.name} – ca. CHF {p.preis(e.budget):.0f}{regel}")
    halb = (len(zeilen) + 1) // 2 + 1
    for spalte, teil in enumerate((zeilen[:halb], zeilen[halb:])):
        ax = fig.add_subplot(gs[1, spalte])
        ax.axis("off")
        text = []
        for z in teil:
            text += textwrap.wrap(z, 78, subsequent_indent="      ") or [""]
        ax.text(0.0, 1.0, "\n".join(text[:17]), va="top", fontsize=9.6, family="DejaVu Sans", linespacing=1.4)
    ax = fig.add_subplot(gs[1, 2])
    ax.axis("off")
    text = ["DIE FÜNF ELEMENTE", ""]
    for el in ELEMENTE:
        text += textwrap.wrap(f"{ELEMENT_NAME[el]}: {', '.join(e.elemente.get(el, [])) or '–'}", 54,
                              subsequent_indent="    ")
    text += ["", "Links zu den Shops: siehe …_einkaufsliste.html"]
    ax.text(0.0, 1.0, "\n".join(text), va="top", fontsize=9.6, family="DejaVu Sans", linespacing=1.4)
    fig.tight_layout()
    if datei:
        fig.savefig(datei, dpi=110)
    if zeigen:
        plt.show()
    else:
        plt.close(fig)
