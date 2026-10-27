"""
Ausführliche Analyse auf Basis der Buch-Regelbasis (buchregeln.py).

Für jeden Befund wird die passende Buchregel gezeigt:
    WENN (Situation) → DANN (Empfehlung) · WARUM (Begründung aus dem Buch) · ABHILFE
Dazu: Profil-Regeln (Farben, Licht, Bett …), Foto-Hinweise, was schon gut ist,
was sich nicht prüfen ließ, und eine Checkliste der übrigen Buch-Tipps für diesen Raum.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .bewertung import Ergebnis
from .buchregeln import BuchRegel, abdeckung, abgeleitetes_profil, pruefe_profil, regeln_fuer_raum, regeln_zu_pruefung
from .erklaerungen import FOTO_ERKLAERUNG, erklaerung
from .modell import Layout

KATEGORIE_NAME = {"hart": "Praktisch", "kommando": "Kommandoposition", "chi": "Chi-Fluss",
                  "zonen": "Zonen", "stil": "Gestaltung", "ausstattung": "Ausstattung"}
PRIO_SCHWERE = {1: 1.6, 2: 0.9, 3: 0.4}
NUR_WOHNUNG = {"wohnung", "garten", "balkon", "unterwegs"}

# Eine erfüllte Prüfung wird nur als "gut" gemeldet, wenn die betroffenen Möbel überhaupt da sind
BRAUCHT_MOEBEL = {
    "C05": [("bett", 1), ("schreibtisch", 1)], "G01": [("bett", 2)], "G02": [("bett", 2)], "G03": [("etagenbett", 1)],
    "C03": [("pflanze", 1)], "C02": [("spiegel", 1)], "C09": [("spiegel", 1)], "C10": [("windspiel", 1)],
    "C11": [("altar", 1)], "C04": [("tv", 1)], "C06": [("aquarium", 1)], "K13": [("schreibtisch", 1)],
    "K11": [("bett", 1)], "K17": [("bett", 1)], "S01": [("bett", 1)], "S04": [("esstisch", 1)], "S05": [("tv", 1)],
    "S06": [("sessel", 1)], "S07": [("tv", 1)], "S09": [("tv", 1), ("kamin", 1)], "W01": [("sofa", 2)],
    "W02": [("sofa", 1)], "W03": [("sofa", 1)], "B01": [("schreibtisch", 1), ("regal", 1)],
    "B02": [("schreibtisch", 2)], "B03": [("tagesbett", 1)], "E01": [("esstisch", 1)], "E02": [("stuhl", 1)],
    "E03": [("esstisch", 1)], "E04": [("esstisch", 1)], "E05": [("spiegel", 1)], "E06": [("uhr", 1)],
    "E07": [("bank", 1)], "L01": [("pendelleuchte", 1)], "L02": [("pendelleuchte", 1)], "KU1": [("herd", 1)],
    "KU2": [("herd", 1)], "KU3": [("herd", 1)], "KU4": [("spiegel", 1)], "KU5": [("herd", 1)],
    "BA1": [("wc", 1)], "BA2": [("wc", 1), ("badewanne", 1)], "BA3": [("badewanne", 1)], "BA4": [("waschbecken", 1)],
    "BA5": [("spiegel", 1)], "T01": [("kaefig", 1)], "T02": [("hundebox", 1)], "T03": [("katzenklo", 1)],
    "ST1": [("bett", 1), ("herd", 1)], "K08": [("balken", 0)], "K09": [("schraege", 0)],
}


@dataclass
class Problem:
    id: str
    titel: str
    kategorie: str
    schwere: float
    befunde: list[str]
    moebel: list[str]
    warum: str
    abhilfe: str
    buch: Optional[BuchRegel] = None
    geloest: bool = False
    loesung: str = ""
    umstellbar: bool = True
    weitere: list[str] = field(default_factory=list)

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
    foto_hinweise: list[tuple[str, str, str]] = field(default_factory=list)
    aenderungen: list[str] = field(default_factory=list)
    tipps: list[BuchRegel] = field(default_factory=list)
    infos: list[BuchRegel] = field(default_factory=list)
    statistik: dict = field(default_factory=dict)

    # -------------------------------------------------------------- Textbericht
    def text(self) -> str:
        z = [f"FENG-SHUI-ANALYSE ({self.raumtyp})", "=" * 64,
             f"Score vorher: {self.score_vorher:.0f}/100" +
             (f"   →   nachher: {self.score_nachher:.0f}/100" if self.score_nachher is not None else "")]
        if self.statistik:
            s = self.statistik
            z.append(f"Regelbasis: {s['gesamt_raum']} Buchregeln gelten für diesen Raum – "
                     f"{s['geprueft']} automatisch geprüft, {s['tipps']} als Tipp unten.")
        z.append("")
        if self.aenderungen:
            z.append("WAS UMGESTELLT WIRD")
            z += [f"  {a}" for a in self.aenderungen]
            z.append("")
        z.append("WAS NICHT GUT IST – UND WARUM (laut Buch)")
        if not self.probleme:
            z.append("  Keine Probleme gefunden.")
        for i, p in enumerate(self.probleme, 1):
            if p.geloest:
                status = "✔ gelöst" + (f" ({p.loesung})" if p.loesung else "")
            else:
                status = "✘ bleibt" + ("" if p.umstellbar else " (nicht durch Umstellen lösbar)")
            ref = f"{p.buch.id}" if p.buch else p.id
            z.append(f"  {i}. {p.stufe} · {p.titel}  [{KATEGORIE_NAME.get(p.kategorie, p.kategorie)}, {ref}]  {status}")
            for b in p.befunde[:4]:
                z.append(f"       – {b}")
            if p.buch:
                z.append(f"       Regel: WENN {p.buch.wenn} → DANN {p.buch.dann}")
            if p.warum:
                z.append(f"       Warum: {p.warum}")
            if p.abhilfe and not p.geloest and (not p.buch or p.abhilfe != p.buch.dann):
                z.append(f"       Was du tun kannst: {p.abhilfe}")
            if p.weitere:
                z.append(f"       Siehe auch: {', '.join(p.weitere)}")
            z.append("")
        if self.foto_hinweise:
            z.append("HINWEISE DIREKT AUS DEM FOTO")
            for stufe, t, w in self.foto_hinweise:
                z.append(f"  {stufe} {t}")
                if w:
                    z.append(f"       Warum: {w}")
            z.append("")
        if self.infos:
            z.append("ZU DEINEM RAUM")
            for r in self.infos:
                z.append(f"  ℹ [{r.id}] {r.wenn[:1].upper() + r.wenn[1:]} → {r.dann}")
                if r.warum:
                    z.append(f"       Warum: {r.warum}")
            z.append("")
        if self.gut:
            z.append("WAS SCHON GUT IST")
            z += [f"  ✓ {g}" for g in self.gut]
            z.append("")
        if self.nicht_pruefbar:
            z.append("NICHT PRÜFBAR")
            z += [f"  ? {n}" for n in self.nicht_pruefbar]
            z.append("")
        if self.tipps:
            z.append("DARAUF SOLLTEST DU AUCH ACHTEN (Tipps aus dem Buch für diesen Raum)")
            for r in self.tipps:
                z.append(f"  • [{r.id}] {r.thema}: WENN {r.wenn} → {r.dann}")
                if r.warum:
                    z.append(f"       Warum: {r.warum}")
        return "\n".join(z)

    def kurz(self, n: int = 7) -> list[str]:
        """Kurze Zeilen für die Grafik."""
        zeilen = []
        for p in self.probleme[:n]:
            zeichen = "✔" if p.geloest else "✘"
            w = p.warum.split(". ")[0].rstrip(".") + "." if p.warum else ""
            ref = p.buch.id if p.buch else p.id
            zeilen.append(f"{zeichen} [{ref}] {p.titel}: {p.befunde[0] if p.befunde else ''} — Warum: {w}")
        return zeilen


# ------------------------------------------------------------------ Hauptfunktion
def analysiere(ist: Layout, e_ist: Ergebnis, neu: Optional[Layout] = None, e_neu: Optional[Ergebnis] = None,
               aenderungen: Optional[list] = None, foto_hinweise: Optional[list] = None,
               profil: Optional[dict] = None, max_tipps: int = 12) -> Analyse:
    raum = ist.raum
    rt = raum.raumtyp
    a = Analyse(rt, e_ist.score, e_neu.score if e_neu else None)
    verschoben = {x.name: x for x in (aenderungen or [])}
    a.aenderungen = [x.text() + (f" – weil: {x.gruende[0]}" if x.gruende else "") for x in (aenderungen or [])]
    gedeckte_buchregeln: set[str] = set()

    # ---------- 1. Geometrische Befunde (Grundriss)
    for r in e_ist.regeln:
        bs = e_ist.befunde[r.id]
        if not bs:
            continue
        if r.id == "L03" and all(not b.moebel for b in bs):
            continue
        buch = regeln_zu_pruefung(r.id, rt)
        haupt = buch[0] if buch else None
        e = erklaerung(r.id)
        warum = haupt.warum if haupt and haupt.warum else e["warum"]
        abhilfe = haupt.abhilfe if haupt and haupt.abhilfe else e["abhilfe"]
        moebel = sorted({b.moebel for b in bs if b.moebel})
        p = Problem(r.id, r.titel, r.kategorie, r.gewicht * e_ist.strafen[r.id], [b.text for b in bs], moebel,
                    warum, abhilfe, haupt,
                    weitere=[f"{b.id} {b.thema}" for b in buch[1:]
                             if "alle" in b.raeume or b.id.split("-")[0] == (haupt.id.split("-")[0] if haupt else "")][:3])
        if e_neu is not None:
            rest = e_neu.strafen.get(r.id, 0.0)
            if rest < 0.05 or rest < 0.4 * e_ist.strafen[r.id]:
                p.geloest = True
                beteiligt = [m for m in moebel if m in verschoben]
                if beteiligt:
                    p.loesung = ", ".join(f"{m} umgestellt" for m in beteiligt)
        a.probleme.append(p)
        gedeckte_buchregeln.update(b.id for b in buch)

    # ---------- 2. Profil-Regeln (Farben, Licht, Bett, Ordnung …)
    offen_profil: list[BuchRegel] = []
    if profil is not None:
        verletzt, offen_profil = pruefe_profil(abgeleitetes_profil(profil, raum), rt)
        for br in verletzt:
            if br.id in gedeckte_buchregeln:
                continue
            gedeckte_buchregeln.add(br.id)
            if br.info:
                a.infos.append(br)
                continue
            a.probleme.append(Problem(br.id, br.thema, "ausstattung", PRIO_SCHWERE[br.prio],
                                      [br.wenn[:1].upper() + br.wenn[1:]], [], br.warum, br.abhilfe or br.dann, br,
                                      umstellbar=False))

    a.probleme.sort(key=lambda p: (p.geloest, -(p.kategorie == "hart"), -p.schwere))

    # ---------- 3. Was schon gut ist
    vorhanden = {m.typ for m in ist.moebel}
    for r in e_ist.regeln:
        if e_ist.befunde[r.id] or r.kategorie == "hart":
            continue
        buch = regeln_zu_pruefung(r.id, rt)
        if not buch:
            continue
        objekte = set(buch[0].objekte)
        if "tuer" in objekte and not raum.tueren:
            continue
        if "fenster" in objekte and not raum.fenster:
            continue
        from collections import Counter
        anzahl = Counter(m.typ for m in ist.moebel)
        if r.id == "K08" and not raum.balken:
            continue
        if r.id == "K09" and raum.schraege is None:
            continue
        if any(anzahl[t] < n for t, n in BRAUCHT_MOEBEL.get(r.id, []) if n > 0):
            continue
        relevante = objekte - {"tuer", "fenster", "wand", "ecken", "licht", "farben", "flur"}
        if relevante and not (relevante & vorhanden):
            continue
        a.gut.append(f"{r.titel} [{buch[0].id}]")

    # ---------- 4. Nicht prüfbar
    raumregeln = [r for r in regeln_fuer_raum(rt) if not (set(r.raeume) & NUR_WOHNUNG) or "alle" in r.raeume]
    if not raum.tueren:
        tuer_regeln = [r for r in raumregeln if "tuer" in r.objekte and r.art == "grundriss"]
        a.nicht_pruefbar.append(
            f"Keine Tür im Foto: {len(tuer_regeln)} Buchregeln zur Tür konnten nicht geprüft werden (z. B. "
            + ", ".join(f"{r.id} {r.thema}" for r in sorted(tuer_regeln, key=lambda r: r.prio)[:4])
            + "). Tipp: so fotografieren, dass die Tür zu sehen ist – oder aus der Tür heraus (foto_von_tuer).")
    if not raum.fenster:
        a.nicht_pruefbar.append("Kein Fenster erkannt: Regeln zu Fenster im Rücken / am Fußende nicht geprüft.")
    if "spiegel" not in vorhanden and rt in ("schlafzimmer", "gaestezimmer", "studio", "kinderzimmer"):
        a.nicht_pruefbar.append("Kein Spiegel im Bild: Falls es einen gibt (z. B. hinter der Kamera), prüfe selbst, "
                                "ob du dich vom Bett aus darin siehst (SZ-32).")
    if profil is not None and offen_profil:
        abgeleitet = {"elemente_fehlen": "wandfarbe", "wandfarbe_element": "wandfarbe", "hauptrichtung": "nord_wand"}
        schluessel = sorted({abgeleitet.get(k, k) for r in offen_profil for k, _, _ in r.profil})
        a.nicht_pruefbar.append(f"{len(offen_profil)} Ausstattungs-Regeln brauchen noch Angaben im PROFIL – z. B. "
                                f"{', '.join(schluessel[:8])} (alle Felder: siehe mein_zimmer.py).")

    # ---------- 5. Foto-Hinweise
    for stufe, regel, text in (foto_hinweise or []):
        if regel in ("F99", "F00"):
            continue
        a.foto_hinweise.append((stufe, text, FOTO_ERKLAERUNG.get(regel, "")))

    # ---------- 6. Checkliste: übrige Buch-Tipps für diesen Raum (wichtigste zuerst, raumspezifische vor allgemeinen)
    tipps = [r for r in raumregeln if r.art == "tipp" and r.id not in gedeckte_buchregeln and r.prio <= 2]
    tipps.sort(key=lambda r: ("alle" in r.raeume, r.prio, r.id))
    a.tipps = tipps[:max_tipps]

    ab = abdeckung()
    a.statistik = {"gesamt_raum": len(raumregeln),
                   "geprueft": len([r for r in raumregeln if r.art != "tipp"]),
                   "tipps": len([r for r in raumregeln if r.art == "tipp"]),
                   "gesamt_buch": ab["gesamt"]}
    return a
