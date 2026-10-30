"""Grundriss-Darstellung mit matplotlib."""
from __future__ import annotations

from typing import Optional

from . import geometrie as g
from .modell import Layout

FARBEN = {
    "bett": "#c9b79c", "nachttisch": "#a89070", "schreibtisch": "#9fb7a0", "sofa": "#b8a3c9",
    "sessel": "#cbb8dc", "couchtisch": "#d9cbb0", "schrank": "#8c8c8c", "kommode": "#a0a0a0",
    "regal": "#9a8478", "pflanze": "#5d9b5d", "spiegel": "#7fb3d5", "bild": "#e0a458",
    "wandregal": "#6d5a4e", "tv": "#333333", "esstisch": "#c2a278", "bank": "#bfae93",
    "konsole": "#b09a7e", "teppich": "#efe6d8", "stuhl": "#d4c4a8", "stehleuchte": "#f4d35e",
    "tischleuchte": "#f4d35e", "pendelleuchte": "#f4d35e", "herd": "#e76f51", "spuele": "#8ecae6",
    "kuehlschrank": "#bde0fe", "wc": "#e0e0e0", "badewanne": "#a2d2ff", "dusche": "#cde7f0",
    "waschbecken": "#bde0fe", "etagenbett": "#c9b79c",
}


def _kissen(ax, m):
    """Kopfkissen am Kopfteil – zeigt eindeutig, wo der Kopf liegt."""
    from matplotlib.patches import FancyBboxPatch
    hx, hy = m.hinten
    lang, tief = m.breite - 0.25, 0.32           # quer zum Bett, in Bettrichtung
    cx, cy = m.x + hx * (m.tiefe / 2 - 0.26), m.y + hy * (m.tiefe / 2 - 0.26)
    w, h = (lang, tief) if hy else (tief, lang)
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                fc="#fffaf2", ec="#8a7457", lw=1))


def _stuhl(ax, m):
    """Stuhl hinter dem Schreibtisch (Sitzfläche + Lehne) – zeigt eindeutig, auf welcher Seite man sitzt."""
    from matplotlib.patches import FancyBboxPatch
    px, py = g.personenpunkt(m)
    hx, hy = m.hinten
    a = 0.4
    ax.add_patch(FancyBboxPatch((px - a / 2, py - a / 2), a, a, boxstyle="round,pad=0,rounding_size=0.06",
                                fc="#e9f5f2", ec="#2a9d8f", lw=1.3))
    # Lehne auf der Seite, die vom Tisch weg zeigt
    lx, ly = px + hx * (a / 2), py + hy * (a / 2)
    if hy:
        ax.plot([px - a / 2, px + a / 2], [ly, ly], color="#2a9d8f", lw=4, solid_capstyle="round")
    else:
        ax.plot([lx, lx], [py - a / 2, py + a / 2], color="#2a9d8f", lw=4, solid_capstyle="round")


def zeichne(layout: Layout, titel: str = "", datei: Optional[str] = None, zeigen: bool = True,
            ax=None, chi: bool = True):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrow, Polygon, Rectangle

    raum = layout.raum
    eigene_figur = ax is None
    if eigene_figur:
        fig, ax = plt.subplots(figsize=(6.5, 6.5 * raum.tiefe / raum.breite + 0.6))
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), raum.breite, raum.tiefe, fill=False, lw=3, ec="#222"))

    # Chi-Bahnen Tür <-> Fenster
    if chi:
        for poly, faktor in g.chi_korridor(raum, mit_faktor=True):
            if len(poly) >= 3:
                ax.add_patch(Polygon(poly, closed=True, fc="#f4a261", alpha=0.16 * faktor, ec="none"))

    # Balken
    for b in raum.balken:
        ax.add_patch(Rectangle((min(b.x1, b.x2), min(b.y1, b.y2)), abs(b.x2 - b.x1), abs(b.y2 - b.y1),
                               fill=False, hatch="///", ec="#999", lw=0.8))
    # Dachschräge
    if raum.schraege:
        s = raum.schraege
        r = {"unten": (0, 0, raum.breite, s.laenge), "oben": (0, raum.tiefe - s.laenge, raum.breite, s.laenge),
             "links": (0, 0, s.laenge, raum.tiefe), "rechts": (raum.breite - s.laenge, 0, s.laenge, raum.tiefe)}[s.wand]
        ax.add_patch(Rectangle(r[:2], r[2], r[3], fc="#ddd", alpha=0.4, ec="none"))
        ax.text(r[0] + r[2] / 2, r[1] + r[3] / 2, "Schräge", ha="center", va="center", fontsize=7, color="#777")

    # Öffnungen
    for o in raum.oeffnungen:
        (ax1, ay1), (ax2, ay2) = o.endpunkte(raum)
        farbe = {"tuer": "#d62828", "balkontuer": "#7b2cbf", "fenster": "#0096c7", "schranktuer": "#999"}[o.typ]
        ax.plot([ax1, ax2], [ay1, ay2], color=farbe, lw=7, solid_capstyle="butt")
        if o.ist_tuer:
            z = g.tuer_schwenkbereich(o, raum)
            ax.add_patch(Rectangle((z[0], z[1]), z[2] - z[0], z[3] - z[1], fc=farbe, alpha=0.07, ec=farbe, ls=":"))

    # Möbel (Teppich zuerst)
    for m in sorted(layout.moebel, key=lambda m: (m.typ != "teppich", m.ist_deckenobjekt)):
        x1, y1, x2, y2 = m.rechteck
        farbe = FARBEN.get(m.typ, "#cccccc")
        if m.ist_deckenobjekt:          # Hängeleuchte: gestrichelter Kreis über allem
            from matplotlib.patches import Circle
            ax.add_patch(Circle((m.x, m.y), max(x2 - x1, 0.3) / 2, fc=farbe, alpha=0.35, ec="#b8860b", ls="--", lw=1.2))
            ax.text(m.x, m.y, m.name, ha="center", va="center", fontsize=5.5, color="#6b5000")
            continue
        if m.rund:
            from matplotlib.patches import Ellipse
            ax.add_patch(Ellipse((m.x, m.y), x2 - x1, y2 - y1, fc=farbe, ec="#333", lw=1))
        else:
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fc=farbe, ec="#333", lw=1, alpha=0.95))
        if m.typ == "bett":
            # Kopfteil hervorheben
            hx, hy = m.hinten
            if hy:
                yk = y2 if hy > 0 else y1
                ax.plot([x1, x2], [yk, yk], color="#5a4632", lw=4)
            else:
                xk = x2 if hx > 0 else x1
                ax.plot([xk, xk], [y1, y2], color="#5a4632", lw=4)
        if not m.ist_wandobjekt and m.typ not in ("pflanze", "teppich", "nachttisch", "stehleuchte", "tischleuchte"):
            vx, vy = m.vorne
            ax.add_patch(FancyArrow(m.x, m.y, vx * 0.25, vy * 0.25, width=0.02, head_width=0.09,
                                    head_length=0.07, color="#333"))
        groesse = 7 if min(x2 - x1, y2 - y1) > 0.4 else 5.5
        ax.text(m.x, m.y - 0.12 if not m.ist_wandobjekt else m.y, m.name, ha="center", va="center",
                fontsize=groesse, color="#111")
        if m.typ == "bett":
            _kissen(ax, m)
        elif m.typ == "schreibtisch":
            _stuhl(ax, m)
        elif m.typ == "sofa":
            px, py = g.personenpunkt(m)
            ax.plot(px, py, "o", ms=5, color="#2a9d8f")

    ax.set_xlim(-0.3, raum.breite + 0.3)
    ax.set_ylim(-0.3, raum.tiefe + 0.3)
    ax.set_xticks([])
    ax.set_yticks([])
    for wand, (x, y) in {"unten": (raum.breite / 2, -0.2), "oben": (raum.breite / 2, raum.tiefe + 0.2),
                         "links": (-0.2, raum.tiefe / 2), "rechts": (raum.breite + 0.2, raum.tiefe / 2)}.items():
        hr = raum.himmelsrichtung(wand)
        ax.text(x, y, wand + (f" ({hr})" if hr else ""), ha="center", va="center", fontsize=7, color="#666",
                rotation=90 if wand in ("links", "rechts") else 0)
    ax.set_title(titel, fontsize=10)
    if eigene_figur:
        fig.tight_layout()
        if datei:
            fig.savefig(datei, dpi=140)
        if zeigen:
            plt.show()
        else:
            plt.close(fig)
    return ax


def zeichne_mehrere(ergebnisse, datei: Optional[str] = None, zeigen: bool = True):
    import matplotlib.pyplot as plt
    n = len(ergebnisse)
    raum = ergebnisse[0][0].raum
    fig, axs = plt.subplots(1, n, figsize=(5 * n, 5 * raum.tiefe / raum.breite + 0.8))
    if n == 1:
        axs = [axs]
    for i, ((lay, erg), ax) in enumerate(zip(ergebnisse, axs)):
        zeichne(lay, f"Variante {i + 1}: Score {erg.score:.1f}", ax=ax)
    fig.tight_layout()
    if datei:
        fig.savefig(datei, dpi=140)
    if zeigen:
        plt.show()
    else:
        plt.close(fig)
