"""
Zimmer automatisch aus EINEM Foto vermessen – ohne Meter-Eingabe.

Pipeline
--------
1. Tiefenkarte: "Depth Anything V2 – Metric Indoor" schätzt für jedes Pixel die
   Entfernung in METERN (trainiert auf Innenräumen).
2. Kamera: Brennweite aus den EXIF-Daten des Fotos (oder Standard-Blickwinkel).
3. 3D-Punktwolke: jedes Pixel wird mit Tiefe + Brennweite in 3D zurückprojiziert.
4. Boden: RANSAC sucht die größte waagerechte Ebene unten im Bild.
5. Wände: Punkte zwischen 0,4 m und 2 m Höhe (ohne Möbel) werden auf den Boden
   projiziert; die Ausrichtung der Wände wird gesucht, die Wandlinien als
   Häufungen ("Peaks") gefunden → Raumbreite und -tiefe.
6. Möbel: YOLOE-Masken × Punktwolke → Grundfläche, Höhe, Wand im Rücken.
   Türen/Fenster → Wand, Position, Breite, Brüstung.
7. Ergebnis: Raum + Möbel mit Positionen (deine JETZIGE Einrichtung) →
   direkt bewertbar und optimierbar.

Grenzen (ehrlich):
  • Genauigkeit typischerweise ±10–20 cm, bei schwierigen Fotos mehr.
  • Ein Foto sieht nur einen Teil des Raums. Wände HINTER der Kamera werden
    geschätzt (Option `kamera_in_ecke=True`: du stehst beim Fotografieren in einer Ecke).
  • Verdeckte Möbel und verdeckte Rückseiten werden mit Standardmaßen ergänzt.
  Darum: Ergebnis kurz prüfen; einzelne Werte kannst du jederzeit überschreiben.

Bestes Foto: aus einer Zimmerecke diagonal in die gegenüberliegende Ecke,
Weitwinkel (0,5×), Handy auf Brusthöhe, möglichst gerade gehalten, Raum hell,
die Tür im Bild oder direkt hinter dir.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .foto import STANDARD_MASSE, Erkennung
from .modell import ROT_VEKTOR, VEKTOR_ROT, WAND_NORMALE, Bewohner, Layout, Moebel, Oeffnung, Raum

TIEFENMODELL = "depth-anything/Depth-Anything-V2-Metric-Indoor-Base-hf"

WANDOBJEKTE_FOTO = {"tuer", "fenster", "spiegel", "bild", "wandregal", "uhr"}
BODENMOEBEL = {"bett", "nachttisch", "schreibtisch", "sofa", "sessel", "couchtisch", "esstisch", "schrank",
               "kommode", "regal", "pflanze", "kaktus", "tv", "aquarium", "stuhl"}
NICHT_ALS_MOEBEL = {"stuhl"}       # Stühle gehören zum Tisch, nicht in die Möbelliste
STANDARD_TUER_HOEHE = 2.0


# ====================================================================== Kamera
@dataclass
class Kamera:
    fx: float
    fy: float
    cx: float
    cy: float
    breite: int
    hoehe: int


def kamera_aus_foto(pfad: str, fov_grad: Optional[float] = None) -> tuple["Kamera", np.ndarray]:
    """Lädt das Foto (EXIF-Drehung korrigiert) und schätzt die Brennweite in Pixeln.
    Auch iPhone-Fotos (HEIC), wenn `pillow-heif` installiert ist."""
    from PIL import Image, ImageOps
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        pass
    img = Image.open(pfad)
    exif = img.getexif()
    f35 = None
    try:
        f35 = exif.get_ifd(0x8769).get(41989) or exif.get(41989)   # FocalLengthIn35mmFilm
    except Exception:
        f35 = exif.get(41989)
    img = ImageOps.exif_transpose(img).convert("RGB")
    W, H = img.size
    lang = max(W, H)
    if fov_grad is not None:
        f = (lang / 2) / math.tan(math.radians(fov_grad) / 2)
    elif f35:
        f = float(f35) / 36.0 * lang
    else:
        f = (lang / 2) / math.tan(math.radians(70) / 2)    # typische Handy-Hauptkamera
    return Kamera(f, f, W / 2, H / 2, W, H), np.asarray(img)


# ====================================================================== Tiefe
def schaetze_tiefe(rgb: np.ndarray, modell: str = TIEFENMODELL) -> np.ndarray:
    """Metrische Tiefe (Meter, Abstand entlang der Blickachse) für jedes Pixel."""
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation

    geraet = "cuda" if torch.cuda.is_available() else "cpu"
    proc = AutoImageProcessor.from_pretrained(modell)
    net = AutoModelForDepthEstimation.from_pretrained(modell).to(geraet).eval()
    eingabe = proc(images=Image.fromarray(rgb), return_tensors="pt").to(geraet)
    with torch.no_grad():
        tiefe = net(**eingabe).predicted_depth            # (1, h, w)
    tiefe = torch.nn.functional.interpolate(tiefe.unsqueeze(1), size=rgb.shape[:2], mode="bicubic",
                                            align_corners=False)[0, 0]
    return tiefe.clamp(min=0.05).cpu().numpy().astype(np.float32)


# ====================================================================== Masken
def maske_aus_erkennung(e: Erkennung, W: int, H: int) -> np.ndarray:
    from PIL import Image, ImageDraw
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    if e.poly and len(e.poly) >= 3:
        d.polygon([tuple(p) for p in e.poly], fill=1)
    else:   # nur Box: innere 60 % nehmen, damit weniger Hintergrund drin ist
        x1, y1, x2, y2 = e.box
        dx, dy = (x2 - x1) * 0.2, (y2 - y1) * 0.2
        d.rectangle((x1 + dx, y1 + dy, x2 - dx, y2 - dy), fill=1)
    return np.asarray(m, dtype=bool)


def _ist_rund(maske: np.ndarray) -> bool:
    """Grobe Formprüfung: Umriss mit vielen Ecken und ohne lange gerade Kanten -> rund/oval."""
    try:
        import cv2
    except ImportError:
        return False
    k, _ = cv2.findContours(maske.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not k:
        return False
    c = max(k, key=cv2.contourArea)
    umfang = cv2.arcLength(c, True)
    if umfang < 40:
        return False
    ecken = len(cv2.approxPolyDP(c, 0.02 * umfang, True))
    flaeche = cv2.contourArea(c)
    kreis = 4 * np.pi * flaeche / (umfang ** 2)     # 1 = Kreis, Quadrat ≈ 0.785
    return ecken >= 9 or kreis > 0.8


def _am_bildrand(maske: np.ndarray, rand: int = 3, anteil: float = 0.02) -> bool:
    """Berührt die Maske den linken, rechten oder unteren Bildrand deutlich?"""
    H, W = maske.shape
    hoehe_px = max(1, int(maske.any(1).sum()))
    breite_px = max(1, int(maske.any(0).sum()))
    links = maske[:, :rand].any(1).sum() / hoehe_px
    rechts = maske[:, -rand:].any(1).sum() / hoehe_px
    unten = maske[-rand:, :].any(0).sum() / breite_px
    return max(links, rechts, unten) > anteil * 10


def _doppelte_entfernen(erk: list[Erkennung], masken: list[np.ndarray], schwelle: float = 0.6):
    """Ein Objekt wird oft mehrfach erkannt (z. B. Bett als 'bed' UND 'sofa').
    Überdeckt eine Bodenmöbel-Maske eine andere zu >60 %, bleibt nur die sicherere."""
    flaeche = [max(1, int(m.sum())) for m in masken]
    reihenfolge = sorted(range(len(erk)), key=lambda i: -erk[i].conf)
    behalten: list[int] = []
    for i in reihenfolge:
        if erk[i].typ in BODENMOEBEL:
            doppelt = False
            for j in behalten:
                if erk[j].typ not in BODENMOEBEL:
                    continue
                ueber = int((masken[i] & masken[j]).sum())
                if ueber / min(flaeche[i], flaeche[j]) > schwelle:
                    doppelt = True
                    break
            if doppelt:
                continue
        behalten.append(i)
    behalten.sort()
    return [erk[i] for i in behalten], [masken[i] for i in behalten]


# ====================================================================== Geometrie
def rueckprojektion(tiefe: np.ndarray, kam: Kamera, schritt: int = 4):
    H, W = tiefe.shape
    v, u = np.mgrid[0:H:schritt, 0:W:schritt]
    z = tiefe[v, u]
    x = (u - kam.cx) * z / kam.fx
    y = (v - kam.cy) * z / kam.fy
    return np.stack([x, y, z], -1).reshape(-1, 3), v.reshape(-1), u.reshape(-1)


def boden_ransac(punkte: np.ndarray, iterationen: int = 400, toleranz: float = 0.04,
                 max_neigung_grad: float = 40, rng=None):
    """Größte fast-waagerechte Ebene. Rückgabe (n, d) mit n·X + d = Höhe über Boden (n zeigt nach oben)."""
    rng = rng or np.random.default_rng(0)
    oben = np.array([0.0, -1.0, 0.0])      # Kamera-y zeigt nach unten
    cos_max = math.cos(math.radians(max_neigung_grad))
    best, best_n, best_d = 0, None, None
    N = len(punkte)
    if N < 50:
        raise ValueError("Zu wenig Bodenpunkte – ist der Boden im Bild?")
    for _ in range(iterationen):
        a, b, c = punkte[rng.choice(N, 3, replace=False)]
        n = np.cross(b - a, c - a)
        norm = np.linalg.norm(n)
        if norm < 1e-9:
            continue
        n /= norm
        if n @ oben < 0:
            n = -n
        if n @ oben < cos_max:
            continue
        d = -n @ a
        inl = np.abs(punkte @ n + d) < toleranz
        k = int(inl.sum())
        if k > best:
            best, best_n, best_d = k, n, d
    if best_n is None:
        raise ValueError("Kein Boden gefunden – Handy gerader halten und mehr Boden ins Bild nehmen.")
    # Feinanpassung mit allen Inliern (Ebene durch SVD)
    inl = punkte[np.abs(punkte @ best_n + best_d) < toleranz]
    mitte = inl.mean(0)
    _, _, vt = np.linalg.svd(inl - mitte, full_matrices=False)
    n = vt[2]
    if n @ oben < 0:
        n = -n
    d = -n @ mitte
    if d < 0:       # Kamera muss über dem Boden sein
        n, d = -n, -d
    return n, float(d)


def bodenachsen(n: np.ndarray):
    """Zwei Achsen in der Bodenebene: e1 ≈ Kamera-rechts, e2 ≈ Kamera-vorwärts."""
    x = np.array([1.0, 0, 0])
    e1 = x - (x @ n) * n
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    if e2 @ np.array([0, 0, 1.0]) < 0:
        e2 = -e2
    return e1, e2


def _konzentration(xy: np.ndarray, winkel: float, bin_m: float = 0.05) -> float:
    c, s = math.cos(winkel), math.sin(winkel)
    r = xy @ np.array([[c, -s], [s, c]])
    score = 0.0
    for k in range(2):
        h, _ = np.histogram(r[:, k], bins=np.arange(r[:, k].min() - bin_m, r[:, k].max() + 2 * bin_m, bin_m))
        score += float((h.astype(float) ** 2).sum())
    return score


def wandausrichtung(xy: np.ndarray) -> float:
    """Drehwinkel (rad), bei dem die Wandpunkte am stärksten auf Linien liegen."""
    if len(xy) > 6000:
        xy = xy[np.random.default_rng(1).choice(len(xy), 6000, replace=False)]
    grob = max(range(0, 90, 2), key=lambda g: _konzentration(xy, math.radians(g)))
    fein = max(np.arange(grob - 2, grob + 2.01, 0.25), key=lambda g: _konzentration(xy, math.radians(g)))
    return math.radians(fein)


def wandlinien(werte: np.ndarray, bin_m: float = 0.05, min_anteil: float = 0.04) -> list[float]:
    """Positionen deutlicher Häufungen (= Wände) entlang einer Achse."""
    if len(werte) < 20:
        return []
    bins = np.arange(werte.min() - bin_m, werte.max() + 2 * bin_m, bin_m)
    h, kanten = np.histogram(werte, bins=bins)
    hs = np.convolve(h, [1, 2, 1], mode="same") / 4
    schwelle = max(min_anteil * len(werte), 15)
    peaks = []
    for i in range(1, len(hs) - 1):
        if hs[i] >= schwelle and hs[i] >= hs[i - 1] and hs[i] >= hs[i + 1]:
            sel = (werte >= kanten[max(0, i - 1)]) & (werte < kanten[min(len(kanten) - 1, i + 2)])
            peaks.append(float(np.median(werte[sel])))
    return peaks


# ====================================================================== Ergebnis
@dataclass
class Vermessung:
    layout: Layout                       # Raum + Möbel an ihren JETZIGEN Positionen
    kamera_pos: tuple[float, float]      # Standort der Kamera im Grundriss
    kamera_blick: tuple[float, float]
    kamerahoehe: float
    gesehene_waende: list[str]
    geschaetzte_waende: list[str]
    skalierung: float                    # Korrekturfaktor aus Türhöhe (1.0 = keiner)
    hinweise: list[str] = field(default_factory=list)
    wandpunkte: Optional[np.ndarray] = None    # für die Kontrollgrafik (Raumkoordinaten)
    bodenpunkte: Optional[np.ndarray] = None
    # für die Rückprojektion ins Foto (fengshui/foto_korrektur.py)
    kamera: Optional[Kamera] = None
    geometrie: Optional[dict] = None           # n, d, e1, e2, rot, links, unten
    erkennungen: list = field(default_factory=list)
    masken: list = field(default_factory=list)
    quelle: dict = field(default_factory=dict) # Möbelname -> Index in erkennungen/masken
    tiefe: Optional[np.ndarray] = None

    def sichtbar(self, rechteck: tuple[float, float, float, float], zelle: float = 0.1) -> float:
        """Anteil (0..1) einer Grundfläche, den das Foto tatsächlich gezeigt hat.
        Bereiche hinter der Kamera sind unbekannt – dort könnten Möbel oder Türen sein."""
        if getattr(self, "_sicht", None) is None:
            raum = self.layout.raum
            nx, ny = int(np.ceil(raum.breite / zelle)) + 1, int(np.ceil(raum.tiefe / zelle)) + 1
            g = np.zeros((nx, ny), bool)
            pts = self.bodenpunkte if self.bodenpunkte is not None else np.zeros((0, 2))
            ix = np.clip((pts[:, 0] / zelle).astype(int), 0, nx - 1)
            iy = np.clip((pts[:, 1] / zelle).astype(int), 0, ny - 1)
            g[ix, iy] = True
            for m in self.layout.moebel:                 # Flächen unter erkannten Möbeln sind auch "gesehen"
                if m.ist_wandobjekt or m.ist_deckenobjekt:
                    continue
                x1, y1, x2, y2 = m.rechteck
                g[max(0, int(x1 / zelle)):int(x2 / zelle) + 1, max(0, int(y1 / zelle)):int(y2 / zelle) + 1] = True
            try:                                        # kleine Lücken schließen (Wandfuß, Schatten)
                import cv2
                g = cv2.dilate(g.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
            except ImportError:
                pass
            self._sicht, self._zelle = g, zelle
        g, z = self._sicht, self._zelle
        x1, y1, x2, y2 = rechteck
        a = g[max(0, int(x1 / z)):max(int(x1 / z) + 1, int(np.ceil(x2 / z))),
              max(0, int(y1 / z)):max(int(y1 / z) + 1, int(np.ceil(y2 / z)))]
        return float(a.mean()) if a.size else 0.0

    def unsichtbar_strafe(self, lay: Layout) -> float:
        """Kosten für Möbel, die in einen nicht gesehenen Bereich gestellt würden."""
        k = 0.0
        alt = {m.name: m for m in self.layout.moebel}
        for m in lay.moebel:
            if m.ist_wandobjekt or m.ist_deckenobjekt:
                continue
            a = alt.get(m.name)
            if a is not None and abs(a.x - m.x) < 0.05 and abs(a.y - m.y) < 0.05:
                continue                                 # nicht bewegt
            k += 40.0 * max(0.0, 0.8 - self.sichtbar(m.rechteck))
        return k

    def raum_zu_kamera(self, x: float, y: float, h: float = 0.0) -> np.ndarray:
        """Punkt im Grundriss (x, y) in Höhe h -> 3D-Kamerakoordinaten."""
        g = self.geometrie
        r = np.array([x + g["links"], y + g["unten"]])
        a, b = r @ g["rot"].T
        return a * g["e1"] + b * g["e2"] + (h - g["d"]) * g["n"]

    def raum_zu_pixel(self, x: float, y: float, h: float = 0.0) -> tuple[float, float, float]:
        X = self.raum_zu_kamera(x, y, h)
        k = self.kamera
        z = float(X[2])
        if z <= 1e-3:
            return float("nan"), float("nan"), z
        return float(k.fx * X[0] / z + k.cx), float(k.fy * X[1] / z + k.cy), z

    def fuer_optimierer(self) -> Layout:
        """Gleiche Möbel, aber Nachttische/Couchtisch hängen am Hauptmöbel (für optimiere())."""
        lay = self.layout.kopie()
        betten = [m for m in lay.moebel if m.typ == "bett"]
        sofas = [m for m in lay.moebel if m.typ == "sofa"]
        tische = [m for m in lay.moebel if m.typ == "esstisch"]
        seite = 0
        for m in lay.moebel:
            if m.typ == "nachttisch" and betten:
                m.gehoert_zu, m.seite = betten[0].name, ("links", "rechts")[seite % 2]
                seite += 1
            if m.typ == "couchtisch" and sofas:
                m.gehoert_zu, m.seite, m.abstand = sofas[0].name, "vorne", 0.45
            if m.typ == "stuhl" and tische:
                m.gehoert_zu = min(tische, key=lambda t: (t.x - m.x) ** 2 + (t.y - m.y) ** 2).name
        return lay


def vermesse(rgb_form: tuple[int, int], tiefe: np.ndarray, kam: Kamera, erkennungen: list[Erkennung],
             raumtyp: str = "schlafzimmer", kamera_in_ecke: bool = True, foto_von_tuer: bool = False,
             tuer_kalibrierung: bool = True, masken: Optional[list[np.ndarray]] = None,
             raumhoehe: Optional[float] = None, randobjekte_fest: bool = True) -> Vermessung:
    """Kernfunktion: Tiefenkarte + Erkennungen → Raum und Möbel in Metern."""
    H, W = rgb_form
    hinweise: list[str] = []
    if masken is None:
        masken = [maske_aus_erkennung(e, W, H) for e in erkennungen]
    erkennungen, masken = _doppelte_entfernen(list(erkennungen), list(masken))

    schritt = max(2, int(round(max(W, H) / 400)))
    P, vv, uu = rueckprojektion(tiefe, kam, schritt)
    alle_masken = np.zeros((H, W), bool)
    for e, m in zip(erkennungen, masken):
        if e.typ not in ("teppich",):
            alle_masken |= m
    frei = ~alle_masken[vv, uu]

    # ---------- 1. Boden
    unten = vv > H * 0.45
    kandidaten = P[frei & unten]
    n, d = boden_ransac(kandidaten)
    hoehe = P @ n + d
    e1, e2 = bodenachsen(n)

    # ---------- 2. Kalibrierung mit der Türhöhe (Standard 2,0 m)
    skala = 1.0
    if tuer_kalibrierung:
        for e, m in zip(erkennungen, masken):
            if e.typ != "tuer":
                continue
            x1, y1, x2, y2 = e.box
            if y1 < 3 or y2 > H - 3:        # Tür oben/unten abgeschnitten -> nicht messbar
                continue
            sel = m[vv, uu]
            if sel.sum() < 30:
                continue
            gemessen = float(np.percentile(hoehe[sel], 99.5))      # Türoberkante über dem Boden
            if gemessen > 0.5:
                s = STANDARD_TUER_HOEHE / gemessen
                if 0.75 < s < 1.33:
                    skala = s
                    hinweise.append(f"Maßstab mit Türhöhe kalibriert (Faktor {s:.2f}).")
            break
    if skala != 1.0:
        P = P * skala
        d = d * skala
        hoehe = P @ n + d
    kamerahoehe = d

    xy = np.stack([P @ e1, P @ e2], -1)       # Bodenkoordinaten, Kamera bei (0,0), Blick ≈ +y

    # ---------- 3. Wände
    h_max = min(2.0, (raumhoehe or 2.6) - 0.3)
    wand_sel = frei & (hoehe > 0.4) & (hoehe < h_max) & (np.linalg.norm(xy, axis=1) > 0.4)
    boden_sel = frei & (np.abs(hoehe) < 0.05)
    wxy = xy[wand_sel]
    if len(wxy) < 100:
        raise ValueError("Zu wenig Wandfläche sichtbar – fotografiere diagonal in eine Ecke.")
    theta = wandausrichtung(wxy)
    c, s_ = math.cos(theta), math.sin(theta)
    rot = np.array([[c, -s_], [s_, c]])
    wr = wxy @ rot
    br = xy[boden_sel] @ rot

    grenzen = {}
    gesehen, geschaetzt = [], []
    for achse, (neg, pos) in enumerate([("links", "rechts"), ("unten", "oben")]):
        linien = wandlinien(wr[:, achse])
        lo = [p for p in linien if p < -0.15]
        hi = [p for p in linien if p > 0.15]
        boden_lo = np.percentile(br[:, achse], 1) if len(br) else -0.3
        boden_hi = np.percentile(br[:, achse], 99) if len(br) else 0.3
        if lo:
            grenzen[neg] = min(lo); gesehen.append(neg)
        else:
            grenzen[neg] = min(-0.3, boden_lo - 0.05) if kamera_in_ecke else boden_lo
            geschaetzt.append(neg)
        if hi:
            grenzen[pos] = max(hi); gesehen.append(pos)
        else:
            grenzen[pos] = max(0.3, boden_hi + 0.05) if kamera_in_ecke else boden_hi
            geschaetzt.append(pos)
    breite = grenzen["rechts"] - grenzen["links"]
    tiefe_raum = grenzen["oben"] - grenzen["unten"]

    def raumkoord(q):              # (N,2) Bodenkoordinaten -> Raumkoordinaten
        r = q @ rot
        return np.stack([r[:, 0] - grenzen["links"], r[:, 1] - grenzen["unten"]], -1)

    kam_pos = raumkoord(np.zeros((1, 2)))[0]
    blick = (np.array([[0.0, 1.0]]) @ rot)[0]

    if raumhoehe is None:
        decke = hoehe[frei & (vv < H * 0.15)]
        raumhoehe = float(np.clip(np.percentile(decke, 95), 2.2, 3.5)) if len(decke) > 50 else 2.5

    raum = Raum("Zimmer (aus Foto)", round(float(breite), 2), round(float(tiefe_raum), 2), raumtyp=raumtyp,
                hoehe=round(raumhoehe, 2))

    # ---------- 4. Objekte
    def naechste_wand(px, py):
        abst = {"links": px, "rechts": raum.breite - px, "unten": py, "oben": raum.tiefe - py}
        w = min(abst, key=abst.get)
        return w, abst[w]

    moebel: list[Moebel] = []
    zaehler: dict[str, int] = {}
    quelle: dict[str, int] = {}
    for idx, (e, m) in enumerate(zip(erkennungen, masken)):
        sel = m[vv, uu]
        if sel.sum() < 15:
            continue
        pts_h = hoehe[sel]
        pts = raumkoord(xy[sel])
        # Hintergrund, der durch die Maske "durchscheint", entfernen
        z = P[sel] @ e2
        ok = np.abs(z - np.median(z)) < 1.0
        pts, pts_h = pts[ok], pts_h[ok]
        if len(pts) < 10:
            continue
        x_lo, x_hi = np.percentile(pts[:, 0], [2, 98])
        y_lo, y_hi = np.percentile(pts[:, 1], [2, 98])
        cx, cy = (x_lo + x_hi) / 2, (y_lo + y_hi) / 2

        if e.typ in ("tuer", "fenster"):
            wand, _ = naechste_wand(cx, cy)
            entlang = pts[:, 0] if wand in ("unten", "oben") else pts[:, 1]
            von, bis = np.percentile(entlang, [1, 99])
            br_ = float(np.clip(bis - von, 0.5, 3.0))
            if e.typ == "tuer":
                raum.oeffnungen.append(Oeffnung("tuer", wand, round(float(von), 2), round(br_, 2),
                                                haupttuer=not any(o.typ == "tuer" for o in raum.oeffnungen)))
            else:
                brue = float(np.clip(np.percentile(pts_h, 3), 0.0, 1.5))
                oben = float(np.percentile(pts_h, 97))
                typ = "balkontuer" if brue < 0.25 else "fenster"
                raum.oeffnungen.append(Oeffnung(typ, wand, round(float(von), 2), round(br_, 2),
                                                bruestung=round(brue, 2), hoehe=round(oben - brue, 2)))
            continue

        if e.typ not in STANDARD_MASSE or e.typ == "teppich":
            continue
        if e.typ in NICHT_ALS_MOEBEL and not any(x.typ == "esstisch" for x in erkennungen):
            continue        # Schreibtischstuhl usw. gehört zum Tisch, kein eigenes Möbel
        zaehler[e.typ] = zaehler.get(e.typ, 0) + 1
        name = e.typ.capitalize() + (f" {zaehler[e.typ]}" if zaehler[e.typ] > 1 else "")
        b0, t0, h0 = STANDARD_MASSE[e.typ]

        if e.typ in WANDOBJEKTE_FOTO:          # Spiegel, Bild, Wandregal
            wand, _ = naechste_wand(cx, cy)
            entlang = pts[:, 0] if wand in ("unten", "oben") else pts[:, 1]
            von, bis = np.percentile(entlang, [5, 95])
            mb = float(np.clip(bis - von, 0.2, 3.0))
            mo = Moebel(e.typ, round(mb, 2), t0, round(float(np.percentile(pts_h, 95) - np.percentile(pts_h, 5)), 2),
                        name=name)
            mo.rot = VEKTOR_ROT[WAND_NORMALE[wand]]
            mitte = (von + bis) / 2
            if wand == "unten":
                mo.x, mo.y = mitte, t0 / 2
            elif wand == "oben":
                mo.x, mo.y = mitte, raum.tiefe - t0 / 2
            elif wand == "links":
                mo.x, mo.y = t0 / 2, mitte
            else:
                mo.x, mo.y = raum.breite - t0 / 2, mitte
            moebel.append(mo)
            quelle[name] = idx
            continue

        if e.typ in ("pendelleuchte", "ventilator", "tischleuchte"):     # Decke bzw. auf einem Möbel
            mo = Moebel(e.typ, b0, t0, h0, name=name, rund=True)
            mo.x, mo.y = round(float(np.median(pts[:, 0])), 2), round(float(np.median(pts[:, 1])), 2)
            moebel.append(mo)
            quelle[name] = idx
            continue

        # ---- Bodenmöbel
        dx, dy = float(x_hi - x_lo), float(y_hi - y_lo)
        hoehe_m = float(np.clip(np.percentile(pts_h, 97), 0.2, 2.6))
        wand, abstand = naechste_wand(cx, cy)
        an_wand = abstand < max(dx, dy) / 2 + 0.45
        if an_wand:
            normal = WAND_NORMALE[wand]
            rot_ = VEKTOR_ROT[normal]                  # Rückseite an der Wand
            entlang_mass = dx if wand in ("unten", "oben") else dy
            quer_mass = dy if wand in ("unten", "oben") else dx
            # sichtbare Tiefe ist oft zu klein (Rückseite verdeckt) -> mit Standard auffüllen
            breite_m = float(np.clip(entlang_mass, 0.6 * b0, 1.8 * b0))
            tiefe_m = float(np.clip(max(quer_mass, 0.8 * t0), 0.6 * t0, 1.5 * t0))
            mo = Moebel(e.typ, round(breite_m, 2), round(tiefe_m, 2), round(hoehe_m, 2), name=name,
                        rund=e.typ in ("pflanze", "kaktus"))
            mo.rot = rot_
            if wand in ("unten", "oben"):
                mo.x = float(np.clip(cx, breite_m / 2, raum.breite - breite_m / 2))
                mo.y = tiefe_m / 2 if wand == "unten" else raum.tiefe - tiefe_m / 2
            else:
                mo.y = float(np.clip(cy, breite_m / 2, raum.tiefe - breite_m / 2))
                mo.x = tiefe_m / 2 if wand == "links" else raum.breite - tiefe_m / 2
        else:
            # frei stehend: Vorderseite zeigt zur Raummitte bzw. zur Kamera
            lang_x = dx >= dy
            mo = Moebel(e.typ, 0, 0, round(hoehe_m, 2), name=name, rund=e.typ in ("pflanze", "kaktus"))
            zur_kamera = np.array([kam_pos[0] - cx, kam_pos[1] - cy])
            if lang_x:
                mo.breite, mo.tiefe = round(max(dx, 0.6 * b0), 2), round(max(dy, 0.8 * t0), 2)
                mo.rot = 180 if zur_kamera[1] < 0 else 0
            else:
                mo.breite, mo.tiefe = round(max(dy, 0.6 * b0), 2), round(max(dx, 0.8 * t0), 2)
                mo.rot = 270 if zur_kamera[0] < 0 else 90
            mo.x, mo.y = float(cx), float(cy)
        if e.typ == "bett":
            # Bettlänge ist fast immer ~2 m: unplausible Werte korrigieren
            if not 1.85 <= mo.tiefe <= 2.25:
                mo.tiefe = 2.0
                if an_wand:
                    nx_, ny_ = WAND_NORMALE[wand]
                    mo.x = mo.x if nx_ == 0 else (1.0 if wand == "links" else raum.breite - 1.0)
                    mo.y = mo.y if ny_ == 0 else (1.0 if wand == "unten" else raum.tiefe - 1.0)
        mo.x, mo.y = round(mo.x, 2), round(mo.y, 2)
        if e.typ in ("couchtisch", "esstisch", "nachttisch", "schreibtisch") and _ist_rund(m):
            mo.rund = True
        if randobjekte_fest and _am_bildrand(m):
            mo.fest = True
            hinweise.append(f"{name} ist vom Bildrand abgeschnitten – Maße unsicher, wird nicht verschoben.")
        moebel.append(mo)
        quelle[name] = idx

    # ---------- 5. Tür hinter der Kamera?
    if foto_von_tuer and not raum.tueren:
        rueck = (-blick[0], -blick[1])
        wand = max(WAND_NORMALE, key=lambda w: -(WAND_NORMALE[w][0] * rueck[0] + WAND_NORMALE[w][1] * rueck[1]))
        pos = kam_pos[0] if wand in ("unten", "oben") else kam_pos[1]
        L = raum.wandlaenge(wand)
        von = float(np.clip(pos - 0.45, 0.05, L - 0.95))
        raum.oeffnungen.append(Oeffnung("tuer", wand, round(von, 2), 0.9))
        hinweise.append(f"Tür hinter der Kamera angenommen (Wand '{wand}').")
    if not raum.tueren:
        hinweise.append("Keine Tür gefunden – bitte Tür eintragen oder `foto_von_tuer=True` setzen, "
                        "sonst fehlen die Regeln zur Kommandoposition.")
    if not raum.fenster:
        hinweise.append("Kein Fenster erkannt – falls vorhanden, bitte nachtragen.")
    if geschaetzt:
        hinweise.append("Nicht sichtbare Wände (geschätzt): " + ", ".join(geschaetzt) +
                        (" – angenommen: du standest in einer Ecke." if kamera_in_ecke else ""))
    hinweise.append(f"Kamerahöhe gemessen: {kamerahoehe:.2f} m (Plausibilitätscheck: Brusthöhe ≈ 1,2–1,6 m).")
    if not 0.9 <= kamerahoehe <= 2.0:
        hinweise.append("⚠ Kamerahöhe unplausibel – Maßstab evtl. falsch. Prüfe eine bekannte Länge (z. B. Bett 2,0 m).")

    lay = Layout(raum, moebel, Bewohner())
    _aufraeumen(lay)
    geo = {"n": n, "d": float(d), "e1": e1, "e2": e2, "rot": rot,
           "links": float(grenzen["links"]), "unten": float(grenzen["unten"])}
    return Vermessung(lay, (round(float(kam_pos[0]), 2), round(float(kam_pos[1]), 2)),
                      (float(blick[0]), float(blick[1])), round(kamerahoehe, 2), gesehen, geschaetzt, skala,
                      hinweise, raumkoord(wxy), raumkoord(xy[boden_sel]),
                      kam, geo, erkennungen, masken, quelle, tiefe * skala)


def _aufraeumen(lay: Layout, runden: int = 12) -> None:
    """Messrauschen ausgleichen: Möbel in den Raum schieben, kleine Überlappungen auflösen."""
    raum = lay.raum
    from .modell import FLACH
    boden = [m for m in lay.moebel if not m.ist_wandobjekt and m.typ not in FLACH]

    def klemmen(m):
        dx, dy = m.ausdehnung
        m.x = min(max(m.x, dx / 2 + 0.005), raum.breite - dx / 2 - 0.005)
        m.y = min(max(m.y, dy / 2 + 0.005), raum.tiefe - dy / 2 - 0.005)

    for _ in range(runden):
        bewegt = False
        for m in boden:
            klemmen(m)
        for i, a in enumerate(boden):
            for b in boden[i + 1:]:
                ax1, ay1, ax2, ay2 = a.rechteck
                bx1, by1, bx2, by2 = b.rechteck
                ox = min(ax2, bx2) - max(ax1, bx1)
                oy = min(ay2, by2) - max(ay1, by1)
                if ox <= 0.001 or oy <= 0.001:
                    continue
                # das kleinere Möbel weicht aus, entlang der kürzeren Überlappung
                klein, gross = (a, b) if a.breite * a.tiefe < b.breite * b.tiefe else (b, a)
                if ox < oy:
                    klein.x += (ox + 0.01) * (1 if klein.x >= gross.x else -1)
                else:
                    klein.y += (oy + 0.01) * (1 if klein.y >= gross.y else -1)
                bewegt = True
        if not bewegt:
            break
    for m in lay.moebel:
        if not m.ist_wandobjekt:
            klemmen(m)
        m.x, m.y = round(m.x, 3), round(m.y, 3)


# ====================================================================== Alles in einem
def zimmer_aus_foto(pfad: str, raumtyp: str = "auto", yolo_modell: str = "yoloe-11s-seg.pt",
                    conf: float = 0.2, kamera_in_ecke: bool = True, foto_von_tuer: bool = False,
                    fov_grad: Optional[float] = None, bekannte_breite: Optional[float] = None,
                    bekannte_tiefe: Optional[float] = None) -> tuple[Vermessung, list[Erkennung], np.ndarray]:
    """Foto → YOLO-Erkennung + Tiefenschätzung → Vermessung.

    bekannte_breite / bekannte_tiefe (optional): Wenn du EINE Länge kennst (z. B. die Raumbreite),
    wird der Maßstab daran ausgerichtet – das verbessert die Genauigkeit deutlich.
    """
    import os
    import tempfile
    from PIL import Image
    from .foto import erkenne

    kam, rgb = kamera_aus_foto(pfad, fov_grad)
    # gedrehtes (EXIF-korrigiertes) Bild für YOLO speichern, damit Masken und Tiefe zusammenpassen
    tmp = os.path.join(tempfile.gettempdir(), "fengshui_foto_gerade.jpg")
    Image.fromarray(rgb).save(tmp, quality=95)
    erk, _ = erkenne(tmp, yolo_modell, conf)
    if raumtyp in (None, "", "auto"):
        from .foto import raumtyp_erkennen
        raumtyp = raumtyp_erkennen(erk)
    tiefe = schaetze_tiefe(rgb)
    v = vermesse(rgb.shape[:2], tiefe, kam, erk, raumtyp, kamera_in_ecke, foto_von_tuer)
    bekannt = [(bekannte_breite, v.layout.raum.breite), (bekannte_tiefe, v.layout.raum.tiefe)]
    faktoren = [b / g for b, g in bekannt if b and g > 0]
    if faktoren:
        f = float(np.mean(faktoren)) * v.skalierung
        tiefe = tiefe * f
        v = vermesse(rgb.shape[:2], tiefe, kam, erk, raumtyp, kamera_in_ecke, foto_von_tuer,
                     tuer_kalibrierung=False)
        v.skalierung = f
        v.hinweise.insert(0, f"Maßstab an deiner bekannten Länge ausgerichtet (Faktor {f:.2f}).")
    return v, erk, tiefe


# ====================================================================== Ausgabe
def als_python_code(lay: Layout) -> str:
    r = lay.raum
    z = ["raum = Raum(", f'    name="{r.name}", breite={r.breite}, tiefe={r.tiefe}, hoehe={r.hoehe},',
         f'    raumtyp="{r.raumtyp}", nord_wand=None,   # <- Himmelsrichtung bitte ergänzen', "    oeffnungen=["]
    for o in r.oeffnungen:
        extra = f", bruestung={o.bruestung}" if o.ist_fenster else ""
        z.append(f'        Oeffnung("{o.typ}", wand="{o.wand}", von={o.von}, breite={o.breite}{extra}),')
    z += ["    ],", ")", "moebel = ["]
    for m in lay.moebel:
        extra = ", rund=True" if m.rund else ""
        z.append(f'    Moebel("{m.typ}", breite={m.breite}, tiefe={m.tiefe}, hoehe={m.hoehe}, name="{m.name}", '
                 f'x={m.x}, y={m.y}, rot={m.rot}{extra}),')
    z.append("]")
    return "\n".join(z)


def zeichne_vermessung(v: Vermessung, datei: Optional[str] = None, zeigen: bool = True, titel: str = ""):
    """Grundriss + Kontrollpunkte (grau = Wände, hellgrün = Boden) + Kamerastandort."""
    import matplotlib.pyplot as plt
    from .visualisierung import zeichne
    raum = v.layout.raum
    fig, ax = plt.subplots(figsize=(6.5, 6.5 * raum.tiefe / max(raum.breite, 0.1) + 0.6))
    if v.bodenpunkte is not None and len(v.bodenpunkte):
        bp = v.bodenpunkte[:: max(1, len(v.bodenpunkte) // 4000)]
        ax.scatter(bp[:, 0], bp[:, 1], s=1, c="#a7c957", alpha=0.25, zorder=0)
    if v.wandpunkte is not None and len(v.wandpunkte):
        wp = v.wandpunkte[:: max(1, len(v.wandpunkte) // 4000)]
        ax.scatter(wp[:, 0], wp[:, 1], s=1, c="#6c757d", alpha=0.35, zorder=0)
    zeichne(v.layout, titel or f"Aus Foto vermessen: {raum.breite:.2f} × {raum.tiefe:.2f} m", ax=ax, chi=False)
    kx, ky = v.kamera_pos
    ax.plot(kx, ky, marker="^", ms=11, color="#e63946", zorder=5)
    ax.annotate("", xy=(kx + v.kamera_blick[0] * 0.6, ky + v.kamera_blick[1] * 0.6), xytext=(kx, ky),
                arrowprops=dict(arrowstyle="->", color="#e63946", lw=2), zorder=5)
    ax.text(kx, ky - 0.18, "Kamera", color="#e63946", fontsize=7, ha="center")
    for w in v.geschaetzte_waende:
        pos = {"unten": (raum.breite / 2, 0.08), "oben": (raum.breite / 2, raum.tiefe - 0.08),
               "links": (0.08, raum.tiefe / 2), "rechts": (raum.breite - 0.08, raum.tiefe / 2)}[w]
        ax.text(*pos, "geschätzt", fontsize=7, color="#e76f51", ha="center", va="center",
                rotation=90 if w in ("links", "rechts") else 0)
    fig.tight_layout()
    if datei:
        fig.savefig(datei, dpi=140)
    if zeigen:
        plt.show()
    else:
        plt.close(fig)


def schreibe_mein_zimmer(v: Vermessung, pfad: str = "mein_zimmer.py", profil: Optional[dict] = None) -> None:
    """Schreibt das Vermessungsergebnis als mein_zimmer.py – danach laufen main.py / lernen.py wie gewohnt."""
    lay = v.fuer_optimierer()          # gleiche Positionen, Nachttische hängen am Bett
    r = lay.raum
    z = ['"""Automatisch aus einem Foto vermessen (fengshui/foto3d.py). Werte bei Bedarf korrigieren."""',
         "from fengshui.modell import Balken, Bewohner, Layout, Moebel, Oeffnung, Raum, Schraege", "", "",
         "def erstelle_layout() -> Layout:", "    raum = Raum(",
         f'        name="{r.name}", breite={r.breite}, tiefe={r.tiefe}, hoehe={r.hoehe},',
         f'        raumtyp="{r.raumtyp}",', "        nord_wand=None,   # optional: welche Wand zeigt nach Norden?",
         "        oeffnungen=["]
    for o in r.oeffnungen:
        extra = f", bruestung={o.bruestung}" if o.ist_fenster else ""
        z.append(f'            Oeffnung("{o.typ}", wand="{o.wand}", von={o.von}, breite={o.breite}{extra}),')
    z += ["        ],", "    )", "    moebel = ["]
    for m in lay.moebel:
        extra = ", rund=True" if m.rund else ""
        if m.gehoert_zu:
            extra += f', gehoert_zu="{m.gehoert_zu}", seite="{m.seite}"'
            if m.abstand != 0.02:
                extra += f", abstand={m.abstand}"
        z.append(f'        Moebel("{m.typ}", breite={m.breite}, tiefe={m.tiefe}, hoehe={m.hoehe}, '
                 f'name="{m.name}", x={m.x}, y={m.y}, rot={m.rot}{extra}),')
    z += ["    ]", "    bewohner = Bewohner(paar=False, sucht_partner=False, viele_bildschirme=False,",
          "                        arbeit_wichtiger_als_schlaf=False, pflanzen_sind_freunde=False)",
          "    return Layout(raum, moebel, bewohner)", "", "",
          f"PROFIL = {repr(profil or {})}", ""]
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(z))
