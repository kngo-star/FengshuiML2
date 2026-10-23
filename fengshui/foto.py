"""
Foto-Analyse: Möbel in einem Zimmerfoto mit YOLO erkennen → Feng-Shui-Empfehlungen.

Unterstützte Modelle (Paket `ultralytics`):
  • YOLOE (Standard) bzw. YOLO-World – "open vocabulary": erkennen beliebige Begriffe wie
    "wardrobe", "mirror", "window", "nightstand" … – ideal für Einrichtung.
  • normales YOLO (COCO, 80 Klassen): kennt bed, couch, chair, tv, potted plant,
    clock, laptop … aber KEINE Schränke, Spiegel, Fenster, Türen.

WICHTIG – was ein Foto kann und was nicht:
  Ein einzelnes Foto ist 2D. Es zeigt, WELCHE Dinge im Raum sind und wie sie im Bild
  zueinander liegen (z.B. Regal über dem Bett, Spiegel neben dem Bett). Es liefert
  aber keine Maße und keinen Grundriss. Daher:
    1. Foto-Regeln (F..) geben direkte Hinweise – als "wahrscheinlich, bitte prüfen".
    2. Die erkannten Möbel werden in eine Möbelliste (Standardmaße) umgewandelt,
       die zusammen mit deinen Raummaßen in den Optimierer geht.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Optional

from .modell import Moebel

# ------------------------------------------------------------------ Klassen-Zuordnung
# YOLO-World-Prompt (englisch)  ->  interner Typ
WORLD_KLASSEN = {
    "bed": "bett",
    "nightstand": "nachttisch",
    "desk": "schreibtisch",
    "office chair": "stuhl",
    "chair": "stuhl",
    "sofa": "sofa",
    "armchair": "sessel",
    "coffee table": "couchtisch",
    "dining table": "esstisch",
    "wardrobe": "schrank",
    "dresser": "kommode",
    "bookshelf": "regal",
    "wall shelf": "wandregal",
    "mirror": "spiegel",
    "picture frame": "bild",
    "window": "fenster",
    "door": "tuer",
    "potted plant": "pflanze",
    "cactus": "kaktus",
    "television": "tv",
    "computer monitor": "bildschirm",
    "laptop": "bildschirm",
    "cell phone": "handy",
    "ceiling lamp": "pendelleuchte",
    "ceiling fan": "ventilator",
    "floor lamp": "stehleuchte",
    "table lamp": "tischleuchte",
    "clock": "uhr",
    "aquarium": "aquarium",
    "rug": "teppich",
    "pile of clothes": "kleidung",
    "cardboard box": "karton",
    "book": "buch",
    "bottle": "kleinkram",
    "cup": "kleinkram",
    "bag": "kleinkram",
    "shoe": "kleinkram",
}

# COCO-Klassen (normales YOLO)  ->  interner Typ
COCO_KLASSEN = {
    "bed": "bett", "couch": "sofa", "chair": "stuhl", "dining table": "esstisch", "potted plant": "pflanze",
    "tv": "tv", "laptop": "bildschirm", "keyboard": "bildschirm", "mouse": "kleinkram", "cell phone": "handy",
    "clock": "uhr", "vase": "vase", "book": "buch", "bottle": "kleinkram", "cup": "kleinkram",
    "backpack": "kleinkram", "handbag": "kleinkram", "suitcase": "kleinkram", "remote": "kleinkram",
    "refrigerator": "kuehlschrank", "oven": "herd", "microwave": "mikrowelle", "sink": "spuele", "toilet": "wc",
}

# Klassen, die oft verwechselt werden (Kamin -> TV, Tischlampe -> Hängelampe …), brauchen mehr Sicherheit
MIN_CONF = {"tv": 0.35, "pendelleuchte": 0.35, "ventilator": 0.4, "aquarium": 0.4, "uhr": 0.35,
            "kaktus": 0.4, "handy": 0.35, "tuer": 0.3, "fenster": 0.25}

KLEINKRAM = {"kleinkram", "buch", "kleidung", "karton"}
LAMPEN = {"pendelleuchte", "stehleuchte", "tischleuchte"}
BILDSCHIRME = {"tv", "bildschirm", "handy"}

# Standardmaße für die Umwandlung in eine Möbelliste (breite, tiefe, hoehe)
STANDARD_MASSE = {
    "bett": (1.4, 2.0, 0.5), "nachttisch": (0.45, 0.4, 0.5), "schreibtisch": (1.2, 0.6, 0.75),
    "sofa": (2.0, 0.9, 0.85), "sessel": (0.8, 0.8, 0.9), "couchtisch": (1.0, 0.6, 0.4),
    "esstisch": (1.4, 0.9, 0.75), "schrank": (1.5, 0.6, 2.1), "kommode": (1.0, 0.45, 0.85),
    "regal": (0.8, 0.35, 1.8), "wandregal": (0.8, 0.25, 0.3), "spiegel": (0.6, 0.04, 1.6),
    "bild": (0.7, 0.03, 0.5), "pflanze": (0.45, 0.45, 1.0), "kaktus": (0.3, 0.3, 0.6),
    "tv": (1.4, 0.45, 0.6), "aquarium": (0.8, 0.4, 1.2), "teppich": (2.0, 1.4, 0.01),
}


@dataclass
class Erkennung:
    typ: str            # interner Typ (bett, schrank, …)
    label: str          # Originallabel des Modells
    conf: float
    box: tuple[float, float, float, float]   # x1, y1, x2, y2 in Pixeln (y nach unten)

    def norm(self, w: int, h: int) -> tuple[float, float, float, float]:
        x1, y1, x2, y2 = self.box
        return (x1 / w, y1 / h, x2 / w, y2 / h)


@dataclass
class FotoHinweis:
    stufe: str          # "✗" Problem | "!" bitte prüfen | "✓" gut | "ℹ" Info
    regel: str
    text: str


# ------------------------------------------------------------------ Erkennung
def erkenne(bild: str, modell: str = "yoloe-11s-seg.pt", conf: float = 0.2,
            iou_dedupe: float = 0.6) -> tuple[list[Erkennung], tuple[int, int]]:
    """Führt YOLO auf einem Foto aus. Gibt (Erkennungen, (Breite, Höhe)) zurück.

    modell:
      "yoloe-11s-seg.pt" / "yoloe-11m-seg.pt"  -> YOLOE, Text-Prompts (Standard, empfohlen)
      "yolov8s-world.pt"                       -> YOLO-World, Text-Prompts (braucht CLIP-Download)
      "yolo11n.pt" / "yolov8n.pt" usw.         -> COCO-Modell (80 feste Klassen, kein Schrank/Spiegel/Fenster)
      eigener Pfad "best.pt"                   -> selbst trainiertes Modell (Labels = Typnamen oder WORLD_KLASSEN)
    Falls das Text-Prompt-Modell nicht lädt, wird automatisch auf yolo11n.pt (COCO) ausgewichen.
    """
    from ultralytics import YOLO

    prompts = list(WORLD_KLASSEN)
    name = modell.lower()
    try:
        if "yoloe" in name:
            from ultralytics import YOLOE
            m = YOLOE(modell)
            m.set_classes(prompts, m.get_text_pe(prompts))
            zuordnung = WORLD_KLASSEN
        elif "world" in name:
            from ultralytics import YOLOWorld
            m = YOLOWorld(modell)
            m.set_classes(prompts)
            zuordnung = WORLD_KLASSEN
        else:
            m = YOLO(modell)
            zuordnung = {**COCO_KLASSEN, **WORLD_KLASSEN}
    except Exception as fehler:          # z.B. kein Internet für Text-Encoder
        print(f"⚠ {modell} konnte nicht geladen werden ({fehler.__class__.__name__}) – nutze yolo11n.pt (COCO).")
        m = YOLO("yolo11n.pt")
        zuordnung = {**COCO_KLASSEN, **WORLD_KLASSEN}

    res = m.predict(bild, conf=conf, verbose=False)[0]
    h, w = res.orig_shape
    erg: list[Erkennung] = []
    for b in res.boxes:
        label = res.names[int(b.cls)]
        typ = zuordnung.get(label, label if label in STANDARD_MASSE else None)
        if typ is None:
            continue
        if float(b.conf) < max(conf, MIN_CONF.get(typ, 0.0)):
            continue
        x1, y1, x2, y2 = (float(v) for v in b.xyxy[0].tolist())
        erg.append(Erkennung(typ, label, float(b.conf), (x1, y1, x2, y2)))
    return _dedupe(erg, iou_dedupe), (w, h)


def _iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def _dedupe(erg: list[Erkennung], schwelle: float) -> list[Erkennung]:
    """Doppelte Boxen gleichen Typs (z.B. 'chair' + 'office chair') zusammenfassen."""
    erg = sorted(erg, key=lambda e: -e.conf)
    behalten: list[Erkennung] = []
    for e in erg:
        if all(not (e.typ == k.typ and _iou(e.box, k.box) > schwelle) for k in behalten):
            behalten.append(e)
    return behalten


def speichere_erkennungen(erk: list[Erkennung], groesse: tuple[int, int], pfad: str) -> None:
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump({"groesse": groesse, "erkennungen": [asdict(e) for e in erk]}, f, indent=2, ensure_ascii=False)


def lade_erkennungen(pfad: str) -> tuple[list[Erkennung], tuple[int, int]]:
    with open(pfad, encoding="utf-8") as f:
        d = json.load(f)
    return [Erkennung(e["typ"], e["label"], e["conf"], tuple(e["box"])) for e in d["erkennungen"]], tuple(d["groesse"])


# ------------------------------------------------------------------ Bild-Geometrie (normiert 0..1, y nach unten)
def _h_ueberlapp(a, b) -> float:
    """Horizontale Überlappung relativ zur schmaleren Box."""
    ov = min(a[2], b[2]) - max(a[0], b[0])
    return max(0.0, ov) / max(1e-6, min(a[2] - a[0], b[2] - b[0]))


def _ueber(a, b, toleranz: float = 0.05) -> bool:
    """a liegt im Bild oberhalb von b (Unterkante a über Oberkante b)."""
    return a[3] <= b[1] + toleranz


def _h_abstand(a, b) -> float:
    return max(0.0, max(a[0], b[0]) - min(a[2], b[2]))


# ------------------------------------------------------------------ Foto-Regeln
def foto_empfehlungen(erk: list[Erkennung], groesse: tuple[int, int], raumtyp: str = "schlafzimmer") -> list[FotoHinweis]:
    w, h = groesse
    n = {e.typ: [] for e in erk}
    for e in erk:
        n[e.typ].append(e.norm(w, h))
    anz = Counter(e.typ for e in erk)
    schlaf = raumtyp in ("schlafzimmer", "gaestezimmer", "studio")
    H: list[FotoHinweis] = []

    def add(stufe, regel, text):
        H.append(FotoHinweis(stufe, regel, text))

    betten = n.get("bett", [])
    sitz = betten + n.get("sofa", []) + n.get("schreibtisch", [])

    # F01 Bildschirme / Elektronik
    bs = sum(anz[t] for t in BILDSCHIRME)
    if schlaf and bs:
        add("✗", "F01", f"{bs} Bildschirm(e)/Elektronik im Schlafzimmer erkannt (TV, Monitor, Laptop, Handy). "
                        "Möglichst raus; sonst nachts ausschalten und abdecken (glänzend schwarz wirkt wie ein Spiegel).")

    # F02 Spiegel
    for sp in n.get("spiegel", []):
        if schlaf:
            add("!", "F02", "Spiegel im Schlafzimmer: Prüfe, ob du dich vom Bett aus siehst – wenn ja, umhängen "
                            "oder abdecken. Nie am Fußende.")
        for b in betten:
            if _h_abstand(sp, b) < 0.08 or _h_ueberlapp(sp, b) > 0.3:
                add("✗", "F02", "Spiegel hängt direkt beim/über dem Bett – Spiegel wirken wie Türen und bringen Unruhe.")
                break

    # F03 Regale über dem Bett / Schreibtisch
    for r in n.get("wandregal", []) + n.get("regal", []):
        for b in betten:
            if _h_ueberlapp(r, b) > 0.3 and _ueber(r, b):
                add("✗", "F03", "Regal über dem Bett erkannt – wie eine Klinge über dem Kopf. Bitte abmontieren/versetzen.")
        for d in n.get("schreibtisch", []):
            if _h_ueberlapp(r, d) > 0.3 and _ueber(r, d) and (r[3] - r[1]) < 0.25:
                add("!", "F03", "Wandregal über dem Schreibtisch – wirkt bedrückend; besser hinter oder neben dich.")

    # F04 Bilder über dem Bett
    for bi in n.get("bild", []):
        for b in betten:
            if _h_ueberlapp(bi, b) > 0.3 and _ueber(bi, b):
                add("!", "F04", "Bild über dem Bett: nur leichte Bilder/Textilien, keine schweren Rahmen mit Glas.")

    # F05 Leuchten / Ventilator über Bett oder Sitzplatz
    for l in n.get("pendelleuchte", []) + n.get("ventilator", []):
        for s in sitz:
            if _h_ueberlapp(l, s) > 0.4 and _ueber(l, s, 0.0) and l[1] < 0.3:
                add("!", "F05", "Hängeleuchte/Ventilator scheint über Bett bzw. Sitzplatz zu hängen – "
                                "nichts Schweres über dem Kopf (leichte Papierleuchte ist ok).")
                break

    # F06 Fenster hinter dem Bett
    for f in n.get("fenster", []):
        for b in betten:
            if _h_ueberlapp(f, b) > 0.5 and _ueber(f, b, 0.12) and b[1] - f[3] < 0.15:
                add("!", "F06", "Fenster direkt über/hinter dem Bett: Falls das Kopfteil am Fenster steht → umstellen; "
                                "sonst massives Kopfteil, Brüstung höher als Kopfteil, schwere Vorhänge.")

    # F07 Tür in Bettachse
    for t in n.get("tuer", []):
        for b in betten:
            mx = (t[0] + t[2]) / 2
            if b[0] < mx < b[2]:
                add("!", "F07", "Tür liegt im Bild in Linie mit dem Bett – prüfe, dass die Füße nicht direkt zur Tür zeigen.")

    # F08 Pflanzen
    pfl = n.get("pflanze", [])
    for p in pfl:
        if schlaf:
            nah = any(_h_abstand(p, b) < 0.05 for b in betten)
            add("✗" if nah else "!", "F08", "Pflanze " + ("direkt am Bett" if nah else "im Schlafzimmer") +
                ": im Schlafzimmer möglichst keine – wenn doch, als Gruppe direkt ans Fenster, weit weg vom Bett.")
        fenster = n.get("fenster", [])
        if fenster and all(_h_abstand(p, f) > 0.15 for f in fenster):
            add("!", "F08", "Pflanze steht weit vom Fenster – braucht Licht (eine tote Pflanze ist schlechter als keine).")
    if anz["kaktus"]:
        add("✗", "F08", "Kaktus erkannt: stachelig, steht für unwirtliches Klima – nicht in die Wohnung (draußen ok).")
    if raumtyp in ("wohnzimmer", "buero", "esszimmer") and not pfl:
        add("ℹ", "F08", "Keine Pflanze erkannt: Ein paar großblättrige Pflanzen (Monstera, Geldbaum) nahe dem Fenster "
                        "bringen Leben (Holz-Element).")

    # F09 Unordnung / untere-Drittel-Regel
    klein = [e for e in erk if e.typ in KLEINKRAM]
    if len(klein) >= 6:
        add("✗", "F09", f"{len(klein)} lose Gegenstände (Kleidung, Kartons, Flaschen, Bücher …) erkannt – Unordnung "
                        "blockiert Chi. Kategorien bilden und alles verstauen.")
    oben = [e for e in klein if e.norm(w, h)[3] < 0.4]
    if len(oben) >= 2:
        add("!", "F09", "Stauraum/Gegenstände im oberen Bildbereich – untere Drittel = Stauraum, obere zwei Drittel "
                        "frei für Deko.")
    if anz["kleidung"]:
        add("✗", "F09", "Kleidung liegt herum – Schrank ordentlich, nicht vollstopfen; Bett morgens machen.")

    # F10 Uhr
    if anz["uhr"] and raumtyp in ("schlafzimmer", "esszimmer", "gaestezimmer"):
        add("✗", "F10", "Uhr erkannt – im Schlaf- und Esszimmer erzeugt sie Zeitdruck.")

    # F11 Aquarium
    if anz["aquarium"] and schlaf:
        add("✗", "F11", "Aquarium im Schlafzimmer = viel Yang/Wasser – besser ins Wohnzimmer oder Büro.")

    # F12 Schreibtisch vor dem Fenster
    for d in n.get("schreibtisch", []):
        for f in n.get("fenster", []):
            if _h_ueberlapp(f, d) > 0.5 and _ueber(f, d, 0.15):
                add("!", "F12", "Schreibtisch steht wohl direkt vor dem Fenster – Blendung/Ablenkung. Ideal: Fenster seitlich, "
                                "Wand im Rücken, Tür im Blick.")
    if schlaf and n.get("schreibtisch") and betten:
        d, b = n["schreibtisch"][0], betten[0]
        if _h_abstand(d, b) < 0.05:
            add("!", "F13", "Schreibtisch direkt neben dem Bett – Zonen trennen (Arbeiten näher zur Tür, Schlafen hinten).")

    # F14 Nachttische
    if betten:
        nt = anz["nachttisch"]
        if nt == 0:
            add("ℹ", "F14", "Keine Nachttische erkannt – ein Paar mit gleichem visuellem Gewicht (rund oder niedriger als "
                            "die Matratze) stabilisiert das Bett.")
        elif nt == 1:
            add("!", "F14", "Nur ein Nachttisch – für Balance (und Offenheit für einen Partner) auf beiden Seiten einen.")
        else:
            add("✓", "F14", "Nachttische auf beiden Seiten – gut.")

    # F15 hohe Regale
    for r in n.get("regal", []):
        if r[3] - r[1] > 0.55:
            add("!", "F15", "Hohes (offenes) Regal – offene Regale erzeugen aggressives Chi; besser niedrig oder mit Türen.")

    # F16 Licht
    lampen = sum(anz[t] for t in LAMPEN)
    if lampen < 2:
        add("ℹ", "F16", f"{lampen} Lampe(n) erkannt – besser mehrere niedrige Lichtquellen (3 von 4 Ecken), "
                        "gleiche Farbtemperatur ~2700 K" + (", im Schlafzimmer diffus" if schlaf else "") + ".")

    # F17 mehrere Schränke
    if anz["schrank"] >= 2:
        add("!", "F17", "Mehrere Schränke = viele Ecken. Ein großer bzw. Einbauschrank wirkt ruhiger.")

    # F18 Wohnzimmer: Sitzkreis / TV
    if raumtyp in ("wohnzimmer", "studio") and n.get("sofa"):
        if not anz["couchtisch"]:
            add("!", "F18", "Kein Couchtisch erkannt – er verankert den Raum und verbindet die Sitzplätze.")
        if not anz["sessel"]:
            add("ℹ", "F18", "Sofa allein – mit Sessel oder Hocker zum geschlossenen Sitzkreis ergänzen (Sessel zum Sofa drehen).")
        for tv in n.get("tv", []):
            mx = (tv[0] + tv[2]) / 2
            if 0.33 < mx < 0.66 and (tv[2] - tv[0]) > 0.2:
                add("!", "F18", "Fernseher steht prominent in der Bildmitte – lieber in eine Ecke, niedrig, nicht über Kamin.")

    # F19 Esstisch: gerade Stuhlanzahl
    if n.get("esstisch") and raumtyp in ("esszimmer", "wohnzimmer", "studio"):
        st = anz["stuhl"]
        if st % 2 == 1:
            add("!", "F19", f"{st} Stühle erkannt – gerade Anzahl, alle gleich, keiner an den Tischecken.")

    if betten and not any(x.stufe == "✗" for x in H):
        add("✓", "F00", "Keine groben Probleme im Bild erkannt.")
    add("ℹ", "F99", "Foto-Hinweise sind Schätzungen aus 2D-Bildlage. Für Kommandoposition, Türlinie und Chi-Bahn "
                    "Raummaße in mein_zimmer.py eintragen und den Optimierer laufen lassen.")
    return H


# ------------------------------------------------------------------ Brücke zum Optimierer
def zu_moebelliste(erk: list[Erkennung]) -> list[Moebel]:
    """Erkannte Möbel -> Moebel-Objekte mit Standardmaßen (bitte nachmessen und anpassen!)."""
    liste: list[Moebel] = []
    zaehler = Counter()
    betten, sofas = [], []
    for e in sorted(erk, key=lambda e: e.typ != "bett" and e.typ != "sofa"):
        if e.typ not in STANDARD_MASSE or e.typ in ("teppich",):
            continue
        zaehler[e.typ] += 1
        b, t, hh = STANDARD_MASSE[e.typ]
        name = e.typ.capitalize() + (f" {zaehler[e.typ]}" if zaehler[e.typ] > 1 else "")
        m = Moebel(e.typ, b, t, hh, name=name, rund=e.typ in ("pflanze", "kaktus"))
        if e.typ == "bett":
            betten.append(m)
        if e.typ == "sofa":
            sofas.append(m)
        if e.typ == "nachttisch" and betten:
            m.gehoert_zu = betten[0].name
            m.seite = "links" if zaehler["nachttisch"] % 2 == 1 else "rechts"
        if e.typ == "couchtisch" and sofas:
            m.gehoert_zu, m.seite, m.abstand = sofas[0].name, "vorne", 0.45
        liste.append(m)
    return liste


def zu_profil(erk: list[Erkennung], raumtyp: str = "schlafzimmer") -> dict:
    """Teil-Profil für den Ausstattungs-Check aus den Erkennungen."""
    anz = Counter(e.typ for e in erk)
    return {
        "computer_im_raum": anz["bildschirm"] + anz["tv"] > 0,
        "smartphone_am_bett": anz["handy"] > 0,
        "uhr_im_raum": anz["uhr"] > 0,
        "anzahl_lichtquellen": sum(anz[t] for t in LAMPEN),
        "unordnung": sum(anz[t] for t in KLEINKRAM) >= 6,
        "kleiderschrank": "mehrere" if anz["schrank"] >= 2 else ("freistehend" if anz["schrank"] else None),
        "pflanzenarten": (["kaktus"] if anz["kaktus"] else []),
    }


# ------------------------------------------------------------------ Ausgabe
FARBE = {"✗": (214, 40, 40), "!": (244, 162, 97), "✓": (42, 157, 143), "ℹ": (100, 100, 100)}


def zeichne_erkennungen(bild: str, erk: list[Erkennung], ziel: str) -> None:
    from PIL import Image, ImageDraw
    img = Image.open(bild).convert("RGB")
    d = ImageDraw.Draw(img)
    st = max(2, img.width // 400)
    for e in erk:
        farbe = (42, 157, 143) if e.typ in ("bett", "sofa", "schreibtisch") else (231, 111, 81)
        d.rectangle(e.box, outline=farbe, width=st)
        txt = f"{e.typ} {e.conf:.2f}"
        x, y = e.box[0], max(0, e.box[1] - 14 * st // 2 - 4)
        d.rectangle((x, y, x + 7 * len(txt) * st // 2 + 6, y + 14 * st // 2 + 4), fill=farbe)
        d.text((x + 3, y + 2), txt, fill=(255, 255, 255))
    img.save(ziel)


def text_bericht(erk: list[Erkennung], hinweise: list[FotoHinweis]) -> str:
    z = ["=== Foto-Analyse ===", "Erkannt: " + ", ".join(f"{k}×{v}" for k, v in Counter(e.typ for e in erk).most_common()), ""]
    reihenfolge = {"✗": 0, "!": 1, "ℹ": 2, "✓": 3}
    for x in sorted(hinweise, key=lambda x: reihenfolge[x.stufe]):
        z.append(f"  {x.stufe} [{x.regel}] {x.text}")
    return "\n".join(z)
