"""
Produktkatalog + Shop-Links (Affiliate) + Einkaufsliste.

    produkte.json   Produkt-Typen mit Maßen, Suchbegriff, Richtpreis und Begründung aus der Regelbasis
    affiliate.json  deine Shops und Partner-Kennungen

Ehrlich gesagt, was diese Datei kann und was nicht:
  • Sie baut für jedes Produkt einen Link zum Shop. Ohne Partner-Kennung ist das ein ganz normaler Link.
  • Ein Link wird erst zum Partner-Link (Provision), wenn DU dich beim Partnerprogramm angemeldet und
    deine Kennung in affiliate.json eingetragen hast. Dann wird er automatisch als Werbelink gekennzeichnet.
  • Die Preise sind grobe Richtpreise (geschätzt), keine Live-Preise aus dem Shop.
"""
from __future__ import annotations

import html
import json
import os
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import parse_qsl, quote, quote_plus, urlencode, urlparse, urlunparse

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUKTE_DATEI = os.path.join(HIER, "produkte.json")
AFFILIATE_DATEI = os.path.join(HIER, "affiliate.json")

BUDGETS = ("guenstig", "mittel", "gehoben")

# Stil = Farbwelt. Jede Materialgruppe bekommt eine Farbe fürs Bild und ein Wort für die Shop-Suche.
# Das Buch empfiehlt fürs Schlafzimmer ruhige, natürliche Töne (Erde) – darum ist "natur" der Standard.
STILE: dict[str, dict[str, tuple[str, str]]] = {
    "natur": {
        "holz": ("#c6a67a", "Eiche"), "holz_hell": ("#e9e2d4", "weiss Eiche"), "stoff": ("#d9cdb8", "beige"),
        "stoff_akzent": ("#8e9c7c", "salbeigrün"), "stoff_dunkel": ("#4a5560", "anthrazit"),
        "textil": ("#e4dccb", "beige"), "metall": ("#c2a468", "Messing"),
    },
    "hell": {
        "holz": ("#e2d2b4", "Birke"), "holz_hell": ("#f1efea", "weiss"), "stoff": ("#d6d6d2", "hellgrau"),
        "stoff_akzent": ("#a9bcc9", "hellblau"), "stoff_dunkel": ("#6a7078", "grau"),
        "textil": ("#eceae4", "creme"), "metall": ("#d9d9d6", "weiss"),
    },
    "dunkel": {
        "holz": ("#7b5b45", "Nussbaum"), "holz_hell": ("#b9a58c", "Eiche dunkel"), "stoff": ("#8b8780", "taupe"),
        "stoff_akzent": ("#6f5a4b", "braun"), "stoff_dunkel": ("#3a3d44", "anthrazit"),
        "textil": ("#cfc5b4", "sand"), "metall": ("#3a3a3a", "schwarz"),
    },
}
FESTE_FARBEN = {"pflanze": "#4f8a4f", "leuchte": "#f3e3bd", "bild": "#e8e2d4", "spiegel": "#c9d9e2",
                "kork": "#c49a6c", "keramik": "#c97b57", "glas": "#f4f0df"}
ELEMENT_NAME = {"feuer": "Feuer", "erde": "Erde", "metall": "Metall", "wasser": "Wasser", "holz": "Holz"}


def hex_zu_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


@dataclass
class Produkt:
    id: str
    typ: str                      # Möbeltyp im Grundriss (bett, sofa …) oder "zubehoer"
    name: str
    masse: tuple[float, float, float]
    material: str
    element: str
    preis_chf: tuple[float, float, float]
    suche: str
    buch: tuple[str, ...] = ()
    warum: str = ""
    rund: bool = False
    shop: Optional[str] = None
    variante: Optional[str] = None
    link: str = ""

    def preis(self, budget: str = "mittel") -> float:
        return float(self.preis_chf[BUDGETS.index(budget)])

    def farbe(self, stil: str = "natur") -> tuple[int, int, int]:
        palette = STILE.get(stil, STILE["natur"])
        if self.material in palette:
            return hex_zu_rgb(palette[self.material][0])
        return hex_zu_rgb(FESTE_FARBEN.get(self.material, "#bdbdbd"))

    def suchbegriff(self, stil: str = "natur") -> str:
        palette = STILE.get(stil, STILE["natur"])
        woerter = {k: v[1] for k, v in palette.items()}
        try:
            return self.suche.format(**woerter)
        except (KeyError, IndexError):
            return self.suche


def lade_produkte(pfad: str = PRODUKTE_DATEI) -> dict[str, Produkt]:
    with open(pfad, encoding="utf-8") as f:
        roh = json.load(f)
    produkte = {}
    for d in roh["produkte"]:
        produkte[d["id"]] = Produkt(
            id=d["id"], typ=d["typ"], name=d["name"], masse=tuple(d["masse"]), material=d.get("material", ""),
            element=d.get("element", ""), preis_chf=tuple(d["preis_chf"]), suche=d["suche"],
            buch=tuple(d.get("buch", ())), warum=d.get("warum", ""), rund=bool(d.get("rund", False)),
            shop=d.get("shop") or None, variante=d.get("variante") or None, link=d.get("link", "") or "")
    return produkte


def lade_shops(pfad: str = AFFILIATE_DATEI) -> dict:
    with open(pfad, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ Links
@dataclass
class ShopLink:
    shop: str            # Schlüssel in affiliate.json
    name: str            # Anzeigename, z. B. "IKEA"
    url: str
    partner: bool        # True = Partner-Link (Provision) → muss als Werbung gekennzeichnet sein
    direkt: bool         # True = Link auf ein bestimmtes Produkt, False = Shop-Suche


def _mit_parametern(url: str, parameter: dict) -> tuple[str, bool]:
    """Hängt nicht-leere Partner-Parameter an die URL (z. B. Amazon: tag=deinname-21)."""
    aktiv = {k: str(v) for k, v in (parameter or {}).items() if str(v).strip()}
    if not aktiv:
        return url, False
    t = urlparse(url)
    q = [(k, v) for k, v in parse_qsl(t.query, keep_blank_values=True) if k not in aktiv]
    q += list(aktiv.items())
    return urlunparse(t._replace(query=urlencode(q))), True


def _partnerlink(url: str, shop_cfg: dict) -> tuple[str, bool]:
    url, p1 = _mit_parametern(url, shop_cfg.get("parameter", {}))
    vorlage = (shop_cfg.get("deeplink") or "").strip()
    if vorlage and "{url}" in vorlage:
        return vorlage.replace("{url}", quote(url, safe="")), True
    return url, p1


def shop_links(produkt: Produkt, shops: dict, stil: str = "natur") -> list[ShopLink]:
    """Alle Links zu einem Produkt – der erste ist der Hauptlink (Shop des Produkts bzw. Standard-Shop)."""
    cfg = shops.get("shops", {})
    if not cfg:
        return []
    haupt = produkt.shop if produkt.shop in cfg else shops.get("standard_shop")
    if haupt not in cfg:
        haupt = next(iter(cfg))
    reihenfolge = [haupt] + [s for s in cfg if s != haupt]
    q = quote_plus(produkt.suchbegriff(stil))
    links: list[ShopLink] = []
    if produkt.link.strip():                       # ein bestimmtes Produkt: Link gehört zum Shop mit passender Domain
        host = urlparse(produkt.link).netloc.lower()
        s = next((k for k, c in cfg.items() if c.get("domain") and c["domain"].lower() in host), None)
        url, partner = _partnerlink(produkt.link, cfg[s]) if s else (produkt.link, False)
        links.append(ShopLink(s or "direkt", cfg[s]["name"] if s else (host or "Shop"), url, partner, True))
        reihenfolge = [x for x in reihenfolge if x != s]
    for s in reihenfolge:
        url, partner = _partnerlink(cfg[s]["suche"].replace("{q}", q), cfg[s])
        links.append(ShopLink(s, cfg[s]["name"], url, partner, False))
    return links


# ------------------------------------------------------------------ Einkaufsliste
@dataclass
class Position:
    """Eine Zeile der Einkaufsliste: ein Produkt, das im Zimmer steht (oder Zubehör dazu)."""
    nr: int
    produkt: Produkt
    menge: int = 1
    moebel: list[str] = field(default_factory=list)   # Namen im Grundriss
    im_foto: bool = True                               # im Ergebnisfoto sichtbar?
    ort: str = ""                                      # z. B. "an der Wand oben, 1,2 m von links"

    def preis(self, budget: str) -> float:
        return self.menge * self.produkt.preis(budget)


def _masse_text(p: Produkt) -> str:
    b, t, h = p.masse
    if not (b or t or h):
        return ""
    if p.typ in ("bild", "spiegel", "pinnwand"):
        return f"{b * 100:.0f} × {h * 100:.0f} cm"
    if p.rund:
        return f"Ø {b * 100:.0f} cm, {h * 100:.0f} cm hoch"
    return f"{b * 100:.0f} × {t * 100:.0f} × {h * 100:.0f} cm"


def einkaufsliste_daten(positionen: list[Position], shops: dict, stil: str, budget: str) -> list[dict]:
    daten = []
    for pos in positionen:
        links = shop_links(pos.produkt, shops, stil)
        daten.append({
            "nr": pos.nr, "id": pos.produkt.id, "name": pos.produkt.name, "menge": pos.menge,
            "masse": _masse_text(pos.produkt), "element": pos.produkt.element, "buchregeln": list(pos.produkt.buch),
            "warum": pos.produkt.warum, "ort": pos.ort, "im_foto": pos.im_foto,
            "richtpreis_chf": pos.produkt.preis(budget), "summe_chf": pos.preis(budget),
            "links": [{"shop": l.name, "url": l.url, "partnerlink": l.partner, "direkt": l.direkt} for l in links],
        })
    return daten


def einkaufsliste_text(positionen: list[Position], shops: dict, stil: str, budget: str) -> str:
    z = ["EINKAUFSLISTE", "=" * 64]
    partner = False
    for d in einkaufsliste_daten(positionen, shops, stil, budget):
        z.append(f"{d['nr']:>2}. {d['menge']}× {d['name']}" + (f"  ({d['masse']})" if d["masse"] else ""))
        z.append(f"    ca. CHF {d['summe_chf']:.0f}" + (f"  ·  Regel {', '.join(d['buchregeln'])}" if d["buchregeln"] else ""))
        z.append(f"    Warum: {d['warum']}")
        for l in d["links"][:1]:
            partner = partner or l["partnerlink"]
            z.append(f"    {l['shop']}{' (Werbelink)' if l['partnerlink'] else ''}: {l['url']}")
        z.append("")
    z.append(f"Summe: ca. CHF {sum(p.preis(budget) for p in positionen):.0f}  (grobe Richtpreise, keine Live-Preise)")
    if partner:
        z.append(shops.get("kennzeichnung", "Werbelinks: Beim Kauf über diese Links erhalte ich eine Provision."))
    return "\n".join(z)


_CSS = """
:root{--bg:#f6f3ee;--karte:#fffdf9;--text:#26221d;--leise:#6f675c;--linie:#e2dccf;--akzent:#7a5c3a;--gruen:#4f7a55}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);
font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.seite{max-width:1080px;margin:0 auto;padding:28px 18px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:20px;margin:34px 0 12px}
.unter{color:var(--leise);margin:0 0 22px}
.bilder{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;align-items:start}
figure{margin:0;background:var(--karte);border:1px solid var(--linie);border-radius:12px;overflow:hidden}
figure img{display:block;width:100%;height:auto}figcaption{padding:8px 12px;font-size:14px;color:var(--leise)}
.kacheln{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0}
.kachel{background:var(--karte);border:1px solid var(--linie);border-radius:10px;padding:10px 14px}
.kachel b{display:block;font-size:22px}.kachel span{font-size:13px;color:var(--leise)}
.pos{display:grid;grid-template-columns:44px 1fr auto;gap:14px;background:var(--karte);border:1px solid var(--linie);
border-radius:12px;padding:14px 16px;margin:0 0 10px;align-items:start}
.nr{width:36px;height:36px;border-radius:50%;background:var(--akzent);color:#fff;font-weight:700;
display:flex;align-items:center;justify-content:center}
.pos h3{margin:0 0 2px;font-size:17px}.meta{font-size:13px;color:var(--leise);margin:0 0 6px}
.warum{margin:0;font-size:15px}.regel{display:inline-block;font:12px ui-monospace,Menlo,monospace;color:var(--akzent);
background:#f1e9dc;border-radius:4px;padding:1px 6px;margin:6px 4px 0 0}
.kauf{text-align:right;min-width:170px}.preis{font-weight:700;font-size:17px;white-space:nowrap}
.knopf{display:inline-block;margin-top:8px;background:var(--gruen);color:#fff;text-decoration:none;font-weight:600;
border-radius:8px;padding:8px 14px;white-space:nowrap}.knopf:hover{filter:brightness(1.08)}
.mehr{font-size:13px;margin-top:6px;color:var(--leise)}.mehr a{color:var(--akzent)}
.werb{font-size:11px;color:var(--leise);display:block;margin-top:3px}
.hinweis{background:var(--karte);border:1px solid var(--linie);border-left:4px solid var(--akzent);border-radius:8px;
padding:12px 16px;font-size:14px;margin:10px 0}.hinweis ul{margin:6px 0 0;padding-left:20px}
.elemente{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.el{background:var(--karte);border:1px solid var(--linie);border-radius:10px;padding:10px 14px;font-size:14px}
.el b{display:block;font-size:15px}
@media(max-width:640px){.pos{grid-template-columns:40px 1fr}.kauf{grid-column:1/-1;text-align:left}}
"""


def einkaufsliste_html(positionen: list[Position], shops: dict, stil: str, budget: str, titel: str,
                       untertitel: str = "", bilder: Optional[list[tuple[str, str]]] = None,
                       kacheln: Optional[list[tuple[str, str]]] = None, elemente: Optional[dict] = None,
                       hinweise: Optional[list[str]] = None) -> str:
    """Eine einzelne HTML-Seite: Vorher/Nachher-Bilder, nummerierte Produkte mit Begründung und Shop-Links."""
    e = html.escape
    daten = einkaufsliste_daten(positionen, shops, stil, budget)
    partner = any(l["partnerlink"] for d in daten for l in d["links"])
    t = [f"<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width,initial-scale=1'>",
         f"<title>{e(titel)}</title><style>{_CSS}</style></head><body><div class='seite'>",
         f"<h1>{e(titel)}</h1><p class='unter'>{e(untertitel)}</p>"]
    if bilder:
        t.append("<div class='bilder'>")
        for datei, text in bilder:
            t.append(f"<figure><img src='{e(datei)}' alt='{e(text)}'><figcaption>{e(text)}</figcaption></figure>")
        t.append("</div>")
    if kacheln:
        t.append("<div class='kacheln'>" + "".join(
            f"<div class='kachel'><b>{e(w)}</b><span>{e(n)}</span></div>" for n, w in kacheln) + "</div>")

    t.append("<h2>Einkaufsliste</h2>")
    if partner:
        t.append(f"<div class='hinweis'><b>Werbung.</b> {e(shops.get('kennzeichnung', ''))}</div>")
    for d in daten:
        haupt, rest = (d["links"][0] if d["links"] else None), d["links"][1:]
        meta = " · ".join(x for x in [d["masse"], d["ort"], "" if d["im_foto"] else "nicht im Foto sichtbar"] if x)
        regeln = "".join(f"<span class='regel'>{e(r)}</span>" for r in d["buchregeln"])
        t.append("<div class='pos'>")
        t.append(f"<div class='nr'>{d['nr']}</div>")
        t.append(f"<div><h3>{d['menge']}× {e(d['name'])}</h3><p class='meta'>{e(meta)}</p>"
                 f"<p class='warum'>{e(d['warum'])}</p>{regeln}</div>")
        kauf = f"<div class='kauf'><div class='preis'>ca. CHF {d['summe_chf']:.0f}</div>"
        if haupt:
            art = "Zum Produkt" if haupt["direkt"] else "Im Shop suchen"
            kauf += (f"<a class='knopf' href='{e(haupt['url'])}' target='_blank' rel='noopener sponsored'>"
                     f"{art}: {e(haupt['shop'])}</a>")
            if haupt["partnerlink"]:
                kauf += "<span class='werb'>Werbelink</span>"
        if rest:
            kauf += "<div class='mehr'>auch bei " + ", ".join(
                f"<a href='{e(l['url'])}' target='_blank' rel='noopener sponsored'>{e(l['shop'])}</a>"
                + ("*" if l["partnerlink"] else "") for l in rest) + "</div>"
        t.append(kauf + "</div></div>")
    summe = sum(p.preis(budget) for p in positionen)
    t.append(f"<div class='hinweis'><b>Summe: ca. CHF {summe:,.0f}</b>".replace(",", "’") +
             " – grobe Richtpreise (geschätzt), keine Live-Preise aus dem Shop. Maße vor dem Kauf nachmessen.</div>")

    if elemente:
        t.append("<h2>Die fünf Elemente im Raum</h2><div class='elemente'>")
        for el, namen in elemente.items():
            t.append(f"<div class='el'><b>{e(ELEMENT_NAME.get(el, el))}</b>{e(', '.join(namen) or '–')}</div>")
        t.append("</div>")
    if hinweise:
        t.append("<h2>Hinweise</h2><div class='hinweis'><ul>" + "".join(f"<li>{e(h)}</li>" for h in hinweise) +
                 "</ul></div>")
    if not partner:
        t.append("<div class='hinweis'>Die Links sind im Moment normale Shop-Links ohne Provision. "
                 "Partner-Kennungen trägst du in <code>affiliate.json</code> ein.</div>")
    t.append("<p class='unter' style='margin-top:26px'>Die Einrichtung folgt Feng-Shui-Regeln (Form-Schule). "
             "Das ist ein Gestaltungs-Regelwerk, keine wissenschaftlich belegte Wirkung.</p>")
    t.append("</div></body></html>")
    return "\n".join(t)
