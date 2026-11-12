"""
Tests für „leeres Zimmer einrichten“: Produktkatalog, Shop-Links, Möbelauswahl nach Buchregeln,
Platzierung mit der Regelbasis und das Zeichnen ins Foto.

Das Foto wird für die Tests nachgebaut (fengshui/demo_zimmer.py) – so laufen sie ohne KI-Modelle.

Ausführen: in PyCharm `tests_ausfuehren.py` → Run   (oder im Terminal: python -m pytest tests)
"""
import os
import tempfile

import numpy as np

from fengshui.bewertung import bewerte
from fengshui.buchregeln import BUCHREGELN
from fengshui.einrichten import ELEMENTE, RAUMTYPEN, _plan, einrichten, richte_foto_ein, tuer_hinter_kamera
from fengshui.katalog import BUDGETS, STILE, lade_produkte, lade_shops, shop_links
from fengshui.modell import Bewohner, Layout, Moebel, Oeffnung, Raum

PRODUKTE = lade_produkte()
SCHNELL = dict(iterationen=1200, neustarts=3, ausgabe=False)


def raum(breite=4.0, tiefe=4.2, raumtyp="schlafzimmer"):
    return Raum("Test", breite, tiefe, raumtyp=raumtyp, oeffnungen=[
        Oeffnung("tuer", wand="unten", von=0.2, breite=0.9),
        Oeffnung("fenster", wand="oben", von=1.3, breite=1.4, bruestung=0.9)])


def leer(**kw):
    bewohner = {k: kw.pop(k) for k in list(kw) if k in ("paar", "pflanzen_sind_freunde")}
    return Layout(raum(**kw), [], Bewohner(**bewohner))


def typen(wuensche):
    return [PRODUKTE[w.pid].typ for w in wuensche]


# ------------------------------------------------------------------ Katalog
def test_katalog_ist_vollstaendig():
    buch = {r.id for r in BUCHREGELN}
    for p in PRODUKTE.values():
        assert p.name and p.suche and p.warum, p.id
        assert len(p.masse) == 3 and len(p.preis_chf) == 3, p.id
        assert list(p.preis_chf) == sorted(p.preis_chf), f"{p.id}: Preise müssen günstig ≤ mittel ≤ gehoben sein"
        assert p.element in ELEMENTE, f"{p.id}: unbekanntes Element {p.element}"
        for regel in p.buch:
            assert regel in buch, f"{p.id}: Buchregel {regel} gibt es nicht"
        for stil in STILE:
            assert "{" not in p.suchbegriff(stil), f"{p.id}: Platzhalter im Suchbegriff nicht ersetzt"
            assert len(p.farbe(stil)) == 3


def test_jedes_moebel_hat_eine_begruendung_aus_dem_buch():
    ohne = [p.id for p in PRODUKTE.values() if not p.buch]
    assert not ohne, f"Produkte ohne Buchregel: {ohne}"


# ------------------------------------------------------------------ Links
def test_links_ohne_partnerkennung_sind_normale_links():
    shops = lade_shops()
    for p in PRODUKTE.values():
        links = shop_links(p, shops)
        assert links and all(l.url.startswith("https://") for l in links), p.id
        assert not any(l.partner for l in links), "ohne Kennung darf nichts als Partnerlink gelten"


def test_amazon_kennung_macht_partnerlink():
    shops = lade_shops()
    shops["standard_shop"] = "amazon"
    shops["shops"]["amazon"]["parameter"]["tag"] = "meinname-21"
    link = shop_links(PRODUKTE["bett-140"], shops)[0]
    assert link.shop == "amazon" and link.partner
    assert "tag=meinname-21" in link.url and "k=Polsterbett" in link.url


def test_deeplink_vorlage_umschliesst_den_shoplink():
    shops = lade_shops()
    shops["shops"]["ikea"]["deeplink"] = "https://netzwerk.example/klick?p=123&url={url}"
    link = shop_links(PRODUKTE["sofa-2"], shops)[0]
    assert link.partner and link.url.startswith("https://netzwerk.example/klick?p=123&url=https%3A%2F%2Fwww.ikea.com")


def test_bestimmtes_produkt_wird_direkt_verlinkt():
    shops = lade_shops()
    shops["shops"]["amazon"]["parameter"]["tag"] = "meinname-21"
    p = lade_produkte()["sessel"]
    p.link = "https://www.amazon.de/dp/B000TEST00?th=1"
    links = shop_links(p, shops)
    assert links[0].direkt and links[0].partner and "tag=meinname-21" in links[0].url and "th=1" in links[0].url
    assert [l.shop for l in links].count("amazon") == 1


# ------------------------------------------------------------------ Auswahl nach Buchregeln
def test_schlafzimmer_ohne_pflanzen_spiegel_bildschirm():
    t = typen(_plan(raum(), Bewohner(), PRODUKTE))
    assert "bett" in t and t.count("nachttisch") == 2 and "schrank" in t
    assert not {"pflanze", "spiegel", "tv", "pendelleuchte"} & set(t), "gehört laut Buch nicht ins Schlafzimmer"
    assert "pflanze" in typen(_plan(raum(), Bewohner(pflanzen_sind_freunde=True), PRODUKTE))


def test_paar_bekommt_breiteres_bett():
    def bett(bewohner):
        return next(PRODUKTE[w.pid] for w in _plan(raum(), bewohner, PRODUKTE) if PRODUKTE[w.pid].typ == "bett")
    assert bett(Bewohner(paar=True)).masse[0] > bett(Bewohner()).masse[0]


def test_wohnzimmer_hat_sitzkreis_und_runden_couchtisch():
    w = _plan(raum(raumtyp="wohnzimmer"), Bewohner(), PRODUKTE)
    t = typen(w)
    assert "sofa" in t and "sessel" in t and "couchtisch" in t
    assert next(PRODUKTE[x.pid] for x in w if PRODUKTE[x.pid].typ == "couchtisch").rund
    assert "tv" not in typen(_plan(raum(raumtyp="wohnzimmer"), Bewohner(), PRODUKTE, mit_tv=False))


def test_esszimmer_runder_tisch_gerade_stuhlzahl():
    w = _plan(raum(raumtyp="esszimmer"), Bewohner(), PRODUKTE)
    t = typen(w)
    assert next(PRODUKTE[x.pid] for x in w if PRODUKTE[x.pid].typ == "esstisch").rund
    assert t.count("stuhl") % 2 == 0 and t.count("stuhl") >= 4
    assert t.count("pendelleuchte") == 1


def test_jeder_raumtyp_hat_einen_plan():
    for rt in RAUMTYPEN:
        assert _plan(raum(raumtyp=rt), Bewohner(), PRODUKTE), rt


# ------------------------------------------------------------------ Platzierung
def test_schlafzimmer_wird_machbar_eingerichtet():
    e = einrichten(leer(), seed=1, **SCHNELL)
    assert e.ergebnis.machbar, {k: s for k, s in e.ergebnis.strafen.items() if s > 0}
    assert e.ergebnis.score >= 70, e.ergebnis.score
    assert bewerte(e.layout).score == e.ergebnis.score
    assert [p.nr for p in e.positionen] == list(range(1, len(e.positionen) + 1))
    assert e.summe() > 0 and all(p.menge >= 1 for p in e.positionen)
    namen = {m.name for m in e.layout.moebel}
    assert all(n in namen for p in e.positionen for n in p.moebel if PRODUKTE[p.produkt.id].typ != "zubehoer")


def test_alle_fuenf_elemente_sind_vertreten():
    for rt in ("schlafzimmer", "wohnzimmer", "buero"):
        e = einrichten(leer(raumtyp=rt), seed=2, **SCHNELL)
        fehlt = [el for el in ELEMENTE if not e.elemente.get(el)]
        assert not fehlt, f"{rt}: Element fehlt: {fehlt}"


def test_runder_esstisch_stuehle_ueberlappen_nicht():
    e = einrichten(leer(raumtyp="esszimmer"), seed=3, **SCHNELL)
    assert e.ergebnis.strafen["H01"] == 0, e.ergebnis.befunde["H01"]
    stuehle = [m for m in e.layout.moebel if m.typ == "stuhl"]
    assert len(stuehle) == 4 and len({m.rot for m in stuehle}) == 4, "vier Stühle, rundherum verteilt"


def test_kleines_zimmer_laesst_unwichtiges_weg():
    e = einrichten(Layout(raum(2.6, 3.0), [], Bewohner()), seed=4, **SCHNELL)
    namen = {m.name for m in e.layout.moebel}
    assert "Bett" in namen, "das Hauptmöbel bleibt immer"
    assert e.ergebnis.machbar or e.hinweise, "entweder machbar oder ein ehrlicher Hinweis"
    gross = einrichten(leer(), seed=4, **SCHNELL)
    assert len(e.layout.moebel) <= len(gross.layout.moebel)


def test_vorhandene_moebel_bleiben_stehen():
    bett = Moebel("bett", 1.4, 2.0, 0.5, name="Mein Bett", x=3.3, y=3.0, rot=270)
    e = einrichten(Layout(raum(), [bett], Bewohner()), seed=5, **SCHNELL)
    m = e.layout.nach_name("Mein Bett")
    assert (m.x, m.y, m.rot) == (3.3, 3.0, 270), "vorhandenes Bett wurde verschoben"
    assert sum(1 for x in e.layout.moebel if x.typ == "bett") == 1, "kein zweites Bett kaufen"
    assert not any(p.produkt.typ == "bett" for p in e.positionen)
    assert "Mein Bett" not in e.neu


def test_bilder_haengen_nicht_uebereinander():
    from fengshui.einrichten import _wand_konflikte
    e = einrichten(leer(raumtyp="wohnzimmer", breite=4.5, tiefe=5.0), seed=6, **SCHNELL)
    assert _wand_konflikte(e.layout) == 0


# ------------------------------------------------------------------ Foto: nachgebautes leeres Zimmer
def test_demo_zimmer_wird_richtig_vermessen():
    from fengshui.demo_zimmer import demo_vermessung
    rgb, v, wahr = demo_vermessung()
    r = v.layout.raum
    assert abs(r.breite - wahr.breite) < 0.15 and abs(r.tiefe - wahr.tiefe) < 0.15, (r.breite, r.tiefe)
    assert r.tueren and r.fenster and not v.layout.moebel


def test_projektion_stimmt_mit_vermessung_ueberein():
    from fengshui.demo_zimmer import demo_vermessung
    from fengshui.render3d import Projektion
    _, v, _ = demo_vermessung()
    pr = Projektion(v, 1.0)
    for punkt in [(1.9, 2.2, 0.0), (3.0, 3.5, 1.2), (0.8, 3.9, 2.0)]:
        u, w, z = v.raum_zu_pixel(*punkt)
        p = pr.punkt(*punkt)
        assert abs(p[0] - u) < 1e-6 and abs(p[1] - w) < 1e-6 and abs(p[2] - z) < 1e-6


def test_leeres_foto_wird_eingerichtet_mit_einkaufsliste():
    from fengshui.demo_zimmer import demo_vermessung
    rgb, v, _ = demo_vermessung("wohnzimmer")
    with tempfile.TemporaryDirectory() as ordner:
        r = richte_foto_ein(rgb, v, "wohnzimmer", ausgabe_ordner=ordner, stamm="test", seed=7, **SCHNELL)
        for pfad in r["dateien"].values():
            assert os.path.getsize(pfad) > 500, pfad
        seite = open(r["dateien"]["einkaufsliste.html"], encoding="utf-8").read()
    e = r["einrichtung"]
    assert e.ergebnis.machbar
    geaendert = np.abs(r["bild"].astype(int) - r["foto"].astype(int)).sum(-1) > 30
    assert geaendert.mean() > 0.05, "im Foto wurden kaum Möbel gezeichnet"
    assert r["maske"].max() > 0.9 and np.isfinite(r["tiefe"]).any()
    assert any(p.im_foto for p in e.positionen if p.produkt.typ == "sofa"), "das Sofa sollte im Foto zu sehen sein"
    for p in e.positionen:
        assert p.produkt.name.split(",")[0] in seite, p.produkt.name
    assert seite.count("https://") >= len(e.positionen) and "Feng-Shui-Score" in seite
    assert "Werbelink" not in seite, "ohne Partner-Kennung keine Werbe-Kennzeichnung"


def test_tuer_hinter_der_kamera_wird_angenommen():
    from fengshui.demo_zimmer import demo_vermessung
    _, v, _ = demo_vermessung()
    v.layout.raum.oeffnungen = [o for o in v.layout.raum.oeffnungen if not o.ist_tuer]
    assert tuer_hinter_kamera(v) and v.layout.raum.haupttuer.wand in ("unten", "links")
    assert not tuer_hinter_kamera(v), "nur ergänzen, wenn keine Tür da ist"


def test_budget_und_stil_aendern_preis_und_suche():
    p = PRODUKTE["sofa-3"]
    assert p.preis("guenstig") < p.preis("mittel") < p.preis("gehoben")
    assert len({p.suchbegriff(s) for s in STILE}) == len(STILE)
    assert set(BUDGETS) == {"guenstig", "mittel", "gehoben"}
