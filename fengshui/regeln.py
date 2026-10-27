"""
REGELBASIS – prüfbare Platzierungsregeln aus dem Buch.

Jede Regel bekommt ein Layout und liefert eine Liste von Befunden.
Ein Befund hat eine Strafe zwischen 0 (perfekt) und 1 (voll verletzt).

    Score einer Regel  = min(1, Summe der Strafen)
    Gesamtscore        = 100 * (1 - Σ gewicht·strafe / Σ gewicht)

Kategorien:
    hart      – physikalisch/praktisch nötig (Überlappung, Tür muss aufgehen, Laufwege)
    kommando  – Kommandoposition (5 Tiere: Schildkröte hinten, Vogel vorne, Drache/Tiger seitlich)
    chi       – Chi-Fluss (Türen, Fenster, Korridore, Spiegel, Balken)
    zonen     – Funktionszonen (Schlafen/Arbeiten getrennt, Ruhe-Bereich ums Bett)
    stil      – Gestaltung (untere-Drittel-Regel, Pflanzen, Bilder, Regale)

Die `gewicht`-Werte sind Startwerte. Das ML-Modul (ml.py) kann sie aus deinen
eigenen Bewertungen nachlernen – ganz im Sinne des Buchs:
"Lass dein Gefühl der ultimative Maßstab sein."
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Optional

from . import geometrie as g
from .modell import (FLACH, KOMMANDO_MOEBEL, ROT_VEKTOR, VEKTOR_WAND, WAND_NORMALE, Layout, Moebel)


@dataclass
class Befund:
    strafe: float
    text: str
    moebel: str = ""


@dataclass
class Regel:
    id: str
    titel: str
    beschreibung: str
    quelle: str
    kategorie: str
    gewicht: float
    pruefe: Callable[[Layout], list[Befund]]
    raumtypen: Optional[set[str]] = None   # None = gilt für alle Räume

    def gilt_fuer(self, raumtyp: str) -> bool:
        return self.raumtypen is None or raumtyp in self.raumtypen


REGELN: list[Regel] = []


def regel(id, titel, beschreibung, quelle, kategorie, gewicht, raumtypen=None):
    def deko(fn):
        REGELN.append(Regel(id, titel, beschreibung, quelle, kategorie, gewicht, fn,
                            set(raumtypen) if raumtypen else None))
        return fn
    return deko


# ============================================================ Hilfen
SCHLAFRAEUME = {"schlafzimmer", "kinderzimmer", "studio", "gaestezimmer"}


def _boden(layout: Layout) -> list[Moebel]:
    return [m for m in layout.moebel if not m.ist_wandobjekt and m.typ not in FLACH]


def _haupt(layout: Layout) -> list[Moebel]:
    return [m for m in layout.moebel if m.typ in KOMMANDO_MOEBEL]


def _kinder(layout: Layout, eltern: Moebel) -> list[Moebel]:
    return [m for m in layout.moebel if m.gehoert_zu == eltern.name]


def _hohe_hindernisse(layout: Layout, ausser: Moebel, min_hoehe: float = 1.2) -> list[g.Rect]:
    return [m.rechteck for m in _boden(layout) if m is not ausser and m.hoehe >= min_hoehe]


def _zone_frei(layout: Layout, zone: g.Rect, ausnahmen: list[Moebel]) -> float:
    """Anteil 0..1 der Zone, der blockiert oder außerhalb des Raums ist."""
    flaeche = (zone[2] - zone[0]) * (zone[3] - zone[1])
    if flaeche <= 0:
        return 0.0
    raum = layout.raum
    innen = g.ueberlappung(zone, (0, 0, raum.breite, raum.tiefe))
    blockiert = flaeche - innen
    for m in _boden(layout):
        if m in ausnahmen:
            continue
        blockiert += g.ueberlappung(zone, m.rechteck)
    return min(1.0, blockiert / flaeche)


def _zone_vorne(m: Moebel, tiefe: float) -> g.Rect:
    x1, y1, x2, y2 = m.rechteck
    vx, vy = m.vorne
    if vy > 0:
        return (x1, y2, x2, y2 + tiefe)
    if vy < 0:
        return (x1, y1 - tiefe, x2, y1)
    if vx > 0:
        return (x2, y1, x2 + tiefe, y2)
    return (x1 - tiefe, y1, x1, y2)


def _zone_hinten(m: Moebel, tiefe: float) -> g.Rect:
    x1, y1, x2, y2 = m.rechteck
    hx, hy = m.hinten
    if hy > 0:
        return (x1, y2, x2, y2 + tiefe)
    if hy < 0:
        return (x1, y1 - tiefe, x2, y1)
    if hx > 0:
        return (x2, y1, x2 + tiefe, y2)
    return (x1 - tiefe, y1, x1, y2)


def _bett_seitenzonen(b: Moebel, breite: float = 0.5) -> list[g.Rect]:
    """Zugangszonen links und rechts entlang der Längsseiten (ohne Kopfbereich mit Nachttischen)."""
    x1, y1, x2, y2 = b.rechteck
    vx, vy = b.vorne
    kopf = 0.55   # erste 55 cm am Kopfteil gehören den Nachttischen
    if vy != 0:   # Bett liegt in y-Richtung
        ya, yb = (y1 + kopf, y2) if vy > 0 else (y1, y2 - kopf)
        return [(x1 - breite, ya, x1, yb), (x2, ya, x2 + breite, yb)]
    xa, xb = (x1 + kopf, x2) if vx > 0 else (x1, x2 - kopf)
    return [(xa, y1 - breite, xb, y1), (xa, y2, xb, y2 + breite)]


def _tuer_winkel_strafe(winkel: float, seitlich_ok: bool) -> float:
    if winkel <= 95:
        return 0.0
    if winkel <= 135:
        return 0.25 if seitlich_ok else 0.5
    return 1.0


# ============================================================ HARTE REGELN
@regel("H01", "Keine Überlappung",
       "Möbel dürfen sich nicht überschneiden.", "praktisch", "hart", 10.0)
def _h01(layout):
    bef = []
    boden = _boden(layout)
    for i, a in enumerate(boden):
        for b in boden[i + 1:]:
            if "stuhl" in (a.typ, b.typ) and (a.gehoert_zu == b.name or b.gehoert_zu == a.name):
                continue        # Stühle dürfen ein Stück unter ihren Tisch geschoben sein
            f = g.ueberlappung(a.rechteck, b.rechteck)
            if f > 0:
                bef.append(Befund(min(1.0, f / 0.05), f"{a.name} überlappt {b.name} ({f:.2f} m²)", a.name))
    return bef


@regel("H02", "Alles im Raum", "Möbel müssen vollständig im Raum stehen.", "praktisch", "hart", 10.0)
def _h02(layout):
    return [Befund(1.0, f"{m.name} ragt aus dem Raum", m.name)
            for m in layout.moebel if not g.im_raum(m, layout.raum)]


@regel("H03", "Türen gehen frei auf",
       "Türen sollen nach innen öffnen und dürfen nicht verstellt sein – blockierte Türen stehen für einen "
       "blockierten Zugang zur Welt.", "Kap. 4 Eingang / Kap. 5 Unordnung", "hart", 8.0)
def _h03(layout):
    bef = []
    for t in layout.raum.tueren:
        zone = g.tuer_schwenkbereich(t, layout.raum)
        for m in _boden(layout):
            f = g.ueberlappung(zone, m.rechteck)
            if f > 0.01:
                bef.append(Befund(1.0, f"{m.name} steht im Aufschlag der {t.typ} ({t.wand})", m.name))
    return bef


@regel("H04", "Laufwege frei (≥ 60 cm)",
       "Freier Weg von der Tür zum Bett (beide Seiten bei Paaren), zum Schreibtischstuhl, zum Sofa, zu Schränken. "
       "Kein Durchquetschen.", "Kap. 4 Büro/Schlafzimmer, Kap. 5", "hart", 6.0)
def _h04(layout):
    ziele, namen = [], []
    for m in _boden(layout):
        if m.typ == "bett":
            zonen = _bett_seitenzonen(m, 0.3)
            pkt = [((z[0] + z[2]) / 2, (z[1] + z[3]) / 2) for z in zonen]
            if layout.bewohner.paar:
                for p in pkt:
                    ziele.append(p); namen.append(m.name)
            else:
                ziele.append(pkt); namen.append(m.name)   # eine Seite reicht
        elif m.typ == "schreibtisch":
            ziele.append(g.personenpunkt(m)); namen.append(m.name)
        elif m.typ in ("sofa", "sessel"):
            # Sitzmöbel: von vorne ODER seitlich (vor dem Sofa steht oft der Couchtisch)
            z = _zone_vorne(m, 0.35)
            fx, fy = m.vorne
            rx, ry = fy, -fx
            halb = m.breite / 2 + 0.35
            pkt = [((z[0] + z[2]) / 2, (z[1] + z[3]) / 2),
                   (m.x + rx * halb + fx * 0.2, m.y + ry * halb + fy * 0.2),
                   (m.x - rx * halb + fx * 0.2, m.y - ry * halb + fy * 0.2)]
            ziele.append(pkt); namen.append(m.name)
        elif m.typ in ("schrank", "kommode", "regal", "herd", "spuele", "kuehlschrank", "wc", "waschbecken",
                       "badewanne", "dusche"):
            z = _zone_vorne(m, 0.35)
            ziele.append(((z[0] + z[2]) / 2, (z[1] + z[3]) / 2)); namen.append(m.name)
    if not ziele:
        return []
    flach, idx = [], []
    for k, z in enumerate(ziele):
        if isinstance(z, list):
            for p in z:
                flach.append(p); idx.append(k)
        else:
            flach.append(z); idx.append(k)
    ok = g.erreichbarkeit(layout, flach)
    erreicht = [False] * len(ziele)
    for k, o in zip(idx, ok):
        erreicht[k] = erreicht[k] or o
    return [Befund(1.0, f"{n} ist von der Tür aus nicht bequem erreichbar", n)
            for n, e in zip(namen, erreicht) if not e]


@regel("H05", "Platz für den Schreibtischstuhl",
       "Hinter dem Schreibtisch braucht es ca. 70 cm freie Fläche für Stuhl und Person.", "praktisch", "hart", 6.0)
def _h05(layout):
    bef = []
    for d in layout.finde("schreibtisch"):
        zone = _zone_hinten(d, 0.7)
        s = _zone_frei(layout, zone, [d])
        if s > 0.05:
            bef.append(Befund(s, f"Stuhlbereich hinter {d.name} ist zu {s:.0%} blockiert", d.name))
    return bef


@regel("H06", "Schränke zugänglich",
       "Vor Schrank-/Kommodenfronten 60 cm frei lassen.", "praktisch", "hart", 4.0)
def _h06(layout):
    bef = []
    for m in _boden(layout):
        if m.typ in ("schrank", "kommode", "regal", "herd", "spuele", "kuehlschrank", "waschbecken", "wc"):
            s = _zone_frei(layout, _zone_vorne(m, 0.6), [m])
            if s > 0.1:
                bef.append(Befund(s, f"Vor {m.name} ist zu wenig Platz", m.name))
    return bef


@regel("H07", "Wandobjekte nicht auf Türen/Fenstern",
       "Spiegel, Bilder, Wandregale brauchen eine echte Wandfläche.", "praktisch", "hart", 6.0)
def _h07(layout):
    bef = []
    for w in layout.moebel:
        if not w.ist_wandobjekt:
            continue
        wand = VEKTOR_WAND[(-w.vorne[0], -w.vorne[1])]
        a, c = g.spanne_quer(w, (-w.vorne[0], -w.vorne[1]))
        if g.oeffnungen_an_wand(layout.raum, wand, a, c):
            bef.append(Befund(1.0, f"{w.name} hängt über einer Tür/einem Fenster", w.name))
    return bef


# ============================================================ KOMMANDOPOSITION
@regel("K01", "Schildkröte: feste Wand im Rücken",
       "Bett mit Kopfteil an eine massive Wand, Sofa mit Rücken zur Wand (sonst niedrige Konsole dahinter), "
       "am Schreibtisch eine Wand hinter dir. Nicht frei im Raum schweben lassen.",
       "Kap. 2 Fünf Tiere, Kap. 3 Kommandoposition, Kap. 4", "kommando", 3.0)
def _k01(layout):
    bef = []
    for m in _haupt(layout):
        d = g.rueckenabstand(m, layout.raum)
        if m.typ == "bett":
            s = min(1.0, max(0.0, d - 0.05) / 0.4)
            if s > 0:
                bef.append(Befund(s, f"Kopfteil von {m.name} steht {d:.2f} m vor der Wand", m.name))
        elif m.typ == "sofa":
            if d > 0.15:
                konsole = any(k.typ in ("konsole", "sideboard") for k in _kinder(layout, m))
                bef.append(Befund(0.35 if konsole else 0.8,
                                  f"{m.name} hat keine Wand im Rücken" + (" (Konsole hilft)" if konsole else ""), m.name))
        elif m.typ == "schreibtisch":
            s = min(1.0, max(0.0, d - 0.9) / 1.2)
            if s > 0:
                bef.append(Befund(s, f"Hinter dir am {m.name} sind {d:.1f} m offener Raum", m.name))
    return bef


@regel("K02", "Kein Fenster im Rücken",
       "Nicht mit dem Rücken/Kopfteil an ein Fenster – besonders nicht an eines, das tiefer als die Hüfte reicht. "
       "Wenn unvermeidbar: Fensterbank höher als das Kopfteil, massives Kopfteil, schwere Vorhänge.",
       "Kap. 3 Kommandoposition, Kap. 4 Schlafzimmer/Büro", "kommando", 2.5)
def _k02(layout):
    bef = []
    for m in _haupt(layout):
        hinten = m.hinten
        if g.rueckenabstand(m, layout.raum) > 1.2:
            continue
        wand = VEKTOR_WAND[hinten]
        a, b = g.spanne_quer(m, hinten)
        for f in g.oeffnungen_an_wand(layout.raum, wand, a, b, nur=("fenster", "balkontuer")):
            kopfteil = 1.0 if m.typ == "bett" else 0.9
            if f.typ == "balkontuer" or f.bruestung < 0.9:
                s = 1.0
            elif f.bruestung < kopfteil + 0.1:
                s = 0.6
            else:
                s = 0.3
            bef.append(Befund(s, f"{m.name} hat ein Fenster ({f.wand}, Brüstung {f.bruestung:.2f} m) im Rücken", m.name))
    return bef


@regel("K03", "Tür im Blick",
       "Von Bett, Sofa und Schreibtisch aus soll man die Zimmertür sehen, ohne sich umzudrehen. "
       "Am Schreibtisch ist seitlich zur Tür noch ok – aber nie mit dem Rücken zur Tür.",
       "Kap. 3 Café-Technik, Kap. 4 Sofa/Büro/Schlafzimmer", "kommando", 3.0)
def _k03(layout):
    bef = []
    t = layout.raum.haupttuer
    if t is None:
        return bef
    tm = g.punkt_vor_oeffnung(t, layout.raum, 0.05)
    for m in _haupt(layout):
        p = g.personenpunkt(m)
        w = g.winkel_zu(p, m.vorne, tm)
        s = _tuer_winkel_strafe(w, seitlich_ok=(m.typ == "schreibtisch"))
        if s > 0:
            bef.append(Befund(s, f"Von {m.name} aus liegt die Tür {w:.0f}° neben der Blickrichtung", m.name))
        elif not g.sichtlinie_frei(p, tm, _hohe_hindernisse(layout, m)):
            bef.append(Befund(0.5, f"Sicht von {m.name} zur Tür ist durch hohe Möbel verdeckt", m.name))
    return bef


@regel("K04", "Füße nicht zur Tür (Sargposition)",
       "Das Bett nie so stellen, dass die Füße direkt in Linie zur Tür zeigen. Notlösung: Paravent oder "
       "schweres Möbel am Fußende.", "Kap. 4 Schlafzimmer – Bett und Chi", "kommando", 3.0,
       raumtypen=SCHLAFRAEUME)
def _k04(layout):
    bef = []
    for b in layout.finde("bett"):
        for t in layout.raum.tueren:
            if g.schaut_zur_oeffnung(b, t):
                schutz = _zone_frei(layout, _zone_vorne(b, 0.6), [b]) > 0.3
                bef.append(Befund(0.5 if schutz else 1.0,
                                  f"Fußende von {b.name} zeigt direkt auf die {t.typ}" +
                                  (" (Möbel am Fußende mildert)" if schutz else ""), b.name))
        for o in layout.raum.oeffnungen:
            if o.typ == "schranktuer" and g.schaut_zur_oeffnung(b, o):
                bef.append(Befund(0.3, f"Fußende von {b.name} zeigt auf eine Schranktür – diskret halten, geschlossen", b.name))
    return bef


@regel("K05", "Füße nicht zum großen Fenster",
       "Füße Richtung Fenster erzeugt viel Bewegungs-Chi; bei kleinen Fenstern/ruhigem Ausblick ok.",
       "Kap. 4 Schlafzimmer", "chi", 1.0, raumtypen=SCHLAFRAEUME)
def _k05(layout):
    bef = []
    for b in layout.finde("bett"):
        for f in layout.raum.fenster:
            if f.typ != "balkontuer" and g.schaut_zur_oeffnung(b, f):
                s = 0.6 if f.breite >= 1.4 or f.bruestung < 0.5 else 0.3
                bef.append(Befund(s, f"Fußende von {b.name} zeigt auf ein Fenster ({f.breite:.1f} m breit)", b.name))
    return bef


@regel("K06", "Abstand zur Tür",
       "Bett so weit wie möglich von der Tür entfernt; am Schreibtisch nicht zu nah an der Tür sitzen "
       "(durch die Tür kommt das Chi herein).", "Kap. 4 Schlafzimmer/Büro", "chi", 2.0)
def _k06(layout):
    bef = []
    t = layout.raum.haupttuer
    if t is None:
        return bef
    tm = t.mitte(layout.raum)
    diag = math.hypot(layout.raum.breite, layout.raum.tiefe)
    for m in _haupt(layout):
        if m.typ == "bett":
            d = g.abstand_punkt_rechteck(tm, m.rechteck)
            s = max(0.0, 1 - d / (0.45 * diag))
        else:
            d = math.dist(tm, g.personenpunkt(m))
            s = max(0.0, (1.3 - d) / 1.3)
        if s > 0.05:
            bef.append(Befund(s, f"{m.name} ist nur {d:.1f} m von der Tür entfernt", m.name))
    return bef


@regel("K07", "Bett nicht an der Türwand",
       "Steht das Bett an derselben Wand wie die Tür, kann man die Tür nicht überblicken.",
       "Kap. 4 Schlafzimmer – Kommandoposition", "kommando", 1.5, raumtypen=SCHLAFRAEUME)
def _k07(layout):
    t = layout.raum.haupttuer
    if t is None:
        return []
    return [Befund(1.0, f"Kopfteil von {b.name} steht an der Türwand ({t.wand})", b.name)
            for b in layout.finde("bett") if VEKTOR_WAND[b.hinten] == t.wand and g.rueckenabstand(b, layout.raum) < 0.5]


@regel("K08", "Keine Balken / Schweres über dir",
       "Nicht unter Deckenbalken, schweren Lampen, Ventilatoren schlafen oder sitzen – sie wirken wie Klingen. "
       "Kein Balken darf quer über das Bett laufen.", "Kap. 2 Chi (Sha), Kap. 3 Kronleuchter, Kap. 4",
       "chi", 2.5)
def _k08(layout):
    bef = []
    for m in _haupt(layout):
        for bk in layout.raum.balken:
            r = (min(bk.x1, bk.x2), min(bk.y1, bk.y2), max(bk.x1, bk.x2), max(bk.y1, bk.y2))
            if m.typ == "bett" and g.ueberlappung(r, m.rechteck) > 0:
                bef.append(Befund(1.0, f"Ein Balken läuft über {m.name}", m.name))
            elif m.typ != "bett" and g.abstand_punkt_rechteck(g.personenpunkt(m), r) < 0.3:
                bef.append(Befund(0.8, f"Du sitzt an {m.name} unter einem Balken", m.name))
    return bef


@regel("K09", "Dachschräge: Kopf auf der hohen Seite",
       "Bett an das höhere Ende der Schräge, ausgeglichen (nicht eine Seite tiefer). "
       "Sofa nicht unter das niedrige Ende.", "Kap. 4 Schlafzimmer/Wohnzimmer", "chi", 2.0)
def _k09(layout):
    bef = []
    raum = layout.raum
    if raum.schraege is None:
        return bef
    for m in _haupt(layout):
        p = g.personenpunkt(m)
        h = raum.deckenhoehe(*p)
        if h < 2.0:
            bef.append(Befund(min(1.0, (2.0 - h) / 0.8), f"Über dem Kopf an {m.name} nur {h:.2f} m Deckenhöhe", m.name))
        if m.typ == "bett":
            # Höhe an den beiden Ecken des Kopfteils vergleichen: unterschiedlich = eine Seite liegt tiefer
            x1, y1, x2, y2 = m.rechteck
            hx, hy = m.hinten
            if hy != 0:
                yk = y2 if hy > 0 else y1
                kopf_ecken = [(x1, yk), (x2, yk)]
            else:
                xk = x2 if hx > 0 else x1
                kopf_ecken = [(xk, y1), (xk, y2)]
            hs = [raum.deckenhoehe(x, y) for x, y in kopf_ecken]
            if abs(hs[0] - hs[1]) > 0.3:
                bef.append(Befund(0.4, f"{m.name} steht schief unter der Schräge (eine Seite tiefer)", m.name))
    return bef


@regel("K10", "Bett von beiden Seiten zugänglich",
       "Bei Paaren immer von beiden Seiten einsteigen können. Für Singles bedeutet es Offenheit für einen Partner; "
       "Bett mit Längsseite an der Wand ist nicht falsch, aber eher für 'glückliche Singles'.",
       "Kap. 4 Schlafzimmer", "kommando", 1.5, raumtypen={"schlafzimmer", "studio", "gaestezimmer"})
def _k10(layout):
    bef = []
    bw = layout.bewohner
    for b in layout.finde("bett"):
        zonen = _bett_seitenzonen(b, 0.45)
        blockiert = [_zone_frei(layout, z, [b] + _kinder(layout, b)) for z in zonen]
        schlimm = max(blockiert)
        if schlimm > 0.3:
            if bw.paar:
                s = 1.0
            elif bw.sucht_partner:
                s = 0.8
            else:
                s = 0.15
            bef.append(Befund(s, f"Eine Längsseite von {b.name} ist nicht frei zugänglich", b.name))
    return bef


@regel("K11", "Kinderbett mit Längsseite an der Wand",
       "Im Kinderzimmer gibt eine Längsseite an der Wand dem Kind mehr Geborgenheit.",
       "Kap. 4 Kinderzimmer", "kommando", 1.0, raumtypen={"kinderzimmer"})
def _k11(layout):
    bef = []
    for b in layout.finde("bett"):
        zonen = _bett_seitenzonen(b, 0.12)
        if max(_zone_frei(layout, z, [b] + _kinder(layout, b)) for z in zonen) < 0.5:
            bef.append(Befund(0.6, f"{b.name} hat keine Längsseite an der Wand", b.name))
    return bef


@regel("K12", "Vogel: Freiraum vor dir",
       "Vor Bett und Sofa braucht es offenen Raum (nicht beengt). Am Schreibtisch nicht direkt gegen die Wand "
       "starren – außer bei vielen Bildschirmen (dann zur Wand, aber Tür sehen).",
       "Kap. 2 Fünf Tiere (Vogel), Kap. 4", "kommando", 1.5)
def _k12(layout):
    bef = []
    for m in _haupt(layout):
        if m.typ == "bett":
            s = _zone_frei(layout, _zone_vorne(m, 0.6), [m] + [k for k in layout.moebel if k.typ == "bank"])
            if s > 0.3:
                bef.append(Befund(s, f"Vor dem Fußende von {m.name} ist es eng", m.name))
        elif m.typ == "sofa":
            s = _zone_frei(layout, _zone_vorne(m, 0.9), [m] + _kinder(layout, m))
            if s > 0.3:
                bef.append(Befund(s, f"Vor {m.name} ist zu wenig Raum", m.name))
        elif m.typ == "schreibtisch":
            d = g.abstand_zur_wand(m, layout.raum, m.vorne)
            if d < 0.3 and not layout.bewohner.viele_bildschirme:
                bef.append(Befund(0.4, f"Am {m.name} schaust du direkt gegen die Wand (Tipp: tiefer Tisch, Bilder, Pinnwand)", m.name))
    return bef


@regel("K13", "Schreibtisch: Fenster seitlich",
       "Ideal ist das Fenster seitlich (gleichmäßiges Licht). Blick ins Fenster lenkt ab und blendet; "
       "Fenster im Rücken = Gefühl, beobachtet zu werden (siehe K02).", "Kap. 4 Büro – Schreibtisch", "kommando", 1.0,
       raumtypen={"buero", "schlafzimmer", "studio", "kinderzimmer", "wohnzimmer"})
def _k13(layout):
    bef = []
    for d in layout.finde("schreibtisch"):
        for f in layout.raum.fenster:
            if g.schaut_zur_oeffnung(d, f) and g.abstand_zur_wand(d, layout.raum, d.vorne) < 1.5:
                bef.append(Befund(0.6, f"Am {d.name} schaust du direkt ins Fenster (Blendung)", d.name))
        if layout.raum.fenster:
            p = g.personenpunkt(d)
            seitlich = any(60 <= g.winkel_zu(p, d.vorne, f.mitte(layout.raum)) <= 120 for f in layout.raum.fenster)
            if not seitlich:
                bef.append(Befund(0.2, f"Kein Fenster seitlich vom {d.name}", d.name))
    return bef


@regel("K14", "Keine spitzen Ecken auf dich gerichtet",
       "Ecken von Schränken, Tischen, Kommoden erzeugen 'tötendes' Sha-Chi. Keine Möbelecken nahe Bett/Kopf oder "
       "Sitzplatz; Ecken mit Möbeln füllen oder mit Pflanzen abmildern; runde/niedrige Nachttische.",
       "Kap. 2 Chi (Sha), Kap. 4", "chi", 1.5)
def _k14(layout):
    bef = []
    raum = layout.raum
    for m in _haupt(layout):
        ziel = m.rechteck if m.typ == "bett" else None
        pp = g.personenpunkt(m)
        for o in _boden(layout):
            if o is m or o.rund or o.gehoert_zu == m.name or o.typ in ("pflanze", "bank", "sessel", "stuhl",
                                                                        "stehleuchte"):
                continue
            if o.typ == "nachttisch" and o.hoehe <= 0.6:
                continue
            for (cx, cy) in g.ecken(o.rechteck):
                # Ecken, die an einer Wand liegen, zeigen nicht in den Raum
                if min(cx, cy, raum.breite - cx, raum.tiefe - cy) < 0.15:
                    continue
                d = g.abstand_punkt_rechteck((cx, cy), ziel) if ziel else math.dist((cx, cy), pp)
                grenze = 0.8 if ziel else 1.0
                if d < grenze:
                    bef.append(Befund(0.35 * (1 - d / grenze) + 0.15,
                                      f"Ecke von {o.name} zeigt auf {m.name} ({d:.2f} m)", m.name))
    return bef


@regel("K15", "Langer Raum: Möbel quer stellen",
       "In langen Räumen fließt das Chi zu schnell. Möbel (auch das Bett) quer zur Längsachse stellen; "
       "Bett nicht ungeschützt am Ende des Raums.", "Kap. 4 Wohnzimmer/Schlafzimmer – lange Räume", "chi", 1.0)
def _k15(layout):
    raum = layout.raum
    if raum.seitenverhaeltnis < 1.6:
        return []
    lang_achse_y = raum.tiefe > raum.breite
    bef = []
    for m in _haupt(layout):
        if m.typ != "bett":
            continue
        laengs = (m.vorne[1] != 0) == lang_achse_y
        if laengs:
            bef.append(Befund(0.7, f"{m.name} liegt längs im langen Raum (wie in einem Korridor)", m.name))
    return bef


@regel("K16", "Bett zentral & symmetrisch",
       "Das Bett symmetrisch platzieren, mittig an seiner Wand – ein zentral stehendes Bett verankert den Raum.",
       "Kap. 4 Schlafzimmer – Gefühl und Plan", "stil", 0.6, raumtypen={"schlafzimmer", "gaestezimmer"})
def _k16(layout):
    bef = []
    for b in layout.finde("bett"):
        wand = VEKTOR_WAND[b.hinten]
        L = layout.raum.wandlaenge(wand)
        a, c = g.spanne_quer(b, b.hinten)
        abw = abs((a + c) / 2 - L / 2) / (L / 2)
        if abw > 0.15:
            bef.append(Befund(min(1.0, abw), f"{b.name} steht nicht mittig an der Wand ({abw:.0%} versetzt)", b.name))
    return bef


# ============================================================ CHI-FLUSS
@regel("C01", "Nicht in der Chi-Bahn Tür ↔ Fenster",
       "Chi fließt von der Tür zum Fenster (gegenüberliegend = schnell durchschneidend). "
       "Bett, Sofa und Arbeitsplatz gehören in die ruhige Zone abseits dieser Bahn.",
       "Kap. 2 Chi-Fluss, Kap. 3 Grundriss-Übung", "chi", 2.0)
def _c01(layout):
    bef = []
    polys = g.chi_korridor(layout.raum, mit_faktor=True)
    for m in _haupt(layout):
        werte = [(g.anteil_im_polygon(m.rechteck, p), f) for p, f in polys]
        anteil, faktor = max(werte, key=lambda af: af[0] * af[1], default=(0.0, 1.0))
        if anteil * faktor > 0.1:
            art = "direkte" if faktor == 1.0 else "über Eck verlaufende"
            bef.append(Befund(min(1.0, anteil * faktor * 1.3),
                              f"{m.name} liegt zu {anteil:.0%} in der {art} Chi-Bahn Tür↔Fenster", m.name))
    return bef


@regel("C02", "Spiegel richtig platzieren",
       "Spiegel wirken wie Türen/Fenster. Im Schlafzimmer vermeiden; wenn doch, nicht vom Bett aus sichtbar und "
       "nie am Fußende. Nie direkt gegenüber der Eingangstür. Kein Spiegel hinter dem Arbeitsplatz.",
       "Kap. 5 Spiegel, Kap. 4", "chi", 2.0)
def _c02(layout):
    bef = []
    raum = layout.raum
    t = raum.haupttuer
    for sp in layout.finde("spiegel"):
        spn = sp.vorne
        sp_p = (sp.x, sp.y)
        if raum.raumtyp in SCHLAFRAEUME:
            bef.append(Befund(0.2, "Spiegel im Schlafzimmer (Ruhezone) – möglichst vermeiden", sp.name))
            for b in layout.finde("bett"):
                if g.abstand_rechtecke(sp.rechteck, b.rechteck) < 1.0:
                    bef.append(Befund(0.6, f"{sp.name} hängt direkt am {b.name} (Spiegel wirken wie Türen)", sp.name))
                kopf = g.personenpunkt(b)
                if g.winkel_zu(sp_p, spn, kopf) < 70 and g.winkel_zu(kopf, b.vorne, sp_p) < 100:
                    bef.append(Befund(1.0, f"{sp.name} ist vom {b.name} aus sichtbar (spiegelt dich im Bett)", sp.name))
        if t is not None:
            tm = t.mitte(raum)
            gegenueber = WAND_NORMALE[t.wand] == tuple(-v for v in spn)
            if gegenueber and g.winkel_zu(sp_p, spn, tm) < 25:
                bef.append(Befund(0.8, f"{sp.name} hängt der Tür direkt gegenüber (lenkt Chi hinaus)", sp.name))
        for d in layout.finde("schreibtisch"):
            pp = g.personenpunkt(d)
            if g.winkel_zu(pp, d.hinten, sp_p) < 40 and math.dist(pp, sp_p) < 2.5:
                bef.append(Befund(0.5, f"{sp.name} hängt hinter dir am {d.name}", sp.name))
    return bef


@regel("C03", "Pflanzen: Licht ja, Bett nein",
       "Pflanzen brauchen Licht (nahe Fenster, in Gruppen). Im Schlafzimmer möglichst keine – wenn doch, "
       "als Gruppe direkt am Fenster und das Bett so weit wie möglich davon entfernt.",
       "Kap. 5 Zimmerpflanzen", "stil", 1.0)
def _c03(layout):
    bef = []
    raum = layout.raum
    fenster_p = [f.mitte(raum) for f in raum.fenster]
    for p in layout.finde("pflanze"):
        d_f = min((g.abstand_punkt_rechteck(fp, p.rechteck) for fp in fenster_p), default=None)
        if d_f is not None and d_f > 1.0:
            bef.append(Befund(min(1.0, (d_f - 1.0) / 2), f"{p.name} steht {d_f:.1f} m vom Fenster (zu wenig Licht)", p.name))
        if raum.raumtyp in ("schlafzimmer", "gaestezimmer", "studio"):
            if not layout.bewohner.pflanzen_sind_freunde:
                bef.append(Befund(0.3, f"{p.name}: im Schlafzimmer eigentlich keine Pflanzen (Yang-Energie)", p.name))
            for b in layout.finde("bett"):
                d = g.abstand_rechtecke(p.rechteck, b.rechteck)
                if d < 1.5:
                    bef.append(Befund((1.5 - d) / 1.5, f"{p.name} steht nur {d:.1f} m vom {b.name}", p.name))
    return bef


@regel("C04", "Keine Bildschirme im Schlafzimmer",
       "Fernseher, Computer (und sogar Smartphones) gehören nicht ins Schlafzimmer. Glänzende schwarze Flächen "
       "wirken zudem wie Spiegel.", "Kap. 4 Schlafzimmer, Kap. 5 Spiegel", "zonen", 1.5,
       raumtypen={"schlafzimmer", "gaestezimmer"})
def _c04(layout):
    bef = [Befund(0.7, f"{m.name} im Schlafzimmer", m.name) for m in layout.finde("tv")]
    for t in layout.finde("tv"):
        for b in layout.finde("bett"):
            if g.winkel_zu(g.personenpunkt(b), b.vorne, (t.x, t.y)) < 45:
                bef.append(Befund(0.3, f"{t.name} steht direkt im Blickfeld des Betts (spiegelt wie ein Spiegel)", t.name))
    return bef


@regel("C05", "Zonen: Arbeiten vorn, Schlafen hinten",
       "Schlaf- und Arbeitsbereich klar trennen. Arbeitsbereich näher zur Tür und im helleren (Yang-)Teil, "
       "Schlafbereich im hinteren, ruhigen Teil. Um das Bett eine reine Ruhezone.",
       "Kap. 4 Gemeinsame Räume – Schlafzimmer und Arbeiten", "zonen", 1.5)
def _c05(layout):
    bef = []
    t = layout.raum.haupttuer
    betten, tische = layout.finde("bett"), layout.finde("schreibtisch")
    if not (betten and tische and t):
        return bef
    tm = t.mitte(layout.raum)
    for b in betten:
        for d in tische:
            db = g.abstand_punkt_rechteck(tm, b.rechteck)
            dd = math.dist(tm, g.personenpunkt(d))
            if db < dd and not layout.bewohner.arbeit_wichtiger_als_schlaf:
                bef.append(Befund(0.5, f"{b.name} ist näher an der Tür als der Arbeitsplatz", b.name))
            nah = g.abstand_rechtecke(b.rechteck, d.rechteck)
            if nah < 0.6:
                bef.append(Befund(0.6, f"{d.name} steht direkt am {b.name} – keine getrennten Zonen", d.name))
    return bef


@regel("C06", "Kein Wasser/Aquarium/Drache im Schlafzimmer",
       "Aquarien, Brunnen und Drachenmotive bringen viel Yang – nicht ins Schlafzimmer.",
       "Kap. 4 Schlafzimmer, Kap. 5 Wasser/Objekte", "zonen", 1.0, raumtypen={"schlafzimmer", "gaestezimmer"})
def _c06(layout):
    return [Befund(0.8, f"{m.name} im Schlafzimmer", m.name)
            for m in layout.moebel if m.typ in ("aquarium", "brunnen", "drache")]


@regel("C07", "Altbau: Bett nicht an die Außenwand",
       "In älteren Gebäuden Temperaturschwankungen der Außenwand meiden (Neubau egal).",
       "Kap. 4 Schlafzimmer – Außenwand", "chi", 0.6, raumtypen=SCHLAFRAEUME)
def _c07(layout):
    raum = layout.raum
    if not raum.altbau:
        return []
    return [Befund(0.7, f"{b.name} steht an der Außenwand ({VEKTOR_WAND[b.hinten]})", b.name)
            for b in layout.finde("bett")
            if VEKTOR_WAND[b.hinten] in raum.aussenwaende and g.rueckenabstand(b, raum) < 0.3]


# ============================================================ STIL / WANDOBJEKTE
@regel("S01", "Nichts Schweres über dem Kopfteil",
       "Nie Regale oder Wandmöbel über dem Bett; keine schweren (Glas-)Bilder über dem Bett – leichte Textilien "
       "oder Wandbilder sind ok. Keine überhängenden Regale über dem Schreibtisch.",
       "Kap. 4 Schlafzimmer – Kunst/Regale, Büro", "stil", 2.0)
def _s01(layout):
    bef = []
    for w in layout.moebel:
        if w.typ not in ("wandregal", "bild"):
            continue
        wand = VEKTOR_WAND[(-w.vorne[0], -w.vorne[1])]
        for b in layout.finde("bett"):
            if VEKTOR_WAND[b.hinten] == wand and g.rueckenabstand(b, layout.raum) < 0.3:
                a, c = g.spanne_quer(b, b.hinten)
                wa, wc = g.spanne_quer(w, (-w.vorne[0], -w.vorne[1]))
                if min(c, wc) - max(a, wa) > 0:
                    s = 1.0 if w.typ == "wandregal" else 0.5
                    bef.append(Befund(s, f"{w.name} hängt über dem Kopfteil von {b.name}", w.name))
        if w.typ == "wandregal":
            for d in layout.finde("schreibtisch"):
                if VEKTOR_WAND[d.vorne] == wand and g.abstand_zur_wand(d, layout.raum, d.vorne) < 0.3:
                    a, c = g.spanne_quer(d, d.vorne)
                    wa, wc = g.spanne_quer(w, (-w.vorne[0], -w.vorne[1]))
                    if min(c, wc) - max(a, wa) > 0:
                        bef.append(Befund(0.6, f"{w.name} hängt bedrohlich über dem {d.name}", w.name))
    return bef


@regel("S02", "Untere-Drittel-Regel",
       "Stauraum gehört ins untere Drittel der Wand; obere zwei Drittel frei für Deko. Keine hohen offenen "
       "Bücherregale (offene Regale = aggressives Chi). Einbauschränke über die ganze Wand sind ok.",
       "Kap. 5 Eindrücke / Ordnung, Kap. 4 Büro", "stil", 0.8)
def _s02(layout):
    grenze = max(1.2, layout.raum.hoehe * 0.5)
    return [Befund(min(1.0, (m.hoehe - grenze) / 1.0) * 0.8, f"{m.name} ist {m.hoehe:.1f} m hoch (offenes Regal)", m.name)
            for m in layout.moebel if m.typ == "regal" and m.hoehe > grenze]


@regel("S03", "Fenster & Ausblick nicht verstellen",
       "Licht und Ausblick erhalten; hohe Möbel nicht vor Fenster und Balkontür stellen (Balkon nie abschneiden).",
       "Kap. 4 Eingang, Kap. 5 Balkone", "chi", 1.5)
def _s03(layout):
    bef = []
    raum = layout.raum
    for f in raum.fenster:
        zone = g.tuer_schwenkbereich(f, raum)
        x1, y1, x2, y2 = zone
        nx, ny = WAND_NORMALE[f.wand]
        # nur 0.5 m tief prüfen
        if nx > 0: x2 = x1 + 0.5
        if nx < 0: x1 = x2 - 0.5
        if ny > 0: y2 = y1 + 0.5
        if ny < 0: y1 = y2 - 0.5
        for m in _boden(layout):
            if m.typ == "pflanze":
                continue
            if g.ueberlappung((x1, y1, x2, y2), m.rechteck) > 0.02 and m.hoehe > f.bruestung + 0.1:
                bef.append(Befund(1.0 if f.typ == "balkontuer" else 0.7,
                                  f"{m.name} ({m.hoehe:.1f} m hoch) verstellt das Fenster ({f.wand})", m.name))
    return bef


@regel("S04", "Esstisch frei in der Raummitte",
       "Esstisch mittig, nie an die Wand (rundum Platz), gute Sicht zum Eingang, aber nicht im Weg.",
       "Kap. 4 Esszimmer", "kommando", 2.0, raumtypen={"esszimmer", "studio", "wohnzimmer"})
def _s04(layout):
    bef = []
    raum = layout.raum
    for t in layout.finde("esstisch"):
        x1, y1, x2, y2 = t.rechteck
        rand = min(x1, y1, raum.breite - x2, raum.tiefe - y2)
        if rand < 0.75:
            bef.append(Befund(min(1.0, (0.75 - rand) / 0.75), f"{t.name} steht zu nah an der Wand ({rand:.2f} m)", t.name))
        if raum.raumtyp == "esszimmer":
            d = math.dist((t.x, t.y), (raum.breite / 2, raum.tiefe / 2))
            s = min(1.0, d / (0.5 * min(raum.breite, raum.tiefe)))
            if s > 0.2:
                bef.append(Befund(s * 0.6, f"{t.name} steht nicht in der Raummitte", t.name))
    return bef


@regel("S05", "Fernseher nicht als Mittelpunkt",
       "TV vom Zentrum in eine Ecke rücken, möglichst niedrig, nicht über einen Kamin; nicht von der Tür aus "
       "als Erstes sichtbar. Das Gespräch hat Vorrang.", "Kap. 4 Wohnzimmer – Fernseher", "stil", 1.0,
       raumtypen={"wohnzimmer", "studio"})
def _s05(layout):
    bef = []
    raum = layout.raum
    for tv in layout.finde("tv"):
        wand = VEKTOR_WAND[tv.hinten]
        L = raum.wandlaenge(wand)
        a, c = g.spanne_quer(tv, tv.hinten)
        if abs((a + c) / 2 - L / 2) < L / 6:
            bef.append(Befund(0.5, f"{tv.name} steht zentral an der Wand (Mittelpunkt des Raums)", tv.name))
        t = raum.haupttuer
        if t is not None:
            tm = g.punkt_vor_oeffnung(t, raum, 0.3)
            if g.winkel_zu(tm, WAND_NORMALE[t.wand], (tv.x, tv.y)) < 30:
                bef.append(Befund(0.4, f"{tv.name} ist das Erste, was man beim Eintreten sieht", tv.name))
    return bef


@regel("S06", "Sitzkreis statt einsamer Stuhl",
       "Sessel ergänzen das Sofa zu einem geschlossenen sozialen Kreis und schauen zum Sofa – nicht alle Sitze in "
       "dieselbe Richtung. Ein einzelner Stuhl außerhalb des Kreises signalisiert einen unwillkommenen Gast.",
       "Kap. 4 Wohnzimmer – Sessel", "stil", 1.2, raumtypen={"wohnzimmer", "studio"})
def _s06(layout):
    bef = []
    sofas = layout.finde("sofa")
    if not sofas:
        return bef
    for s in layout.finde("sessel"):
        sofa = min(sofas, key=lambda o: g.abstand_rechtecke(o.rechteck, s.rechteck))
        mitte = (sofa.x + sofa.vorne[0] * 1.2, sofa.y + sofa.vorne[1] * 1.2)   # ungefähr Couchtisch
        d = g.abstand_punkt_rechteck(mitte, s.rechteck)
        if d > 1.3:
            bef.append(Befund(min(1.0, (d - 1.3) / 1.5 + 0.3), f"{s.name} steht außerhalb des Sitzkreises ({d:.1f} m)", s.name))
        if g.winkel_zu((s.x, s.y), s.vorne, mitte) > 80:
            bef.append(Befund(0.5, f"{s.name} schaut nicht zur Sitzgruppe", s.name))
    return bef


@regel("S07", "Fernseher vom Sofa sichtbar, aber dezent",
       "Der TV soll vom Sofa aus nutzbar sein, aber nicht die Bühne beherrschen (siehe S05).",
       "Kap. 4 Wohnzimmer – Fernseher", "stil", 0.8, raumtypen={"wohnzimmer", "studio"})
def _s07(layout):
    bef = []
    for tv in layout.finde("tv"):
        for sofa in layout.finde("sofa"):
            if g.winkel_zu((sofa.x, sofa.y), sofa.vorne, (tv.x, tv.y)) > 70:
                bef.append(Befund(0.8, f"{tv.name} ist vom {sofa.name} aus kaum zu sehen", tv.name))
            elif g.winkel_zu((tv.x, tv.y), tv.vorne, (sofa.x, sofa.y)) > 80:
                bef.append(Befund(0.6, f"{tv.name} zeigt vom {sofa.name} weg", tv.name))
    return bef


# ============================================================ LICHT (Kap. 5 Künstliches Licht)
@regel("L01", "Keine Hängeleuchte über Bett oder Sitzplatz",
       "Schwere Pendel-/Kronleuchter und Ventilatoren nie über Bett, Sofa oder Sitzplatz – sie hängen wie eine Last "
       "über dir. Besser über Couch- oder Esstisch (eine leichte Papierleuchte über dem Bett ist ok).",
       "Kap. 3 Kronleuchter, Kap. 4 Wohnzimmer/Schlafzimmer, Kap. 5 Licht", "chi", 1.5)
def _l01(layout):
    bef = []
    for p in layout.moebel:
        if not p.ist_deckenobjekt:
            continue
        for m in _haupt(layout):
            if m.typ == "bett":
                getroffen = g.abstand_punkt_rechteck((p.x, p.y), m.rechteck) < 0.15
            else:
                getroffen = math.dist((p.x, p.y), g.personenpunkt(m)) < 0.6
            if getroffen:
                bef.append(Befund(0.8, f"{p.name} hängt über {m.name}", p.name))
    return bef


@regel("L02", "Pendelleuchte über dem Tisch",
       "Die Hängeleuchte gehört mittig über den Esstisch (bzw. den Couchtisch) – sie zieht die Leute an den Tisch. "
       "Nur eine Statement-Leuchte pro Raum.", "Kap. 4 Esszimmer, Kap. 5 Hängeleuchten", "stil", 1.0,
       raumtypen={"esszimmer", "wohnzimmer", "studio"})
def _l02(layout):
    bef = []
    pend = [p for p in layout.moebel if p.typ == "pendelleuchte"]
    tische = layout.finde("esstisch") or layout.finde("couchtisch")
    if len(pend) > 1:
        bef.append(Befund(0.3, f"{len(pend)} Hängeleuchten – nur eine Statement-Leuchte pro Raum", pend[1].name))
    for p in pend:
        if tische:
            t = min(tische, key=lambda t: math.dist((p.x, p.y), (t.x, t.y)))
            d = math.dist((p.x, p.y), (t.x, t.y))
            if d > 0.25:
                bef.append(Befund(min(1.0, d / 1.0), f"{p.name} hängt {d:.2f} m neben der Mitte von {t.name}", p.name))
    return bef


@regel("L03", "Drei von vier Ecken beleuchten",
       "Mehrere niedrige Lichtquellen statt einem Deckenlicht: etwa drei von vier Raumecken mit Steh- oder "
       "Tischleuchten beleuchten, eine Ecke bewusst im Schatten (Yin) lassen.", "Kap. 5 Künstliches Licht",
       "stil", 0.8, raumtypen={"schlafzimmer", "kinderzimmer", "gaestezimmer", "wohnzimmer", "esszimmer", "buero",
                               "studio"})
def _l03(layout):
    raum = layout.raum
    lampen = [m for m in layout.moebel if m.typ in ("stehleuchte", "tischleuchte")]
    if not lampen:
        return [Befund(0.3, "Keine Steh-/Tischleuchten eingetragen – mehrere niedrige Lichtquellen einplanen "
                            "(vorhandene Lampen als 'stehleuchte'/'tischleuchte' eintragen)")]
    ecken = [(0, 0), (raum.breite, 0), (0, raum.tiefe), (raum.breite, raum.tiefe)]
    hell = sum(1 for e in ecken if any(math.dist(e, (l.x, l.y)) < 1.3 for l in lampen))
    if hell < 2:
        return [Befund(0.5, f"Nur {hell} Ecke(n) beleuchtet – Ziel: drei von vier Ecken")]
    if hell == 4:
        return [Befund(0.2, "Alle vier Ecken beleuchtet – eine Ecke darf im Schatten bleiben (Yin)")]
    return []


# ============================================================ ESSZIMMER (Kap. 4)
@regel("E01", "Esstisch: rund ist am besten",
       "Runde Tische haben keine Ecken und keine Hierarchie; danach oval, quadratisch (Erde) und rechteckig. "
       "Unregelmäßige oder zusammengeschobene Tische vermeiden.", "Kap. 4 Esszimmer – Tischform", "stil", 0.6,
       raumtypen={"esszimmer", "wohnzimmer", "studio", "kueche"})
def _e01(layout):
    bef = []
    tische = layout.finde("esstisch")
    for t in tische:
        if not t.rund:
            quad = abs(t.breite - t.tiefe) < 0.1
            bef.append(Befund(0.15 if quad else 0.3, f"{t.name} ist {'quadratisch' if quad else 'rechteckig'} – "
                                                    f"rund oder oval wäre harmonischer", t.name))
    if len(tische) > 1:
        bef.append(Befund(0.6, "Mehrere Esstische – lieber ein ganzer, einheitlicher Tisch", tische[1].name))
    return bef


@regel("E02", "Gerade Anzahl gleicher Stühle",
       "Immer eine gerade Anzahl Stühle, alle gleich (keine Hierarchie), keiner an einer Tischecke. "
       "Ersatzstühle gehören nicht in den Raum.", "Kap. 4 Esszimmer – Stühle", "stil", 0.8,
       raumtypen={"esszimmer", "wohnzimmer", "studio", "kueche"})
def _e02(layout):
    bef = []
    tische = layout.finde("esstisch")
    stuehle = layout.finde("stuhl")
    if not tische or not stuehle:
        return bef
    if len(stuehle) % 2 == 1:
        bef.append(Befund(0.6, f"{len(stuehle)} Stühle – besser eine gerade Anzahl", stuehle[0].name))
    if len({(round(s.breite, 2), round(s.tiefe, 2)) for s in stuehle}) > 1:
        bef.append(Befund(0.3, "Stühle haben unterschiedliche Größen – alle gleich wirken fair", stuehle[0].name))
    for s in stuehle:
        t = min(tische, key=lambda t: math.dist((s.x, s.y), (t.x, t.y)))
        if not t.rund:
            for e in g.ecken(t.rechteck):
                if math.dist(e, (s.x, s.y)) < 0.3:
                    bef.append(Befund(0.4, f"{s.name} steht an einer Tischecke", s.name))
                    break
        if g.abstand_rechtecke(s.rechteck, t.rechteck) > 0.6:
            bef.append(Befund(0.4, f"{s.name} steht abseits vom Tisch (wirkt wie ein unwillkommener Gast)", s.name))
    return bef


@regel("E03", "Nur Tisch und Stühle in der Mitte",
       "Konsolen und Sideboards stehen an der Wand, die Raummitte gehört dem Esstisch. Nichts darf den Tisch "
       "überragen.", "Kap. 4 Esszimmer – andere Möbel", "stil", 0.6, raumtypen={"esszimmer"})
def _e03(layout):
    bef = []
    for m in _boden(layout):
        if m.typ in ("esstisch", "stuhl", "pflanze", "stehleuchte"):
            continue
        if not g.an_wand(m, layout.raum, 0.2):
            bef.append(Befund(0.5, f"{m.name} steht frei im Raum – an die Wand stellen", m.name))
    return bef


@regel("E04", "Esstisch nicht im Eingang",
       "Der Tisch soll die Tür im Blick haben, aber nicht im Weg stehen; kein Sitzplatz direkt an der Tür und "
       "nicht in einer Linie mit der Tür.", "Kap. 4 Esszimmer – Lage", "chi", 1.2,
       raumtypen={"esszimmer", "wohnzimmer", "studio", "kueche"})
def _e04(layout):
    bef = []
    t = layout.raum.haupttuer
    if t is None:
        return bef
    tm = t.mitte(layout.raum)
    for tisch in layout.finde("esstisch"):
        d = g.abstand_punkt_rechteck(tm, tisch.rechteck)
        if d < 1.2:
            bef.append(Befund((1.2 - d) / 1.2, f"{tisch.name} steht nur {d:.1f} m von der Tür", tisch.name))
        if g.in_tuerflucht(tisch, t, layout.raum, 0.0):
            bef.append(Befund(0.4, f"{tisch.name} steht in einer Linie mit der Tür (Konsole davor schützt)", tisch.name))
    return bef


@regel("E05", "Spiegel spiegelt den Esstisch",
       "Im Esszimmer sind Spiegel gut, wenn sie das Essen (Fülle) spiegeln – nicht die Tür.",
       "Kap. 4 Esszimmer, Kap. 5 Spiegel", "stil", 0.6, raumtypen={"esszimmer"})
def _e05(layout):
    bef = []
    tische = layout.finde("esstisch")
    for sp in layout.finde("spiegel"):
        if tische and all(g.winkel_zu((sp.x, sp.y), sp.vorne, (t.x, t.y)) > 50 for t in tische):
            bef.append(Befund(0.5, f"{sp.name} spiegelt nicht den Esstisch", sp.name))
    return bef


@regel("E06", "Keine Uhr im Ess- und Schlafzimmer",
       "Uhren erzeugen Zeitdruck – im Esszimmer zählt die Gesellschaft, im Schlafzimmer die Ruhe.",
       "Kap. 4 Esszimmer, Kap. 5 Kunst – Uhren", "stil", 0.6, raumtypen={"esszimmer", "schlafzimmer", "gaestezimmer"})
def _e06(layout):
    return [Befund(0.7, f"{u.name} im {layout.raum.raumtyp}", u.name) for u in layout.finde("uhr")]


# ============================================================ GETEILTES SCHLAFZIMMER (Kap. 4)
@regel("G01", "Geteiltes Zimmer: gleiche Betten mit Abstand",
       "Mehrere Betten im Raum: gleich groß (kein Ungleichgewicht zwischen den Personen) und mit Abstand. "
       "Keine zwei Einzelbetten zusammenschieben – das steht für eine versteckte Trennung.",
       "Kap. 4 Geteilte Schlafzimmer", "zonen", 1.5, raumtypen=SCHLAFRAEUME)
def _g01(layout):
    bef = []
    betten = layout.finde("bett")
    for i, a in enumerate(betten):
        for b in betten[i + 1:]:
            if abs(a.breite - b.breite) > 0.05 or abs(a.tiefe - b.tiefe) > 0.05:
                bef.append(Befund(0.5, f"{a.name} und {b.name} sind unterschiedlich groß", b.name))
            d = g.abstand_rechtecke(a.rechteck, b.rechteck)
            if d < 0.3:
                bef.append(Befund(1.0 if d < 0.05 else 0.6,
                                  f"{a.name} und {b.name} stehen {'zusammengeschoben' if d < 0.05 else 'zu dicht'}", b.name))
    return bef


@regel("G02", "Nicht die Füße zum Kopf des anderen",
       "Im geteilten Zimmer darf niemandes Fußende auf den Kopf einer anderen Person zeigen. "
       "Kopfteile Rücken an Rücken sind okay.", "Kap. 4 Geteilte Schlafzimmer", "zonen", 1.2, raumtypen=SCHLAFRAEUME)
def _g02(layout):
    bef = []
    betten = layout.finde("bett")
    for a in betten:
        for b in betten:
            if a is b:
                continue
            kopf_b = g.personenpunkt(b)
            fx, fy = a.vorne
            vor = (kopf_b[0] - a.x) * fx + (kopf_b[1] - a.y) * fy
            quer = abs((kopf_b[0] - a.x) * fy - (kopf_b[1] - a.y) * fx)
            if vor > a.tiefe / 2 and quer < a.breite / 2 + 0.2:
                bef.append(Befund(0.8, f"Fußende von {a.name} zeigt auf den Kopf in {b.name}", a.name))
    return bef


@regel("G03", "Kein Etagenbett",
       "Etagenbetten möglichst vermeiden; wenn nötig, schläft die ältere Person oben.",
       "Kap. 4 Geteilte Schlafzimmer", "stil", 0.5, raumtypen=SCHLAFRAEUME)
def _g03(layout):
    return [Befund(0.6, f"{m.name}: Etagenbett – wenn nötig, Ältere oben", m.name) for m in layout.finde("etagenbett")]


# ============================================================ STUDIO (Kap. 4 Gemeinsame Räume)
@regel("ST1", "Studio: Schichten von ruhig nach aktiv",
       "In einer Ein-Raum-Wohnung: Bett im ruhigsten, hintersten Teil; davor der Wohnbereich als Puffer; dann Essen; "
       "die Küche so weit wie möglich vom Bett weg. Esstisch nahe an der Küche.",
       "Kap. 4 Studio-Apartments", "zonen", 2.0, raumtypen={"studio"})
def _st1(layout):
    bef = []
    t = layout.raum.haupttuer
    betten = layout.finde("bett")
    if t is None or not betten:
        return bef
    tm = t.mitte(layout.raum)
    bett = betten[0]
    d_bett = math.dist(tm, (bett.x, bett.y))
    for m in _boden(layout):
        if m.typ in ("sofa", "esstisch", "herd", "spuele", "kuehlschrank") and math.dist(tm, (m.x, m.y)) > d_bett + 0.3:
            bef.append(Befund(0.5, f"{m.name} liegt weiter hinten als das Bett – das Bett gehört in den ruhigsten Teil",
                              m.name))
    for k in layout.finde("herd"):
        d = g.abstand_rechtecke(k.rechteck, bett.rechteck)
        if d < 2.0:
            bef.append(Befund((2.0 - d) / 2.0, f"{k.name} ist nur {d:.1f} m vom Bett entfernt", k.name))
        for e in layout.finde("esstisch"):
            d = g.abstand_rechtecke(k.rechteck, e.rechteck)
            if d > 2.5:
                bef.append(Befund(0.4, f"{e.name} ist {d:.1f} m von der Küche entfernt – Esstisch nahe zur Küche", e.name))
    return bef


# ============================================================ KÜCHE (Kap. 4)
@regel("KU1", "Herd in der Kommandoposition",
       "Der Herd ist das wichtigste Element: hinten im Raum, von der Tür aus sichtbar, aber nicht direkt zur Tür "
       "gerichtet und nicht gleich neben dem Eingang.", "Kap. 4 Küche – Herd", "kommando", 2.0,
       raumtypen={"kueche", "studio"})
def _ku1(layout):
    bef = []
    t = layout.raum.haupttuer
    if t is None:
        return bef
    tm = t.mitte(layout.raum)
    for h in layout.finde("herd"):
        if g.schaut_zur_oeffnung(h, t):
            bef.append(Befund(0.8, f"{h.name} steht der Tür direkt gegenüber", h.name))
        d = g.abstand_punkt_rechteck(tm, h.rechteck)
        if d < 1.5:
            bef.append(Befund((1.5 - d) / 1.5, f"{h.name} steht nur {d:.1f} m von der Tür", h.name))
    return bef


@regel("KU2", "Feuer und Wasser trennen",
       "Herd (Feuer) nicht direkt neben oder gegenüber von Spüle und Kühlschrank (Wasser) – mindestens eine "
       "Arbeitsfläche dazwischen, oder Holz (Pflanze) als Vermittler.", "Kap. 4 Küche – Prinzipien", "chi", 1.5,
       raumtypen={"kueche", "studio"})
def _ku2(layout):
    bef = []
    for h in layout.finde("herd"):
        for w in layout.finde("spuele") + layout.finde("kuehlschrank") + layout.finde("geschirrspueler"):
            d = g.abstand_rechtecke(h.rechteck, w.rechteck)
            if d < 0.45:
                hat_holz = any(g.abstand_rechtecke(p.rechteck, h.rechteck) < 0.8 and
                               g.abstand_rechtecke(p.rechteck, w.rechteck) < 0.8 for p in layout.finde("pflanze"))
                bef.append(Befund(0.3 if hat_holz else 0.8, f"{h.name} steht direkt neben {w.name} "
                                  f"({d:.2f} m)" + (" – Pflanze vermittelt" if hat_holz else ""), h.name))
            elif h.vorne == tuple(-v for v in w.vorne) and g.winkel_zu((h.x, h.y), h.vorne, (w.x, w.y)) < 25:
                bef.append(Befund(0.5, f"{h.name} und {w.name} stehen sich direkt gegenüber", h.name))
    return bef


@regel("KU3", "Herd nicht unter dem Fenster",
       "Ein Kochfeld unter dem Fenster lässt die Energie entweichen – besser an eine Wand mit Spritzschutz "
       "oder auf eine Kochinsel. Die Spüle darf unter dem Fenster stehen.", "Kap. 4 Küche – Kochfeld", "chi", 1.0,
       raumtypen={"kueche", "studio"})
def _ku3(layout):
    bef = []
    for h in layout.finde("herd"):
        wand = VEKTOR_WAND[h.hinten]
        a, b = g.spanne_quer(h, h.hinten)
        if g.rueckenabstand(h, layout.raum) < 0.3 and g.oeffnungen_an_wand(layout.raum, wand, a, b, nur=("fenster",)):
            bef.append(Befund(0.8, f"{h.name} steht unter einem Fenster", h.name))
    return bef


@regel("KU4", "Keine Spiegel in der Küche",
       "Spiegel verteilen das aggressive Chi der Küche – vor allem nie einen Spiegel, der auf den Herd zeigt.",
       "Kap. 4 Küche, Kap. 5 Spiegel", "chi", 1.0, raumtypen={"kueche"})
def _ku4(layout):
    bef = []
    for sp in layout.finde("spiegel"):
        bef.append(Befund(0.5, f"{sp.name} in der Küche", sp.name))
        for h in layout.finde("herd"):
            if g.winkel_zu((sp.x, sp.y), sp.vorne, (h.x, h.y)) < 40:
                bef.append(Befund(0.5, f"{sp.name} spiegelt den Herd", sp.name))
    return bef


# ============================================================ BAD (Kap. 4)
@regel("BA1", "WC nicht in Sicht- und Türlinie",
       "Das WC soll von der Tür aus nicht sichtbar sein und nicht in einer Linie mit der Tür stehen – aber selbst die "
       "Tür im Blick haben (Sicherheit). An eine Wand, nicht unters Fenster, nicht frei im Raum.",
       "Kap. 4 Bad – WC", "kommando", 2.0, raumtypen={"bad"})
def _ba1(layout):
    bef = []
    t = layout.raum.haupttuer
    for wc in layout.finde("wc"):
        if t is not None:
            tm = g.punkt_vor_oeffnung(t, layout.raum, 0.1)
            if g.in_tuerflucht(wc, t, layout.raum, 0.0):
                bef.append(Befund(0.8, f"{wc.name} steht in einer Linie mit der Tür", wc.name))
            elif g.winkel_zu(tm, WAND_NORMALE[t.wand], (wc.x, wc.y)) < 35:
                bef.append(Befund(0.5, f"{wc.name} ist von der Tür aus direkt sichtbar", wc.name))
            if g.winkel_zu((wc.x, wc.y), wc.vorne, tm) > 110:
                bef.append(Befund(0.4, f"Von {wc.name} aus sieht man die Tür nicht", wc.name))
        if g.rueckenabstand(wc, layout.raum) > 0.15:
            bef.append(Befund(0.8, f"{wc.name} steht nicht an der Wand", wc.name))
        wand = VEKTOR_WAND[wc.hinten]
        a, b = g.spanne_quer(wc, wc.hinten)
        if g.oeffnungen_an_wand(layout.raum, wand, a, b, nur=("fenster",)):
            bef.append(Befund(0.5, f"{wc.name} steht vor einem Fenster", wc.name))
    return bef


@regel("BA2", "WC weg von der Badewanne",
       "Niemand will in der Wanne liegen und das WC neben dem Gesicht haben. Das Waschbecken kann WC und Wanne "
       "trennen; eine Dusche neben dem WC ist eher akzeptabel.", "Kap. 4 Bad – WC", "zonen", 1.2, raumtypen={"bad"})
def _ba2(layout):
    bef = []
    for wc in layout.finde("wc"):
        for w in layout.finde("badewanne"):
            d = g.abstand_rechtecke(wc.rechteck, w.rechteck)
            if d < 0.8:
                bef.append(Befund((0.8 - d) / 0.8, f"{wc.name} steht nur {d:.2f} m von der {w.name}", wc.name))
    return bef


@regel("BA3", "Badewanne: Blickfang, Füße nicht zur Tür",
       "Die Wanne verankert das Bad optisch und ist das Erste, was man beim Eintreten sieht – aber ihr Fußende "
       "zeigt nicht in Linie zur Tür.", "Kap. 4 Bad – Badewanne", "kommando", 1.0, raumtypen={"bad"})
def _ba3(layout):
    bef = []
    t = layout.raum.haupttuer
    for w in layout.finde("badewanne") + layout.finde("dusche"):
        if t is not None and g.in_tuerflucht(w, t, layout.raum, 0.0) and w.typ == "badewanne":
            vorne_wand = VEKTOR_WAND[w.vorne]
            if vorne_wand == t.wand:
                bef.append(Befund(0.7, f"Fußende der {w.name} zeigt zur Tür", w.name))
        if t is not None and w.typ == "dusche" and g.in_tuerflucht(w, t, layout.raum, 0.0):
            bef.append(Befund(0.2, f"{w.name} steht in Linie mit der Tür", w.name))
    return bef


@regel("BA4", "Waschbecken: Rücken nicht zur Tür",
       "Beim Händewaschen soll die Tür nicht direkt hinter dir sein – Waschtisch und Spiegel am besten im rechten "
       "Winkel zur Tür.", "Kap. 4 Bad – Waschbecken", "kommando", 0.8, raumtypen={"bad"})
def _ba4(layout):
    bef = []
    t = layout.raum.haupttuer
    if t is None:
        return bef
    for w in layout.finde("waschbecken"):
        if VEKTOR_WAND[w.vorne] == t.wand:       # du stehst davor und schaust zur Wand -> Tür im Rücken
            bef.append(Befund(0.6, f"Am {w.name} hast du die Tür im Rücken", w.name))
    return bef


@regel("BA5", "Kein Spiegel auf das WC",
       "Spiegel im Bad nicht so hängen, dass sie das WC spiegeln.", "Kap. 4 Bad", "stil", 0.8, raumtypen={"bad"})
def _ba5(layout):
    bef = []
    for sp in layout.finde("spiegel"):
        for wc in layout.finde("wc"):
            if g.winkel_zu((sp.x, sp.y), sp.vorne, (wc.x, wc.y)) < 35:
                bef.append(Befund(0.7, f"{sp.name} spiegelt das WC", sp.name))
    return bef


# ============================================================ WEITERE BUCHREGELN (Version 4)
_FENSTER_PFLICHT = {"schlafzimmer", "kinderzimmer", "gaestezimmer", "buero", "esszimmer", "kueche", "studio",
                    "wohnzimmer"}


@regel("C08", "Tür und Fenster auf verschiedenen Wänden",
       "Chi kann nicht durch dieselbe Öffnung herein und hinaus: Ein Raum braucht Tür UND Fenster, am besten auf "
       "verschiedenen Wänden. Schlafzimmer und Arbeitsräume nie ohne Fenster.",
       "Kap. 2 Chi, Kap. 4 Schlafzimmer/Büro/Küche", "chi", 2.0)
def _c08(layout):
    raum = layout.raum
    fenster = [o for o in raum.oeffnungen if o.ist_fenster]
    if not fenster:
        if raum.raumtyp in ("flur", "bad"):
            return [Befund(0.3, "Raum ohne Fenster – gut lüften, Licht an die Wände")]
        s = 1.0 if raum.raumtyp in _FENSTER_PFLICHT else 0.5
        return [Befund(s, f"{raum.raumtyp.capitalize()} ohne Fenster – Chi kann nicht zirkulieren")]
    tueren = raum.tueren
    if tueren and all(f.wand == t.wand for f in fenster for t in tueren):
        return [Befund(0.4, "Tür und Fenster liegen auf derselben Wand – der hintere Raum bekommt wenig Chi")]
    return []


@regel("C09", "Spiegel spiegelt keine Tür und keinen Fernseher",
       "Spiegel verdoppeln, was sie zeigen: Eine gespiegelte Tür lässt das Chi hinausfließen, ein gespiegelter "
       "Fernseher verdoppelt die Unruhe. Spiegel sollen Schönes zeigen.", "Kap. 4 Wohnzimmer/Esszimmer, Kap. 5",
       "chi", 1.2)
def _c09(layout):
    bef = []
    raum = layout.raum
    for sp in layout.finde("spiegel"):
        p = (sp.x, sp.y)
        for t in raum.tueren:
            if t.wand == VEKTOR_WAND[(-sp.vorne[0], -sp.vorne[1])]:
                continue
            if g.winkel_zu(p, sp.vorne, t.mitte(raum)) < 30:
                bef.append(Befund(0.6, f"{sp.name} spiegelt die {t.typ} ({t.wand})", sp.name))
        for tv in layout.finde("tv"):
            if g.winkel_zu(p, sp.vorne, (tv.x, tv.y)) < 30:
                bef.append(Befund(0.4, f"{sp.name} spiegelt {tv.name}", sp.name))
    return bef


@regel("C10", "Kein Windspiel oder Mobile über Bett und Schreibtisch",
       "Windspiele nehmen Chi auf und bremsen es – richtig in Durchgängen oder bei vielen Fenstern, aber nie über "
       "Bett oder Schreibtisch.", "Kap. 5 Bewegte Objekte", "chi", 1.0)
def _c10(layout):
    bef = []
    for w in layout.moebel:
        if w.typ not in ("windspiel", "mobile"):
            continue
        for m in _haupt(layout):
            ziel = g.abstand_punkt_rechteck((w.x, w.y), m.rechteck) < 0.1 if m.typ == "bett" \
                else math.dist((w.x, w.y), g.personenpunkt(m)) < 0.6
            if ziel:
                bef.append(Befund(0.8 if w.typ == "windspiel" else 0.4, f"{w.name} hängt über {m.name}", w.name))
    return bef


@regel("C11", "Religiöse Objekte am richtigen Ort",
       "Religiöse Objekte gehören in den wichtigsten Raum (Wohnzimmer), nicht ins Schlafzimmer, nicht auf den Boden "
       "und nicht in einer Linie mit dem Bett.", "Kap. 5 Religiöse Objekte", "zonen", 0.8)
def _c11(layout):
    bef = []
    for a in layout.finde("altar"):
        if layout.raum.raumtyp in SCHLAFRAEUME:
            bef.append(Befund(0.6, f"{a.name} steht im Schlafzimmer", a.name))
        if a.hoehe < 0.3:
            bef.append(Befund(0.5, f"{a.name} steht auf dem Boden", a.name))
        for b in layout.finde("bett"):
            if g.winkel_zu(g.personenpunkt(b), b.vorne, (a.x, a.y)) < 20:
                bef.append(Befund(0.6, f"{a.name} steht in einer Linie mit {b.name}", a.name))
    return bef


@regel("K17", "Nachttische als ausgewogenes Paar",
       "Drache und Tiger: Zwei Nachttische mit gleichem visuellem Gewicht geben dem Bett Halt zu beiden Seiten. "
       "Sie sollen nicht höher als die Matratze aufragen.", "Kap. 2 Fünf Tiere, Kap. 4 Schlafzimmer – Nachttische",
       "kommando", 0.8, raumtypen={"schlafzimmer", "gaestezimmer", "studio"})
def _k17(layout):
    bef = []
    nachttische = layout.finde("nachttisch")
    for b in layout.finde("bett"):
        eigene = [n for n in nachttische if n.gehoert_zu == b.name or g.abstand_rechtecke(n.rechteck, b.rechteck) < 0.3]
        einseitig_an_wand = max((_zone_frei(layout, z, [b] + _kinder(layout, b)) for z in _bett_seitenzonen(b, 0.12)),
                                default=0) > 0.6
        if not eigene:
            bef.append(Befund(0.4, f"{b.name} hat keine Nachttische", b.name))
        elif len(eigene) == 1 and not einseitig_an_wand:
            bef.append(Befund(0.5, f"{b.name} hat nur auf einer Seite einen Nachttisch", b.name))
        elif len(eigene) >= 2:
            a, c = eigene[0], eigene[1]
            if abs(a.hoehe - c.hoehe) > 0.15 or abs(a.breite * a.tiefe - c.breite * c.tiefe) > 0.12:
                bef.append(Befund(0.3, "Die Nachttische sind sehr unterschiedlich (Ungleichgewicht)", b.name))
        for n in eigene:
            if n.hoehe > b.hoehe + 0.25:
                bef.append(Befund(0.3, f"{n.name} ragt über das Bett auf ({n.hoehe:.2f} m)", n.name))
    return bef


@regel("W01", "Zwei Sofas gegenüber brauchen einen Tisch",
       "Zwei Sofas, die sich über eine leere Fläche ansehen, wirken konfrontativ und formell – ein Couchtisch "
       "dazwischen entschärft die Spannung.", "Kap. 4 Wohnzimmer – Sofa", "stil", 1.0, raumtypen={"wohnzimmer", "studio"})
def _w01(layout):
    bef = []
    sofas = layout.finde("sofa")
    tische = layout.finde("couchtisch") + layout.finde("beistelltisch")
    for i, a in enumerate(sofas):
        for b in sofas[i + 1:]:
            gegenueber = a.vorne == tuple(-v for v in b.vorne) and g.winkel_zu((a.x, a.y), a.vorne, (b.x, b.y)) < 30
            if not gegenueber:
                continue
            mitte = ((a.x + b.x) / 2, (a.y + b.y) / 2)
            if not any(g.abstand_punkt_rechteck(mitte, t.rechteck) < 0.5 for t in tische):
                bef.append(Befund(0.8, f"{a.name} und {b.name} stehen sich ohne Tisch gegenüber", a.name))
    return bef


@regel("W02", "Couchtisch als Anker",
       "Ohne Couchtisch schwebt das Wohnzimmer um eine Leere. Der Tisch verbindet die Sitzplätze, vermittelt im "
       "Gespräch und steht – mit Blumen oder Obst darauf – für Fülle.", "Kap. 4 Wohnzimmer – Couchtisch", "stil", 0.8,
       raumtypen={"wohnzimmer", "studio"})
def _w02(layout):
    if not layout.finde("sofa"):
        return []
    if layout.finde("couchtisch"):
        return []
    if layout.finde("beistelltisch"):
        return [Befund(0.2, "Nur Beistelltisch – ein Couchtisch in der Mitte würde den Raum verankern")]
    return [Befund(0.7, "Kein Couchtisch: Die Sitzgruppe hat keine Mitte")]


@regel("W03", "Sofa nicht allein",
       "Erst mehrere Sitzplätze bilden eine Gemeinschaft: Das Sofa mit Sessel, Bank oder Hocker ergänzen.",
       "Kap. 4 Wohnzimmer – Sofa", "stil", 0.5, raumtypen={"wohnzimmer", "studio"})
def _w03(layout):
    if layout.finde("sofa") and not any(layout.finde(t) for t in ("sessel", "hocker", "bank")):
        return [Befund(0.6, "Das Sofa steht allein – ein Sessel oder Hocker schließt den Sitzkreis")]
    return []


@regel("B01", "Bücher in Reichweite des Arbeitsplatzes",
       "Das Bücherregal soll vom Arbeitsplatz gut erreichbar sein; Nachschlagewerke hinter dir geben Rückhalt.",
       "Kap. 4 Büro – Regale", "stil", 0.5, raumtypen={"buero", "studio", "schlafzimmer", "kinderzimmer"})
def _b01(layout):
    bef = []
    regale = layout.finde("regal")
    for d in layout.finde("schreibtisch"):
        if regale:
            dist = min(math.dist(g.personenpunkt(d), (r.x, r.y)) for r in regale)
            if dist > 2.2:
                bef.append(Befund(min(1.0, (dist - 2.2) / 2 + 0.3), f"Das Regal ist {dist:.1f} m vom {d.name} entfernt",
                                  d.name))
    return bef


@regel("B02", "Geteiltes Büro: gleich große Tische",
       "Arbeiten mehrere Gleichgestellte im Raum, sollen alle gleich große Tische und keine schlechte Position "
       "haben – sonst entstehen Konflikte.", "Kap. 4 Büro – geteilter Arbeitsplatz", "zonen", 0.8,
       raumtypen={"buero"})
def _b02(layout):
    tische = layout.finde("schreibtisch")
    if len(tische) < 2:
        return []
    fl = [t.breite * t.tiefe for t in tische]
    if max(fl) - min(fl) > 0.15:
        return [Befund(0.5, "Die Schreibtische sind unterschiedlich groß (Ungleichgewicht)")]
    return []


@regel("B03", "Tagesbett im Büro nicht zur Tür",
       "Die beste Position bleibt dem Schreibtisch; ein Sofa oder Tagesbett soll aber nicht mit dem Fußende zur "
       "Tür zeigen.", "Kap. 4 Büro – Sitz- und Ruhemöbel", "kommando", 0.6, raumtypen={"buero"})
def _b03(layout):
    bef = []
    for m in layout.finde("tagesbett") + layout.finde("sofa"):
        for t in layout.raum.tueren:
            if g.schaut_zur_oeffnung(m, t):
                bef.append(Befund(0.6, f"{m.name} zeigt direkt zur Tür", m.name))
    return bef


@regel("KU5", "Ofen nicht auf Sitzplätze richten",
       "Der Ofen strahlt sein Feuer nach vorne ab – Sitzplätze gehören nicht direkt davor.",
       "Kap. 4 Küche – Herd und Ofen", "chi", 1.0, raumtypen={"kueche", "studio"})
def _ku5(layout):
    bef = []
    sitze = [m for m in layout.moebel if m.typ in ("stuhl", "sofa", "sessel", "esstisch", "bank")]
    for h in layout.finde("herd"):
        zone = _zone_vorne(h, 1.2)
        for s in sitze:
            if g.ueberlappung(zone, s.rechteck) > 0.02:
                bef.append(Befund(0.6, f"{s.name} steht direkt vor dem {h.name}", h.name))
    return bef


@regel("E07", "Keine lange Bank am Esstisch",
       "Besonders in langen Esszimmern bremsen Stühle mit Armlehnen das schnelle Chi; lange Bänke verstärken es.",
       "Kap. 4 Esszimmer – lange Räume", "stil", 0.5, raumtypen={"esszimmer", "wohnzimmer", "studio", "kueche"})
def _e07(layout):
    bef = []
    for b in layout.finde("bank"):
        for t in layout.finde("esstisch"):
            if g.abstand_rechtecke(b.rechteck, t.rechteck) < 0.6 and b.breite >= 1.2:
                bef.append(Befund(0.5, f"{b.name} steht als lange Bank am {t.name}", b.name))
    return bef


_ANKER = {"schlafzimmer": ("bett",), "kinderzimmer": ("bett",), "gaestezimmer": ("bett", "tagesbett"),
          "wohnzimmer": ("sofa",), "studio": ("sofa", "bett"), "esszimmer": ("esstisch",),
          "buero": ("schreibtisch",), "kueche": ("herd",), "bad": ("badewanne", "dusche")}


@regel("S08", "Erster Eindruck: Hauptmöbel verankert den Blick",
       "Der Raum soll vom Eingang aus gut aussehen; das Hauptmöbel (Bett, Sofa, Schreibtisch, Esstisch) zeigt "
       "sofort, wofür der Raum da ist, und verankert den Blick.", "Kap. 5 Eindrücke – der erste Blick", "stil", 0.6)
def _s08(layout):
    raum = layout.raum
    t = raum.haupttuer
    typen = _ANKER.get(raum.raumtyp)
    if t is None or not typen:
        return []
    anker = [m for m in layout.moebel if m.typ in typen]
    if not anker:
        return []
    p = g.punkt_vor_oeffnung(t, raum, 0.4)
    blick = WAND_NORMALE[t.wand]
    hindernisse = [m.rechteck for m in _boden(layout) if m.hoehe >= 1.4 and m.typ not in typen]
    for m in anker:
        if g.winkel_zu(p, blick, (m.x, m.y)) < 80 and g.sichtlinie_frei(p, (m.x, m.y), hindernisse):
            return []
    return [Befund(0.6, f"Vom Eingang aus sieht man das Hauptmöbel ({anker[0].name}) nicht", anker[0].name)]


@regel("S09", "Kein Fernseher über dem Kamin",
       "Über dem Kamin bekommt der Fernseher zu viel Bedeutung – er wird zum Altar des Raums.",
       "Kap. 4 Wohnzimmer – Fernseher", "stil", 1.0, raumtypen={"wohnzimmer", "studio"})
def _s09(layout):
    bef = []
    for tv in layout.finde("tv"):
        for k in layout.finde("kamin"):
            if g.abstand_rechtecke(tv.rechteck, k.rechteck) < 0.3 and VEKTOR_WAND[tv.hinten] == VEKTOR_WAND[k.hinten]:
                bef.append(Befund(1.0, f"{tv.name} steht/hängt am Kamin", tv.name))
    return bef


@regel("T01", "Tierkäfige an den richtigen Ort",
       "Vögel, Nager, Fische und Reptilien nicht in Küche (Dämpfe), Bad (Feuchte) oder Schlafzimmer (Unruhe in der "
       "Nacht); Käfig an eine Wand für Schutz, weg vom Eingang mit seinem Trubel.", "Kap. 4 Haustiere", "zonen", 0.8)
def _t01(layout):
    bef = []
    raum = layout.raum
    for k in layout.finde("kaefig") + layout.finde("aquarium"):
        if raum.raumtyp in ("kueche", "bad") or (raum.raumtyp in SCHLAFRAEUME and k.typ == "kaefig"):
            bef.append(Befund(0.8, f"{k.name} im Raum '{raum.raumtyp}'", k.name))
        if k.typ == "kaefig" and not g.an_wand(k, raum, 0.15):
            bef.append(Befund(0.4, f"{k.name} steht frei im Raum statt an einer Wand", k.name))
        t = raum.haupttuer
        if t is not None and g.abstand_punkt_rechteck(t.mitte(raum), k.rechteck) < 1.2:
            bef.append(Befund(0.4, f"{k.name} steht direkt am Eingang", k.name))
    return bef


@regel("T02", "Haustiere sehen die Tür",
       "Tiere suchen ihre Kommandoposition: Eine Hundebox so stellen, dass der Hund sieht, wer hereinkommt; der "
       "Kratzbaum gehört in deine Nähe.", "Kap. 4 Haustiere", "kommando", 0.5)
def _t02(layout):
    bef = []
    t = layout.raum.haupttuer
    for h in layout.finde("hundebox"):
        if t is not None and g.winkel_zu((h.x, h.y), h.vorne, t.mitte(layout.raum)) > 100:
            bef.append(Befund(0.6, f"Aus der {h.name} sieht der Hund die Tür nicht", h.name))
    sitze = _haupt(layout)
    for kb in layout.finde("kratzbaum"):
        if sitze and min(g.abstand_rechtecke(kb.rechteck, s.rechteck) for s in sitze) > 2.5:
            bef.append(Befund(0.3, f"{kb.name} steht weit weg von deinem Platz", kb.name))
    return bef


@regel("T03", "Futter und Katzenklo getrennt",
       "Futter- und Toilettenplatz der Tiere voneinander und vom Schlafplatz trennen; das Katzenklo braucht einen "
       "privaten Ort.", "Kap. 4 Haustiere", "zonen", 0.5)
def _t03(layout):
    bef = []
    for k in layout.finde("katzenklo"):
        for f in layout.finde("futternapf"):
            if g.abstand_rechtecke(k.rechteck, f.rechteck) < 1.5:
                bef.append(Befund(0.7, f"{k.name} steht direkt neben {f.name}", k.name))
        for b in layout.finde("bett") + layout.finde("tierbett"):
            if g.abstand_rechtecke(k.rechteck, b.rechteck) < 1.5:
                bef.append(Befund(0.4, f"{k.name} steht nahe am {b.name}", k.name))
    return bef


# ============================================================ Auswertung
def anwendbare_regeln(raumtyp: str) -> list[Regel]:
    return [r for r in REGELN if r.gilt_fuer(raumtyp)]


def regel_nach_id(rid: str) -> Regel:
    for r in REGELN:
        if r.id == rid:
            return r
    raise KeyError(rid)
