"""
Datenmodell: Raum, Öffnungen (Türen/Fenster), Deckenbalken, Dachschräge, Möbel.

Koordinatensystem (Draufsicht, Meter):
    (0, tiefe) ┌──────── oben ────────┐ (breite, tiefe)
               │                      │
             links                  rechts
               │                      │
         (0,0) └──────── unten ───────┘ (breite, 0)

Möbel-Rotation `rot` = Blickrichtung / Vorderseite des Möbels:
    0   -> schaut nach "oben"   (+y)
    90  -> schaut nach "rechts" (+x)
    180 -> schaut nach "unten"  (-y)
    270 -> schaut nach "links"  (-x)

Bedeutung der Vorderseite je Möbeltyp:
    bett         -> Fußende zeigt in Blickrichtung, Kopfteil ist die Rückseite
    schreibtisch -> Richtung, in die die sitzende Person schaut (Person sitzt an der Rückseite)
    sofa/sessel  -> Sitzrichtung, Rückenlehne ist die Rückseite
    schrank, regal, kommode -> Türen/Front zeigen in Blickrichtung
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional

WAENDE = ("unten", "rechts", "oben", "links")

# Normale jeder Wand ins Rauminnere
WAND_NORMALE = {"unten": (0, 1), "oben": (0, -1), "links": (1, 0), "rechts": (-1, 0)}

ROT_VEKTOR = {0: (0, 1), 90: (1, 0), 180: (0, -1), 270: (-1, 0)}
VEKTOR_ROT = {v: k for k, v in ROT_VEKTOR.items()}

# Wand, die in Richtung eines Vektors liegt
VEKTOR_WAND = {(0, 1): "oben", (0, -1): "unten", (1, 0): "rechts", (-1, 0): "links"}

# Reihenfolge im Uhrzeigersinn (von oben betrachtet) für die Himmelsrichtungs-Zuordnung
_WAENDE_UHRZEIGER = ["oben", "rechts", "unten", "links"]
_HIMMEL_UHRZEIGER = ["N", "O", "S", "W"]

# Möbeltypen, die an der Wand hängen (keine Bodenfläche)
WANDOBJEKTE = {"spiegel", "bild", "wandregal", "pinnwand", "uhr"}
# Möbeltypen ohne "Hindernis"-Wirkung
FLACH = {"teppich", "tischleuchte", "pendelleuchte", "ventilator"}
# Hängen an der Decke (keine Bodenfläche, frei im Raum platzierbar)
DECKENOBJEKTE = {"pendelleuchte", "ventilator"}
LAMPEN = {"stehleuchte", "tischleuchte", "pendelleuchte"}
# Hauptmöbel, für die die Kommandoposition gilt (Buch: Bett, Schreibtisch, Sofa)
KOMMANDO_MOEBEL = {"bett", "schreibtisch", "sofa"}


@dataclass
class Oeffnung:
    """Tür oder Fenster in einer Wand."""
    typ: str                 # "tuer" | "fenster" | "balkontuer" | "schranktuer"
    wand: str                # "unten" | "rechts" | "oben" | "links"
    von: float               # Abstand vom Wandanfang (unten/oben: ab x=0, links/rechts: ab y=0)
    breite: float
    bruestung: float = 0.0   # Fenster: Höhe der Fensterbank über Boden (m)
    hoehe: float = 2.0
    haupttuer: bool = True   # die Zimmertür, durch die man hereinkommt

    @property
    def bis(self) -> float:
        return self.von + self.breite

    def mitte(self, raum: "Raum") -> tuple[float, float]:
        m = self.von + self.breite / 2
        if self.wand == "unten":
            return (m, 0.0)
        if self.wand == "oben":
            return (m, raum.tiefe)
        if self.wand == "links":
            return (0.0, m)
        return (raum.breite, m)

    def endpunkte(self, raum: "Raum") -> tuple[tuple[float, float], tuple[float, float]]:
        if self.wand == "unten":
            return (self.von, 0.0), (self.bis, 0.0)
        if self.wand == "oben":
            return (self.von, raum.tiefe), (self.bis, raum.tiefe)
        if self.wand == "links":
            return (0.0, self.von), (0.0, self.bis)
        return (raum.breite, self.von), (raum.breite, self.bis)

    @property
    def ist_tuer(self) -> bool:
        return self.typ in ("tuer", "balkontuer")

    @property
    def ist_fenster(self) -> bool:
        # Balkon-/Fenstertüren zählen laut Buch als Fenster (Licht) UND als Durchgang
        return self.typ in ("fenster", "balkontuer")


@dataclass
class Balken:
    """Deckenbalken (oder schwere Deckenstruktur) als Rechteck in der Draufsicht."""
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class Schraege:
    """Dachschräge: niedrigste Stelle an `wand`, steigt über `laenge` m auf volle Raumhöhe."""
    wand: str
    hoehe_niedrig: float
    laenge: float


@dataclass
class Raum:
    name: str
    breite: float                       # x-Ausdehnung (m)
    tiefe: float                        # y-Ausdehnung (m)
    raumtyp: str = "schlafzimmer"       # schlafzimmer | buero | wohnzimmer | esszimmer | kinderzimmer | studio
    hoehe: float = 2.5
    oeffnungen: list[Oeffnung] = field(default_factory=list)
    balken: list[Balken] = field(default_factory=list)
    schraege: Optional[Schraege] = None
    nord_wand: Optional[str] = None     # welche Wand zeigt nach Norden? (für Licht-/Farbregeln)
    suedhalbkugel: bool = False
    altbau: bool = False                # Außenwand-Regel fürs Bett gilt nur im Altbau
    aussenwaende: list[str] = field(default_factory=list)

    @property
    def tueren(self) -> list[Oeffnung]:
        return [o for o in self.oeffnungen if o.ist_tuer]

    @property
    def fenster(self) -> list[Oeffnung]:
        return [o for o in self.oeffnungen if o.ist_fenster]

    @property
    def haupttuer(self) -> Optional[Oeffnung]:
        for o in self.oeffnungen:
            if o.typ == "tuer" and o.haupttuer:
                return o
        t = self.tueren
        return t[0] if t else None

    def wandlaenge(self, wand: str) -> float:
        return self.breite if wand in ("unten", "oben") else self.tiefe

    def himmelsrichtung(self, wand: str) -> Optional[str]:
        """Himmelsrichtung, in die eine Wand (bzw. ihr Fenster) nach außen zeigt."""
        if self.nord_wand is None:
            return None
        i = _WAENDE_UHRZEIGER.index(self.nord_wand)
        j = _WAENDE_UHRZEIGER.index(wand)
        return _HIMMEL_UHRZEIGER[(j - i) % 4]

    def deckenhoehe(self, x: float, y: float) -> float:
        if self.schraege is None:
            return self.hoehe
        s = self.schraege
        d = {"unten": y, "oben": self.tiefe - y, "links": x, "rechts": self.breite - x}[s.wand]
        if d >= s.laenge:
            return self.hoehe
        return s.hoehe_niedrig + (self.hoehe - s.hoehe_niedrig) * d / s.laenge

    @property
    def seitenverhaeltnis(self) -> float:
        return max(self.breite, self.tiefe) / min(self.breite, self.tiefe)


@dataclass
class Moebel:
    typ: str
    breite: float           # Maß quer zur Blickrichtung
    tiefe: float            # Maß in Blickrichtung (Bett: Länge!)
    hoehe: float = 0.8
    name: str = ""
    x: float = 0.0          # Mittelpunkt
    y: float = 0.0
    rot: int = 0
    fest: bool = False      # True = Optimierer verschiebt dieses Möbel nicht
    rund: bool = False      # runde Möbel haben keine "spitzen Ecken"
    gehoert_zu: Optional[str] = None   # Name des Elternmöbels (z.B. Nachttisch -> Bett)
    seite: Optional[str] = None        # bei gehoert_zu: "links" | "rechts" | "vorne" | "hinten"
    abstand: float = 0.02              # bei gehoert_zu: Lücke zum Elternmöbel (Couchtisch z.B. 0.45)

    def __post_init__(self):
        if not self.name:
            self.name = self.typ

    @property
    def vorne(self) -> tuple[int, int]:
        return ROT_VEKTOR[self.rot % 360]

    @property
    def hinten(self) -> tuple[int, int]:
        v = self.vorne
        return (-v[0], -v[1])

    @property
    def ausdehnung(self) -> tuple[float, float]:
        """(dx, dy) in Raumkoordinaten."""
        if self.rot % 180 == 0:
            return self.breite, self.tiefe
        return self.tiefe, self.breite

    @property
    def rechteck(self) -> tuple[float, float, float, float]:
        dx, dy = self.ausdehnung
        return (self.x - dx / 2, self.y - dy / 2, self.x + dx / 2, self.y + dy / 2)

    @property
    def ist_wandobjekt(self) -> bool:
        return self.typ in WANDOBJEKTE

    @property
    def ist_deckenobjekt(self) -> bool:
        return self.typ in DECKENOBJEKTE

    def kopie(self) -> "Moebel":
        return copy.copy(self)


@dataclass
class Bewohner:
    """Persönliche Angaben, die die Regeln beeinflussen."""
    paar: bool = False                 # zwei Personen im Bett?
    sucht_partner: bool = False        # Buch: Bett von beiden Seiten zugänglich -> "offen für jemanden"
    viele_bildschirme: bool = False    # Arbeitsplatz mit vielen Monitoren -> lieber zur Wand
    arbeit_wichtiger_als_schlaf: bool = False   # Studio/Schlafzimmer+Arbeiten: Prioritätsentscheidung
    pflanzen_sind_freunde: bool = False         # Buch erlaubt dann Pflanzen im Schlafzimmer (am Fenster)


@dataclass
class Layout:
    raum: Raum
    moebel: list[Moebel]
    bewohner: Bewohner = field(default_factory=Bewohner)

    def finde(self, typ: str) -> list[Moebel]:
        return [m for m in self.moebel if m.typ == typ]

    def nach_name(self, name: str) -> Optional[Moebel]:
        for m in self.moebel:
            if m.name == name:
                return m
        return None

    def kopie(self) -> "Layout":
        return Layout(self.raum, [m.kopie() for m in self.moebel], self.bewohner)
