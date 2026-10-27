"""
Ausführliche Analyse: Was ist nicht gut, WARUM (laut Buch), was wurde korrigiert,
was kannst du sonst tun – und was ließ sich aus dem Foto gar nicht prüfen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .bewertung import Ergebnis
from .erklaerungen import BRAUCHT, FOTO_ERKLAERUNG, erklaerung
from .modell import Layout

KATEGORIE_NAME = {"hart": "Praktisch", "kommando": "Kommandoposition", "chi": "Chi-Fluss",
                  "zonen": "Zonen", "stil": "Gestaltung"}


@dataclass
class Problem:
    id: str
    titel: str
    kategorie: str
    schwere: float                  # Gewicht × Strafe
    befunde: list[str]
    moebel: list[str]
    warum: str
    abhilfe: str
    geloest: bool = False
    loesung: str = ""

    @property
    def stufe(self) -> str:
        return "🔴 wichtig" if self.schwere >= 1.5 else ("🟠 mittel" if self.schwere >= 0.6 else "🟡 klein")


@dataclass
class Analyse:
    raumtyp: str
    score_vorher: float
    score_nachher: Optional[float]
    probleme: list[Problem] = field(default_factory=list)
    gut: list[str] = field(default_factory=list)
    nicht_pruefbar: list[str] = field(default_factory=list)
    foto_hinweise: list[tuple[str, str, str]] = field(default_factory=list)   # (stufe, text, warum)
    aenderungen: list[str] = field(default_factory=list)

    def text(self) -> str:
        z = [f"FENG-SHUI-ANALYSE ({self.raumtyp})",
             "=" * 60,
             f"Score vorher: {self.score_vorher:.0f}/100" +
             (f"   →   nachher: {self.score_nachher:.0f}/100" if self.score_nachher is not None else ""), ""]
        if self.aenderungen:
            z.append("WAS UMGESTELLT WIRD")
            z += [f"  {a}" for a in self.aenderungen]
            z.append("")
        z.append("WAS NICHT GUT IST – UND WARUM")
        if not self.probleme:
            z.append("  Keine Probleme gefunden.")
        for i, p in enumerate(self.probleme, 1):
            status = "✔ gelöst" + (f" ({p.loesung})" if p.loesung else "") if p.geloest else "✘ bleibt"
            z.append(f"  {i}. {p.stufe} · {p.titel}  [{KATEGORIE_NAME.get(p.kategorie, p.kategorie)}, {p.id}]  {status}")
            for b in p.befunde[:4]:
                z.append(f"       – {b}")
            if p.warum:
                z.append(f"       Warum: {p.warum}")
            if p.abhilfe and not p.geloest:
                z.append(f"       Was du tun kannst: {p.abhilfe}")
            z.append("")
        if self.foto_hinweise:
            z.append("HINWEISE DIREKT AUS DEM FOTO")
            for stufe, t, w in self.foto_hinweise:
                z.append(f"  {stufe} {t}")
                if w:
                    z.append(f"       Warum: {w}")
            z.append("")
        if self.gut:
            z.append("WAS SCHON GUT IST")
            z += [f"  ✓ {g}" for g in self.gut]
            z.append("")
        if self.nicht_pruefbar:
            z.append("NICHT PRÜFBAR (im Foto nicht zu sehen)")
            z += [f"  ? {n}" for n in self.nicht_pruefbar]
        return "\n".join(z)

    def kurz(self, n: int = 6) -> list[str]:
        """Kurze Zeilen für die Grafik."""
        zeilen = []
        for p in self.probleme[:n]:
            zeichen = "✔" if p.geloest else "✘"
            w = p.warum.split(". ")[0].rstrip(".") + "." if p.warum else ""
            zeilen.append(f"{zeichen} {p.titel}: {p.befunde[0] if p.befunde else ''} — Warum: {w}")
        return zeilen


def analysiere(ist: Layout, e_ist: Ergebnis, neu: Optional[Layout] = None, e_neu: Optional[Ergebnis] = None,
               aenderungen: Optional[list] = None, foto_hinweise: Optional[list] = None) -> Analyse:
    raum = ist.raum
    a = Analyse(raum.raumtyp, e_ist.score, e_neu.score if e_neu else None)
    verschoben = {x.name: x for x in (aenderungen or [])}
    a.aenderungen = [x.text() + (f" – weil: {x.gruende[0]}" if x.gruende else "") for x in (aenderungen or [])]

    for r in e_ist.regeln:
        bs = e_ist.befunde[r.id]
        if not bs:
            continue
        # konstante Hinweise ohne Möbelbezug (z. B. "keine Lampen eingetragen") nur einmal, nicht als Problem führen
        if r.id == "L03" and all(not b.moebel for b in bs):
            continue
        e = erklaerung(r.id)
        moebel = sorted({b.moebel for b in bs if b.moebel})
        p = Problem(r.id, r.titel, r.kategorie, r.gewicht * e_ist.strafen[r.id], [b.text for b in bs], moebel,
                    e["warum"], e["abhilfe"])
        if e_neu is not None:
            rest = e_neu.strafen.get(r.id, 0.0)
            if rest < 0.05 or rest < 0.4 * e_ist.strafen[r.id]:
                p.geloest = True
                beteiligt = [m for m in moebel if m in verschoben]
                if beteiligt:
                    p.loesung = ", ".join(f"{m} umgestellt" for m in beteiligt)
        a.probleme.append(p)
    a.probleme.sort(key=lambda p: (-(p.kategorie == "hart"), -p.schwere))

    # Was schon gut ist: erfüllte Regeln, die für vorhandene Möbel wirklich etwas aussagen
    vorhanden = {m.typ for m in ist.moebel}
    wichtig = ["K01", "K02", "K03", "K04", "K06", "K07", "K08", "K14", "C01", "C02", "C03", "C04", "S01",
               "K12", "K13", "C05", "L01", "S06", "E04", "BA1", "KU1", "KU2"]
    for rid in wichtig:
        r = next((r for r in e_ist.regeln if r.id == rid), None)
        if r is None or e_ist.befunde[rid]:
            continue
        if rid in BRAUCHT["tuer"] and not raum.tueren:
            continue
        if rid in BRAUCHT["fenster"] and not raum.fenster:
            continue
        if rid == "C02" and "spiegel" not in vorhanden:
            continue
        if rid == "C03" and "pflanze" not in vorhanden:
            continue
        if rid in ("K13", "C05") and "schreibtisch" not in vorhanden:
            continue
        a.gut.append(f"{r.titel}")

    # Was sich nicht prüfen ließ
    if not raum.tueren:
        a.nicht_pruefbar.append("Keine Tür im Foto: Tür im Blick, Füße zur Tür, Bett neben der Tür, Chi-Bahn "
                                "Tür↔Fenster konnten NICHT geprüft werden. Tipp: so fotografieren, dass die Tür "
                                "zu sehen ist – oder aus der Tür heraus fotografieren (Option 'foto_von_tuer').")
    if not raum.fenster:
        a.nicht_pruefbar.append("Kein Fenster erkannt: Fenster im Rücken / am Fußende nicht geprüft.")
    if "spiegel" not in vorhanden:
        a.nicht_pruefbar.append("Kein Spiegel im Foto: Falls es einen gibt (z. B. hinter der Kamera), prüfe "
                                "selbst, ob du dich vom Bett aus darin siehst.")
    for stufe, regel, text in (foto_hinweise or []):
        if regel in ("F99", "F00"):
            continue
        a.foto_hinweise.append((stufe, text, FOTO_ERKLAERUNG.get(regel, "")))
    return a
