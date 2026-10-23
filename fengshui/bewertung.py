"""Bewertet ein Layout mit der Regelbasis und erzeugt einen lesbaren Bericht."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .modell import Layout
from .regeln import Befund, Regel, anwendbare_regeln


@dataclass
class Ergebnis:
    score: float                         # 0..100 (nur weiche Regeln; 100 = keine Verstöße)
    harte_strafe: float                  # Summe gewichteter harter Verstöße (0 = alles machbar)
    strafen: dict[str, float]            # Regel-ID -> Strafe 0..1
    befunde: dict[str, list[Befund]]     # Regel-ID -> Befunde
    regeln: list[Regel] = field(default_factory=list)

    @property
    def machbar(self) -> bool:
        return self.harte_strafe < 1e-6

    @property
    def kosten(self) -> float:
        """Für den Optimierer: kleiner = besser."""
        return self.harte_strafe * 50 + (100 - self.score)


def bewerte(layout: Layout, gewichte: Optional[dict[str, float]] = None) -> Ergebnis:
    regeln = anwendbare_regeln(layout.raum.raumtyp)
    strafen, befunde = {}, {}
    weich_summe, weich_max, hart = 0.0, 0.0, 0.0
    for r in regeln:
        b = r.pruefe(layout)
        s = min(1.0, sum(x.strafe for x in b))
        strafen[r.id] = s
        befunde[r.id] = b
        w = (gewichte or {}).get(r.id, r.gewicht)
        if r.kategorie == "hart":
            hart += r.gewicht * s
        else:
            weich_summe += w * s
            weich_max += w
    # 0 Verstöße = 100 Punkte; je 5 gewichtete Strafpunkte halbiert sich der Score
    score = 100.0 / (1.0 + weich_summe / 5.0)
    return Ergebnis(score, hart, strafen, befunde, regeln)


def bericht(layout: Layout, erg: Optional[Ergebnis] = None, gewichte=None) -> str:
    erg = erg or bewerte(layout, gewichte)
    z = []
    z.append(f"=== Feng-Shui-Bewertung: {layout.raum.name} ({layout.raum.raumtyp}) ===")
    z.append(f"Score: {erg.score:.1f} / 100" + ("" if erg.machbar else "   ⚠ NICHT MACHBAR (harte Regeln verletzt)"))
    z.append("")
    z.append("Möbel:")
    for m in layout.moebel:
        z.append(f"  - {m.name:<16} x={m.x:5.2f}  y={m.y:5.2f}  Blick={_richtung(m.rot):<6} ({m.breite:.2f}×{m.tiefe:.2f} m)")
    z.append("")
    probleme = [(r, erg.befunde[r.id]) for r in erg.regeln if erg.befunde[r.id]]
    if not probleme:
        z.append("✓ Keine Regel verletzt.")
    else:
        z.append("Hinweise (nach Wichtigkeit):")
        probleme.sort(key=lambda rb: -(rb[0].gewicht * erg.strafen[rb[0].id]) - (100 if rb[0].kategorie == 'hart' else 0))
        for r, bs in probleme:
            z.append(f"  [{r.id}] {r.titel}  (Strafe {erg.strafen[r.id]:.2f}, Gewicht {r.gewicht})")
            for b in bs:
                z.append(f"        • {b.text}")
    erfuellt = [r for r in erg.regeln if not erg.befunde[r.id]]
    z.append("")
    z.append("Erfüllt: " + ", ".join(f"{r.id} {r.titel}" for r in erfuellt))
    return "\n".join(z)


def _richtung(rot: int) -> str:
    return {0: "oben", 90: "rechts", 180: "unten", 270: "links"}[rot % 360]
