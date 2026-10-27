"""
Dein Zimmerfoto → dasselbe Foto mit den Möbeln an der korrigierten Position.

Ablauf
------
1. `foto3d.vermesse` kennt Boden, Kamera und die Umrisse (Masken) aller Möbel.
2. `optimierer.korrigiere` verschiebt nur die Möbel, die gegen Regeln verstoßen – so wenig wie möglich.
3. Für jedes verschobene Möbel:
   • alte Stelle: Möbel ausschneiden, Lücke auffüllen (LaMa-KI, sonst OpenCV)
   • neue Stelle: Ausschnitt perspektivisch skaliert an die neue Bodenposition setzen
     (näher an der Kamera = größer, weiter weg = kleiner)
   • gedrehte Möbel lassen sich aus einem Foto nicht realistisch drehen (die Rückseite ist unbekannt):
     sie werden als grüner 3D-Umriss mit „drehen“ eingezeichnet
4. Zusätzlich eine Erklär-Version: rote Umrisse = vorher, grüne 3D-Boxen = nachher, Pfeile, Nummern.

Ergebnis ist eine Vorschau, kein Foto-Realismus: Beim Verschieben behält das Möbel die
Ansicht aus dem Originalfoto, verdeckte Flächen werden von der KI geschätzt.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from .foto3d import Vermessung
from .modell import Layout

GRUEN = (46, 196, 120)
ROT = (230, 57, 70)
GELB = (255, 200, 60)


# ------------------------------------------------------------------ Hilfen
def _schrift(groesse: int):
    from PIL import ImageFont
    try:
        from matplotlib import font_manager
        return ImageFont.truetype(font_manager.findfont("DejaVu Sans"), groesse)
    except Exception:
        try:
            return ImageFont.load_default(size=groesse)
        except TypeError:
            return ImageFont.load_default()


def _box_ecken(v: Vermessung, m) -> Optional[list[tuple[float, float]]]:
    """8 Bildpunkte der 3D-Box eines Möbels (unten 0–3, oben 4–7) oder None, falls hinter der Kamera."""
    x1, y1, x2, y2 = m.rechteck
    h = max(0.05, float(m.hoehe))
    if m.ist_wandobjekt:            # flaches Rechteck an der Wand, ca. Brust- bis Kopfhöhe
        unten = 0.8 if m.typ != "wandregal" else 1.4
        hs = (unten, unten + min(h, 1.2))
    else:
        hs = (0.0, h)
    pts = []
    for hh in hs:
        for (x, y) in [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]:
            u, vv, z = v.raum_zu_pixel(x, y, hh)
            if not (z > 0.15) or math.isnan(u):
                return None
            pts.append((u, vv))
    return pts


def _zeichne_box(draw, pts, farbe, breite=3, gestrichelt=False):
    kanten = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    for a, b in kanten:
        (x0, y0), (x1, y1) = pts[a], pts[b]
        if gestrichelt:
            n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 14))
            for i in range(0, n, 2):
                t0, t1 = i / n, min(1.0, (i + 1) / n)
                draw.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                          fill=farbe, width=breite)
        else:
            draw.line([(x0, y0), (x1, y1)], fill=farbe, width=breite)


def _fuelle_box(draw, pts, farbe):
    """Seitenflächen und Deckel einer 3D-Box halbtransparent füllen."""
    flaechen = [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for f in flaechen:
        draw.polygon([pts[i] for i in f], fill=farbe)


def _kontur(maske: np.ndarray) -> list:
    import cv2
    k, _ = cv2.findContours(maske.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c[:, 0, :].tolist() for c in k if len(c) >= 3]


LAMA_URL = "https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt"
_LAMA = {}


def _herunterladen(url: str, ziel: str) -> None:
    """Download mit `requests` (nutzt certifi) – umgeht das bekannte Mac-Zertifikatsproblem von urllib."""
    import os
    import requests
    print(f"  Lade LaMa-Modell (~200 MB, einmalig) …")
    tmp = ziel + ".teil"
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for block in r.iter_content(1 << 20):
                f.write(block)
    os.replace(tmp, ziel)


def _lama(rgb: np.ndarray, maske: np.ndarray) -> np.ndarray:
    """LaMa (Large Mask Inpainting) – füllt große Lücken realistisch. Lädt ~200 MB beim ersten Mal."""
    import os
    import torch
    if "m" not in _LAMA:
        pfad = os.environ.get("LAMA_MODELL") or os.path.join(torch.hub.get_dir(), "big-lama.pt")
        if not os.path.exists(pfad):
            os.makedirs(os.path.dirname(pfad), exist_ok=True)
            _herunterladen(LAMA_URL, pfad)
        geraet = "cuda" if torch.cuda.is_available() else "cpu"
        _LAMA["m"] = torch.jit.load(pfad, map_location=geraet).eval()
        _LAMA["g"] = geraet
    H, W = rgb.shape[:2]
    ph, pw = (8 - H % 8) % 8, (8 - W % 8) % 8
    bild = np.pad(rgb, ((0, ph), (0, pw), (0, 0)), mode="symmetric").astype(np.float32) / 255.0
    msk = np.pad((maske > 0).astype(np.float32), ((0, ph), (0, pw)))
    with torch.no_grad():
        t_bild = torch.from_numpy(bild).permute(2, 0, 1)[None].to(_LAMA["g"])
        t_msk = torch.from_numpy(msk)[None, None].to(_LAMA["g"])
        aus = _LAMA["m"](t_bild, t_msk)[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()
    return (aus[:H, :W] * 255).round().astype(np.uint8)


def luecke_fuellen(rgb: np.ndarray, maske: np.ndarray, methode: str = "auto") -> np.ndarray:
    """Füllt die Stellen, an denen ein Möbel entfernt wurde: LaMa-KI, falls möglich, sonst OpenCV."""
    import cv2
    m = cv2.dilate(maske.astype(np.uint8) * 255, np.ones((15, 15), np.uint8))
    if methode in ("auto", "lama"):
        try:
            return _lama(rgb, m)
        except Exception as fehler:
            if methode == "lama":
                raise
            print(f"  (LaMa nicht verfügbar: {fehler.__class__.__name__}: {fehler} – nutze OpenCV-Auffüllen)")
    return cv2.inpaint(rgb, m, 9, cv2.INPAINT_TELEA)


# ------------------------------------------------------------------ Hauptfunktion
def korrigiere_foto(rgb: np.ndarray, v: Vermessung, neu: Layout, aenderungen: list,
                    fuellen: str = "auto") -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Gibt (Foto mit verschobenen Möbeln, Erklär-Foto mit Umrissen/Pfeilen, Legende) zurück."""
    import cv2
    from PIL import Image, ImageDraw

    H, W = rgb.shape[:2]
    alt = {m.name: m for m in v.layout.moebel}
    neu_m = {m.name: m for m in neu.moebel}
    tiefe = v.tiefe

    def zentrum_tiefe(idx):
        sel = v.masken[idx]
        return float(np.median(tiefe[sel])) if sel.any() else 99.0

    # ---------- 1. was wird ausgeschnitten und wohin gesetzt?
    plaene, nur_umriss, legende, entfernen = [], [], [], []
    for nr, a in enumerate(aenderungen, 1):
        legende.append(f"{nr}. {a.text()}" + (f" – weil: {a.gruende[0]}" if a.gruende else ""))
        idx = v.quelle.get(a.name)
        m_alt, m_neu = alt[a.name], neu_m[a.name]
        if idx is None or m_alt.ist_wandobjekt or m_alt.ist_deckenobjekt:
            nur_umriss.append((nr, a))
            continue
        u0, v0, z0 = v.raum_zu_pixel(m_alt.x, m_alt.y, 0.0)
        u1, v1, z1 = v.raum_zu_pixel(m_neu.x, m_neu.y, 0.0)
        if a.gedreht or not (z0 > 0.2 and z1 > 0.2):
            nur_umriss.append((nr, a))
            if z0 > 0.2:
                entfernen.append(idx)          # alte Stelle trotzdem leeren, neue Stelle als 3D-Box zeigen
            continue
        s = z0 / z1
        if not 0.4 < s < 2.5:
            nur_umriss.append((nr, a))
            continue
        plaene.append({"nr": nr, "a": a, "idx": idx, "s": s, "tx": u1 - s * u0, "ty": v1 - s * v0, "z1": z1})

    # ---------- 2. Lücken füllen
    weg = np.zeros((H, W), bool)
    for p in plaene:
        weg |= v.masken[p["idx"]]
    for idx in entfernen:
        weg |= v.masken[idx]
    bild = luecke_fuellen(rgb, weg, fuellen) if weg.any() else rgb.copy()

    # ---------- 3. Ausschnitte an die neue Stelle setzen (weit weg zuerst)
    belegt_tiefe = np.full((H, W), np.inf, np.float32)
    for p in sorted(plaene, key=lambda p: -p["z1"]):
        M = np.float32([[p["s"], 0, p["tx"]], [0, p["s"], p["ty"]]])
        maske = cv2.warpAffine(v.masken[p["idx"]].astype(np.uint8) * 255, M, (W, H), flags=cv2.INTER_LINEAR) / 255.0
        quelle = cv2.warpAffine(rgb, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        maske = cv2.GaussianBlur(maske, (3, 3), 0)[..., None]
        bild = (bild * (1 - maske) + quelle * maske).astype(np.uint8)
        belegt_tiefe[maske[..., 0] > 0.5] = np.minimum(belegt_tiefe[maske[..., 0] > 0.5], p["z1"])

    # ---------- 4. Verdeckung: nicht bewegte Möbel, die näher sind, wieder darüberlegen
    bewegt = {p["idx"] for p in plaene} | set(entfernen)
    for idx, msk in enumerate(v.masken):
        if idx in bewegt or v.erkennungen[idx].typ in ("fenster", "tuer", "teppich", "bild", "spiegel"):
            continue
        z = zentrum_tiefe(idx)
        vorne = msk & (belegt_tiefe > z + 0.1) & np.isfinite(belegt_tiefe)
        if vorne.any():
            bild[vorne] = rgb[vorne]

    # ---------- 5. Umrisse für gedrehte / nicht verschiebbare Möbel (auch im Ergebnisbild)
    erg_pil = Image.fromarray(bild).convert("RGBA")
    schicht = Image.new("RGBA", erg_pil.size, (0, 0, 0, 0))
    d_erg = ImageDraw.Draw(schicht)
    ausserhalb = []
    for nr, a in nur_umriss:
        pts = _box_ecken(v, neu_m[a.name])
        sichtbar = pts is not None and any(0 <= x < W and 0 <= y < H for x, y in pts)
        if not sichtbar:
            ausserhalb.append(a.name)
            continue
        if pts:
            _fuelle_box(d_erg, pts, GRUEN + (95,))
            _zeichne_box(d_erg, pts, GRUEN + (255,), breite=max(2, W // 350))
            oben = min(pts, key=lambda p: p[1])
            txt = f"{a.name} hierhin" + (" (gedreht)" if a.gedreht else "")
            f = _schrift(max(14, W // 45))
            x0, y0 = oben[0], max(0, oben[1] - f.size - 10)
            d_erg.rectangle(d_erg.textbbox((x0, y0), txt, font=f), fill=(0, 0, 0, 170))
            d_erg.text((x0, y0), txt, fill=(255, 255, 255, 255), font=f)
    if ausserhalb:
        f = _schrift(max(14, W // 50))
        txt = ", ".join(ausserhalb) + ": neue Stelle liegt außerhalb des Fotos – siehe Grundriss"
        box = d_erg.textbbox((12, H - f.size - 22), txt, font=f)
        d_erg.rectangle((box[0] - 6, box[1] - 6, box[2] + 6, box[3] + 6), fill=(0, 0, 0, 180))
        d_erg.text((12, H - f.size - 22), txt, fill=GELB + (255,), font=f)
    erg_pil = Image.alpha_composite(erg_pil, schicht).convert("RGB")

    # ---------- 6. Erklär-Version
    erkl = Image.fromarray(rgb).convert("RGB")
    dr = ImageDraw.Draw(erkl, "RGBA")
    schrift = _schrift(max(13, W // 55))
    lw = max(2, W // 350)
    for nr, a in enumerate(aenderungen, 1):
        idx = v.quelle.get(a.name)
        if idx is not None:
            for k in _kontur(v.masken[idx]):
                dr.line([tuple(p) for p in k] + [tuple(k[0])], fill=ROT + (255,), width=lw)
        pts = _box_ecken(v, neu_m[a.name])
        if pts:
            _zeichne_box(dr, pts, GRUEN + (255,), breite=lw, gestrichelt=True)
        u0, v0, z0 = v.raum_zu_pixel(alt[a.name].x, alt[a.name].y, 0.0)
        u1, v1, z1 = v.raum_zu_pixel(neu_m[a.name].x, neu_m[a.name].y, 0.0)
        if z0 > 0.15 and z1 > 0.15 and not any(map(math.isnan, (u0, v0, u1, v1))):
            dr.line([(u0, v0), (u1, v1)], fill=GELB + (255,), width=lw + 1)
            winkel = math.atan2(v1 - v0, u1 - u0)
            sp = 14 + lw * 2
            dr.polygon([(u1, v1), (u1 - sp * math.cos(winkel - 0.45), v1 - sp * math.sin(winkel - 0.45)),
                        (u1 - sp * math.cos(winkel + 0.45), v1 - sp * math.sin(winkel + 0.45))], fill=GELB + (255,))
            r = 13 + lw * 2
            dr.ellipse((u0 - r, v0 - r, u0 + r, v0 + r), fill=(20, 20, 20, 210), outline=GELB + (255,), width=2)
            dr.text((u0, v0), str(nr), fill=(255, 255, 255, 255), font=schrift, anchor="mm")
    return np.asarray(erg_pil), np.asarray(erkl), legende


def zeichne_grundriss_vergleich(ax, v: Vermessung, neu: Layout, aenderungen: list):
    """Draufsicht: alte Positionen rot gestrichelt, neue Positionen gefüllt, Kamera als Dreieck."""
    from matplotlib.patches import Rectangle
    from .visualisierung import zeichne
    zeichne(neu, "", ax=ax, chi=True)
    alt = {m.name: m for m in v.layout.moebel}
    for nr, a in enumerate(aenderungen, 1):
        m = alt.get(a.name)
        if m is None:
            continue
        x1, y1, x2, y2 = m.rechteck
        ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, ec="#e63946", lw=2, ls="--", zorder=6))
        n = next(x for x in neu.moebel if x.name == a.name)
        ax.annotate("", xy=(n.x, n.y), xytext=(m.x, m.y), zorder=7,
                    arrowprops=dict(arrowstyle="->", color="#f4a261", lw=2.2))
        ax.text(m.x, m.y, str(nr), color="white", fontsize=8, ha="center", va="center", zorder=8,
                bbox=dict(boxstyle="circle,pad=0.25", fc="#222", ec="#f4a261"))
    kx, ky = v.kamera_pos
    ax.plot(kx, ky, marker="^", ms=10, color="#e63946", zorder=9)
    ax.annotate("", xy=(kx + v.kamera_blick[0] * 0.5, ky + v.kamera_blick[1] * 0.5), xytext=(kx, ky),
                arrowprops=dict(arrowstyle="->", color="#e63946", lw=1.6), zorder=9)
    ax.set_title("Grundriss: rot gestrichelt = jetzt, gefüllt = neu, ▲ = Kamera", fontsize=10.5)


def vorher_nachher(rgb: np.ndarray, erkl: np.ndarray, korrigiert: np.ndarray, legende: list[str],
                   score_vorher: float, score_nachher: float, datei: Optional[str] = None, zeigen: bool = True,
                   analyse_zeilen: Optional[list[str]] = None, nicht_pruefbar: Optional[list[str]] = None,
                   grundriss: Optional[tuple] = None):
    """Drei Bilder nebeneinander + Änderungen, Probleme mit Begründung und Grundriss."""
    import matplotlib.pyplot as plt
    import textwrap
    fig = plt.figure(figsize=(18, 11))
    gs = fig.add_gridspec(2, 3, height_ratios=[4.2, 3.8])
    for i, (b, t) in enumerate([(rgb, f"Vorher – Score {score_vorher:.0f}/100"),
                                (erkl, "Was sich ändert (rot = jetzt, grün = neu, gelb = Weg)"),
                                (korrigiert, f"Nachher – Score {score_nachher:.0f}/100")]):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(b)
        ax.set_title(t, fontsize=12.5, fontweight="bold")
        ax.axis("off")

    zeilen = ["UMSTELLEN:"] + (list(legende) if legende else ["Nichts muss umgestellt werden."]) + [""]
    zeilen += ["WAS NICHT GUT IST – UND WARUM (laut Buch):"] + (analyse_zeilen or ["Keine Probleme gefunden."])
    if nicht_pruefbar:
        zeilen += ["", "NICHT PRÜFBAR:"] + [f"? {n.split(':')[0]}" for n in nicht_pruefbar]
    text = []
    for z in zeilen:
        text += textwrap.wrap(z, 128, subsequent_indent="     ") or [""]
    ax = fig.add_subplot(gs[1, :2])
    ax.axis("off")
    ax.text(0.0, 1.0, "\n".join(text[:26]), va="top", fontsize=9.6, family="DejaVu Sans", linespacing=1.35)
    if grundriss is not None:
        zeichne_grundriss_vergleich(fig.add_subplot(gs[1, 2]), *grundriss)
    fig.tight_layout()
    if datei:
        fig.savefig(datei, dpi=120)
    if zeigen:
        plt.show()
    else:
        plt.close(fig)


# ------------------------------------------------------------------ Alles in einem Aufruf
def foto_korrigieren(pfad: str, raumtyp: str = "auto", ausgabe_ordner: str = "ausgabe",
                     bewohner=None, gewichte: Optional[dict] = None, kamera_in_ecke: bool = True,
                     foto_von_tuer: bool = False, bekannte_breite: Optional[float] = None,
                     preis_pro_meter: float = 4.0, zeigen: bool = True, profil: Optional[dict] = None):
    """Foto rein → analysiertes, korrigiertes Foto raus.

    profil: optionale Angaben (Farben, Licht, Bett …) – ergänzen, was das Foto nicht zeigt.

    raumtyp="auto" erkennt den Raum selbst (Bett -> Schlafzimmer, Sofa -> Wohnzimmer, WC -> Bad …).
    Speichert <name>_korrigiert.jpg (verschobene Möbel), <name>_aenderungen.jpg (Umrisse + Pfeile),
    <name>_vorher_nachher.png (alles nebeneinander mit Erklärung).
    """
    import os
    from PIL import Image
    from .foto3d import kamera_aus_foto, zimmer_aus_foto
    from .optimierer import korrigiere

    os.makedirs(ausgabe_ordner, exist_ok=True)
    v, erk, _ = zimmer_aus_foto(pfad, raumtyp, kamera_in_ecke=kamera_in_ecke, foto_von_tuer=foto_von_tuer,
                                bekannte_breite=bekannte_breite)
    if not any(not m.ist_wandobjekt and not m.ist_deckenobjekt for m in v.layout.moebel):
        raise ValueError("Keine Möbel erkannt – ist das ein Zimmerfoto? Bett, Sofa, Schreibtisch o. Ä. "
                         "sollten gut sichtbar sein.")
    _, rgb = kamera_aus_foto(pfad)
    ist = v.fuer_optimierer()
    if bewohner is not None:
        ist.bewohner = bewohner
    neu, e_neu, aenderungen, e_ist = korrigiere(ist, gewichte, preis_pro_meter=preis_pro_meter, ausgabe=False,
                                                zusatzkosten=v.unsichtbar_strafe)
    korr, erkl, legende = korrigiere_foto(rgb, v, neu, aenderungen)
    from .analyse import analysiere
    from .foto import foto_empfehlungen
    hinweise = [(h.stufe, h.regel, h.text) for h in
                foto_empfehlungen(erk, (rgb.shape[1], rgb.shape[0]), v.layout.raum.raumtyp)]
    from .foto import zu_profil
    profil_foto = {k: w for k, w in zu_profil(erk, v.layout.raum.raumtyp).items() if w is not None}
    profil_foto.update(profil or {})
    analyse = analysiere(ist, e_ist, neu, e_neu, aenderungen, hinweise, profil=profil_foto)
    stamm = os.path.splitext(os.path.basename(pfad))[0]
    dateien = {"korrigiert": os.path.join(ausgabe_ordner, f"{stamm}_korrigiert.jpg"),
               "aenderungen": os.path.join(ausgabe_ordner, f"{stamm}_aenderungen.jpg"),
               "vorher_nachher": os.path.join(ausgabe_ordner, f"{stamm}_vorher_nachher.png")}
    Image.fromarray(korr).save(dateien["korrigiert"], quality=92)
    Image.fromarray(erkl).save(dateien["aenderungen"], quality=92)
    vorher_nachher(rgb, erkl, korr, legende, e_ist.score, e_neu.score, datei=dateien["vorher_nachher"],
                   zeigen=zeigen, analyse_zeilen=analyse.kurz(7), nicht_pruefbar=analyse.nicht_pruefbar,
                   grundriss=(v, neu, aenderungen))
    return {"vermessung": v, "vorher": e_ist, "nachher": e_neu, "layout_neu": neu,
            "aenderungen": aenderungen, "legende": legende, "korrigiert": korr, "erklaerung": erkl,
            "raumtyp": v.layout.raum.raumtyp, "dateien": dateien, "analyse": analyse}
