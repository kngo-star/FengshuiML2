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


def _kontur(maske: np.ndarray) -> list:
    import cv2
    k, _ = cv2.findContours(maske.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c[:, 0, :].tolist() for c in k if len(c) >= 3]


LAMA_URL = "https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt"
_LAMA = {}


def _lama(rgb: np.ndarray, maske: np.ndarray) -> np.ndarray:
    """LaMa (Large Mask Inpainting) – füllt große Lücken realistisch. Lädt ~200 MB beim ersten Mal."""
    import os
    import torch
    if "m" not in _LAMA:
        pfad = os.environ.get("LAMA_MODELL") or os.path.join(torch.hub.get_dir(), "big-lama.pt")
        if not os.path.exists(pfad):
            os.makedirs(os.path.dirname(pfad), exist_ok=True)
            torch.hub.download_url_to_file(LAMA_URL, pfad)
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
            print(f"  (LaMa nicht verfügbar: {fehler.__class__.__name__} – nutze OpenCV-Auffüllen)")
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
    plaene, nur_umriss, legende = [], [], []
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
    bewegt = {p["idx"] for p in plaene}
    for idx, msk in enumerate(v.masken):
        if idx in bewegt or v.erkennungen[idx].typ in ("fenster", "tuer", "teppich", "bild", "spiegel"):
            continue
        z = zentrum_tiefe(idx)
        vorne = msk & (belegt_tiefe > z + 0.1) & np.isfinite(belegt_tiefe)
        if vorne.any():
            bild[vorne] = rgb[vorne]

    # ---------- 5. Umrisse für gedrehte / nicht verschiebbare Möbel (auch im Ergebnisbild)
    erg_pil = Image.fromarray(bild)
    d_erg = ImageDraw.Draw(erg_pil)
    for nr, a in nur_umriss:
        pts = _box_ecken(v, neu_m[a.name])
        if pts:
            _zeichne_box(d_erg, pts, GRUEN, breite=max(2, W // 400), gestrichelt=True)
            d_erg.text(pts[4], f"{a.name}{' ↻ drehen' if a.gedreht else ''}", fill=GRUEN, font=_schrift(max(12, W // 60)))

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


def vorher_nachher(rgb: np.ndarray, erkl: np.ndarray, korrigiert: np.ndarray, legende: list[str],
                   score_vorher: float, score_nachher: float, datei: Optional[str] = None, zeigen: bool = True):
    """Drei Bilder nebeneinander + Liste der Änderungen."""
    import matplotlib.pyplot as plt
    import textwrap
    fig = plt.figure(figsize=(17, 6.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[5, 1.3])
    for i, (b, t) in enumerate([(rgb, f"Vorher – Score {score_vorher:.0f}/100"),
                                (erkl, "Was sich ändert (rot = jetzt, grün = neu)"),
                                (korrigiert, f"Nachher – Score {score_nachher:.0f}/100")]):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(b)
        ax.set_title(t, fontsize=12)
        ax.axis("off")
    ax = fig.add_subplot(gs[1, :])
    ax.axis("off")
    text = "\n".join(textwrap.shorten(l, 170) for l in legende) if legende else \
        "Alles gut – keine Möbel müssen verschoben werden."
    ax.text(0.01, 0.95, text, va="top", fontsize=10.5, family="DejaVu Sans")
    fig.tight_layout()
    if datei:
        fig.savefig(datei, dpi=130)
    if zeigen:
        plt.show()
    else:
        plt.close(fig)


# ------------------------------------------------------------------ Alles in einem Aufruf
def foto_korrigieren(pfad: str, raumtyp: str = "schlafzimmer", ausgabe_ordner: str = "ausgabe",
                     bewohner=None, gewichte: Optional[dict] = None, kamera_in_ecke: bool = True,
                     foto_von_tuer: bool = False, bekannte_breite: Optional[float] = None,
                     preis_pro_meter: float = 4.0, zeigen: bool = True):
    """Foto rein → analysiertes, korrigiertes Foto raus.

    Speichert: foto_korrigiert.jpg (verschobene Möbel), foto_aenderungen.jpg (Umrisse + Pfeile),
               foto_vorher_nachher.png (alles nebeneinander mit Erklärung).
    """
    import os
    from PIL import Image
    from .foto3d import kamera_aus_foto, zimmer_aus_foto
    from .optimierer import korrigiere

    os.makedirs(ausgabe_ordner, exist_ok=True)
    v, erk, _ = zimmer_aus_foto(pfad, raumtyp, kamera_in_ecke=kamera_in_ecke, foto_von_tuer=foto_von_tuer,
                                bekannte_breite=bekannte_breite)
    _, rgb = kamera_aus_foto(pfad)
    ist = v.fuer_optimierer()
    if bewohner is not None:
        ist.bewohner = bewohner
    neu, e_neu, aenderungen, e_ist = korrigiere(ist, gewichte, preis_pro_meter=preis_pro_meter, ausgabe=False)
    korr, erkl, legende = korrigiere_foto(rgb, v, neu, aenderungen)
    Image.fromarray(korr).save(os.path.join(ausgabe_ordner, "foto_korrigiert.jpg"), quality=92)
    Image.fromarray(erkl).save(os.path.join(ausgabe_ordner, "foto_aenderungen.jpg"), quality=92)
    vorher_nachher(rgb, erkl, korr, legende, e_ist.score, e_neu.score,
                   datei=os.path.join(ausgabe_ordner, "foto_vorher_nachher.png"), zeigen=zeigen)
    return {"vermessung": v, "vorher": e_ist, "nachher": e_neu, "layout_neu": neu,
            "aenderungen": aenderungen, "legende": legende, "korrigiert": korr, "erklaerung": erkl}
