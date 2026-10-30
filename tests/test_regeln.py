"""
Tests für die Regelbasis: Ist jede Regel richtig programmiert?

Idee: Für die wichtigsten Regeln bauen wir zwei kleine Testzimmer –
eines, das laut Buch eindeutig FALSCH ist, und eines, das eindeutig RICHTIG ist.
Die Regel muss beim falschen anschlagen und beim richtigen nicht.

Dazu kommen allgemeine Tests für ALLE Regeln (stürzt keine ab, Strafen im gültigen Bereich,
Verweise aus der Buch-Regelbasis zeigen auf existierende Prüfungen …) und Tests für den Optimierer.

Ausführen: in PyCharm `tests_ausfuehren.py` → Run   (oder im Terminal: python -m pytest tests)
"""
import random

from fengshui.bewertung import bewerte
from fengshui.buchregeln import BUCHREGELN
from fengshui.modell import Bewohner, Layout, Moebel, Oeffnung, Raum
from fengshui.optimierer import an_wand_setzen, kinder_platzieren, korrigiere, optimiere, zufallslayout
from fengshui.regeln import REGELN

REGEL = {r.id: r for r in REGELN}


# ------------------------------------------------------------------ Testzimmer bauen
def raum(breite=4.0, tiefe=4.0, raumtyp="schlafzimmer", oeffnungen=None, **kw):
    """Standard-Testzimmer 4 × 4 m: Tür unten links, Fenster oben in der Mitte (Brüstung 0.9 m)."""
    if oeffnungen is None:
        oeffnungen = [Oeffnung("tuer", wand="unten", von=0.2, breite=0.9),
                      Oeffnung("fenster", wand="oben", von=1.3, breite=1.4, bruestung=0.9)]
    return Raum("Test", breite, tiefe, raumtyp=raumtyp, oeffnungen=oeffnungen, **kw)


def bett():
    return Moebel("bett", breite=1.4, tiefe=2.0, hoehe=0.5, name="Bett")


def schreibtisch():
    return Moebel("schreibtisch", breite=1.2, tiefe=0.6, hoehe=0.75, name="Schreibtisch")


def schrank(name="Schrank"):
    return Moebel("schrank", breite=1.5, tiefe=0.6, hoehe=2.2, name=name)


def layout(r, *moebel, **bewohner):
    return Layout(r, list(moebel), Bewohner(**bewohner))


def an_wand(lay, m, wand, pos):
    """Möbel mit der Rückseite (Bett: Kopfteil) an `wand`, Mitte bei `pos`."""
    an_wand_setzen(m, lay, wand, pos)
    kinder_platzieren(lay)
    return lay


def frei(m, x, y, rot):
    m.x, m.y, m.rot = x, y, rot
    return m


def strafe(lay, regel_id):
    return min(1.0, sum(b.strafe for b in REGEL[regel_id].pruefe(lay)))


# ================================================================== HARTE REGELN
def test_H01_ueberlappung():
    r = raum()
    schlecht = layout(r, frei(bett(), 2.5, 2.0, 270), frei(schrank(), 2.5, 2.0, 0))
    gut = layout(r, frei(bett(), 3.0, 2.0, 270), frei(schrank(), 0.3, 2.0, 90))
    assert strafe(schlecht, "H01") > 0.9
    assert strafe(gut, "H01") == 0


def test_H02_alles_im_raum():
    r = raum()
    assert strafe(layout(r, frei(bett(), -0.2, 2.0, 90)), "H02") == 1.0
    assert strafe(layout(r, frei(bett(), 1.0, 2.0, 90)), "H02") == 0


def test_H03_tuer_geht_frei_auf():
    r = raum()   # Tür unten, x = 0.2 … 1.1
    assert strafe(layout(r, frei(schrank(), 0.75, 0.5, 0)), "H03") == 1.0
    assert strafe(layout(r, frei(schrank(), 3.2, 0.3, 0)), "H03") == 0


def test_H04_laufweg_zum_bett():
    r = raum()
    gut = an_wand(layout(r, b := bett()), b, "rechts", 2.5)
    # Drei Schränke bilden eine Wand quer durchs Zimmer – das Bett dahinter ist nicht erreichbar
    s1, s2, s3 = schrank("S1"), schrank("S2"), schrank("S3")
    for s in (s1, s2, s3):
        s.breite = 1.34
    schlecht = layout(r, frei(bett(), 2.0, 3.0, 270), frei(s1, 0.67, 1.6, 0), frei(s2, 2.0, 1.6, 0), frei(s3, 3.33, 1.6, 0))
    assert strafe(schlecht, "H04") == 1.0
    assert strafe(gut, "H04") == 0


def test_H05_platz_fuer_stuhl():
    r = raum()
    # Person sitzt auf der Rückseite des Tischs: Rücken 0.2 m vor der Wand → kein Platz für Stuhl
    eng = layout(r, frei(schreibtisch(), 3.0, 0.5, 0))
    weit = layout(r, frei(schreibtisch(), 3.0, 1.5, 0))
    assert strafe(eng, "H05") > 0.5
    assert strafe(weit, "H05") == 0


# ================================================================== KOMMANDOPOSITION
def test_K01_bett_kopfteil_an_der_wand():
    r = raum()
    an_der_wand = an_wand(layout(r, b := bett()), b, "rechts", 2.5)
    frei_im_raum = layout(r, frei(bett(), 2.0, 2.5, 270))     # Kopfteil 1 m vor der Wand
    assert strafe(an_der_wand, "K01") == 0
    assert strafe(frei_im_raum, "K01") > 0.9


def test_K02_kein_fenster_im_ruecken():
    r = raum()
    unter_fenster = an_wand(layout(r, b := bett()), b, "oben", 2.0)
    massive_wand = an_wand(layout(r, b := bett()), b, "rechts", 2.5)
    assert strafe(unter_fenster, "K02") > 0
    assert strafe(massive_wand, "K02") == 0


def test_K03_tuer_im_blick():
    r = raum()   # Tür unten links
    blick_zur_tuer = layout(r, frei(schreibtisch(), 2.0, 2.0, 180))   # Person schaut nach unten
    ruecken_zur_tuer = layout(r, frei(schreibtisch(), 0.65, 2.0, 0))  # Tür genau hinter der Person
    assert strafe(blick_zur_tuer, "K03") == 0
    assert strafe(ruecken_zur_tuer, "K03") == 1.0


def test_K04_fuesse_nicht_zur_tuer():
    r = raum()   # Tür unten x = 0.2 … 1.1
    sarg = an_wand(layout(r, b := bett()), b, "oben", 0.75)          # Fußende genau auf die Tür
    gut = an_wand(layout(r, b := bett()), b, "rechts", 2.5)
    assert strafe(sarg, "K04") >= 0.5
    assert strafe(gut, "K04") == 0


def test_K06_bett_weit_weg_von_der_tuer():
    r = raum()
    nah = an_wand(layout(r, b := bett()), b, "links", 1.2)
    fern = an_wand(layout(r, b := bett()), b, "rechts", 3.0)
    assert strafe(nah, "K06") > strafe(fern, "K06") + 0.3


def test_K07_bett_nicht_an_der_tuerwand():
    r = raum()
    tuerwand = an_wand(layout(r, b := bett()), b, "unten", 3.0)
    andere = an_wand(layout(r, b := bett()), b, "rechts", 2.5)
    assert strafe(tuerwand, "K07") == 1.0
    assert strafe(andere, "K07") == 0


def test_K10_bett_von_beiden_seiten_zugaenglich():
    r = raum()
    ecke = layout(r, frei(bett(), 3.3, 3.0, 270))   # Längsseite an der oberen Wand
    ecke.moebel[0].y = r.tiefe - 0.7
    mitte = an_wand(layout(r, b := bett()), b, "rechts", 2.2)
    assert strafe(ecke, "K10") > 0       # Bewohner sucht Partner → zählt deutlich
    assert strafe(mitte, "K10") == 0
    assert strafe(layout(r, *ecke.moebel, sucht_partner=True), "K10") > strafe(layout(r, *ecke.moebel), "K10")


def test_K13_schreibtisch_fenster_seitlich():
    r = raum()   # Fenster oben Mitte
    ins_fenster = layout(r, frei(schreibtisch(), 2.0, 3.0, 0))      # Person schaut direkt ins Fenster
    seitlich = layout(r, frei(schreibtisch(), 2.0, 2.0, 90))        # Fenster links von der Person
    assert strafe(ins_fenster, "K13") >= 0.6
    assert strafe(seitlich, "K13") == 0


def test_K14_keine_spitzen_ecken_aufs_bett():
    r = raum()
    b = an_wand(layout(r, bb := bett()), bb, "rechts", 2.5).moebel[0]
    mit_ecke = layout(r, b, frei(schrank(), 1.2, 2.8, 90))   # Schrankecke ragt nahe ans Bett
    ohne = layout(r, b)
    assert strafe(mit_ecke, "K14") > 0
    assert strafe(ohne, "K14") == 0


def test_K16_bett_mittig():
    r = raum()
    mittig = an_wand(layout(r, b := bett()), b, "rechts", 2.0)
    versetzt = an_wand(layout(r, b := bett()), b, "rechts", 3.2)
    assert strafe(mittig, "K16") == 0
    assert strafe(versetzt, "K16") > 0.3


# ================================================================== CHI
def test_C01_nicht_in_der_chi_bahn():
    # 5 m breit: Tür unten links, Fenster oben links → Chi-Bahn am linken Rand
    r = raum(breite=5.0, oeffnungen=[Oeffnung("tuer", wand="unten", von=0.3, breite=0.8),
                                     Oeffnung("fenster", wand="oben", von=0.3, breite=1.0, bruestung=0.9)])
    in_bahn = an_wand(layout(r, b := bett()), b, "links", 2.5)
    ruhig = an_wand(layout(r, b := bett()), b, "rechts", 2.5)
    assert strafe(in_bahn, "C01") > 0.3
    assert strafe(ruhig, "C01") < strafe(in_bahn, "C01") - 0.3


def test_C02_spiegel_spiegelt_nicht_das_bett():
    r = raum()
    b = an_wand(layout(r, bb := bett()), bb, "rechts", 2.5).moebel[0]
    sp_gegenueber = Moebel("spiegel", breite=0.6, tiefe=0.04, hoehe=1.6, name="Spiegel")
    an_wand_setzen(sp_gegenueber, layout(r), "links", 2.5)            # schaut genau aufs Bett
    sp_seitlich = Moebel("spiegel", breite=0.6, tiefe=0.04, hoehe=1.6, name="Spiegel")
    an_wand_setzen(sp_seitlich, layout(r), "rechts", 0.5)             # an der Kopfteilwand, vom Bett nicht sichtbar
    assert strafe(layout(r, b, sp_gegenueber), "C02") > strafe(layout(r, b, sp_seitlich), "C02") + 0.5


def test_C03_pflanze_am_fenster_nicht_am_bett():
    r = raum()
    b = an_wand(layout(r, bb := bett()), bb, "rechts", 1.5).moebel[0]
    am_bett = Moebel("pflanze", breite=0.4, tiefe=0.4, hoehe=1.0, name="Pflanze", rund=True, x=3.0, y=2.7)
    am_fenster = Moebel("pflanze", breite=0.4, tiefe=0.4, hoehe=1.0, name="Pflanze", rund=True, x=1.5, y=3.7)
    assert strafe(layout(r, b, am_bett), "C03") > strafe(layout(r, b, am_fenster), "C03") + 0.3


def test_S03_fenster_nicht_verstellen():
    r = raum()
    vor_fenster = an_wand(layout(r, s := schrank()), s, "oben", 2.0)
    an_wand_links = an_wand(layout(r, s := schrank()), s, "links", 2.0)
    assert strafe(vor_fenster, "S03") > 0
    assert strafe(an_wand_links, "S03") == 0


# ================================================================== ALLE REGELN
def test_regel_ids_eindeutig_und_vollstaendig():
    ids = [r.id for r in REGELN]
    assert len(ids) == len(set(ids)), "doppelte Regel-ID"
    for r in REGELN:
        assert r.titel and r.beschreibung and r.quelle, f"{r.id}: Titel/Beschreibung/Quelle fehlt"
        assert r.gewicht > 0, f"{r.id}: Gewicht muss > 0 sein"
        assert r.kategorie in {"hart", "kommando", "chi", "zonen", "stil"}, f"{r.id}: unbekannte Kategorie"


def test_buchregeln_verweisen_auf_existierende_pruefungen():
    """Jede Buchregel mit `grundriss:XYZ` muss auf eine echte Prüfung in regeln.py zeigen."""
    fehlend = [(b.id, p) for b in BUCHREGELN for p in b.pruefung
               if p.startswith("grundriss:") and p.split(":", 1)[1] not in REGEL]
    assert not fehlend, f"Verweise ins Leere: {fehlend}"


def _zufallslayouts(anzahl=25):
    from mein_zimmer import erstelle_layout
    basis = erstelle_layout()
    rng = random.Random(7)
    for raumtyp in ("schlafzimmer", "buero", "wohnzimmer", "kinderzimmer", "studio", "esszimmer"):
        b = basis.kopie()
        b.raum = Raum(**{**b.raum.__dict__, "raumtyp": raumtyp})
        for _ in range(anzahl // 5):
            yield zufallslayout(b, rng)


def test_alle_regeln_robust_und_im_gueltigen_bereich():
    """Keine Regel stürzt ab, Strafen sind 0…1, gleiche Eingabe = gleiches Ergebnis, das Layout bleibt unverändert."""
    for lay in _zufallslayouts():
        vorher = [(m.x, m.y, m.rot) for m in lay.moebel]
        for r in REGELN:
            if not r.gilt_fuer(lay.raum.raumtyp):
                continue
            b1 = r.pruefe(lay)
            b2 = r.pruefe(lay)
            for b in b1:
                assert 0 <= b.strafe <= 1.0 + 1e-9, f"{r.id}: Strafe {b.strafe} außerhalb 0…1"
                assert b.text, f"{r.id}: Befund ohne Text"
            assert [b.strafe for b in b1] == [b.strafe for b in b2], f"{r.id}: nicht deterministisch"
        assert vorher == [(m.x, m.y, m.rot) for m in lay.moebel], "Regel hat das Layout verändert"


# ================================================================== OPTIMIERER
def test_optimierer_findet_bessere_und_machbare_layouts():
    from mein_zimmer import erstelle_layout
    basis = erstelle_layout()
    rng = random.Random(3)
    zufall = [bewerte(zufallslayout(basis, rng)) for _ in range(60)]
    machbare = [e.score for e in zufall if e.machbar]
    (lay, erg), *_ = optimiere(basis, iterationen=1200, neustarts=2, seed=1, anzahl_ergebnisse=1, ausgabe=False)
    assert erg.machbar
    # Zufällig hingestellte Möbel verletzen fast immer eine harte Regel; falls doch eine machbar ist,
    # muss der Optimierer besser sein.
    assert not machbare or erg.score > max(machbare)


def test_korrektur_ohne_mini_verschiebungen_und_mit_begruendung():
    """Keine Verschiebung unter 30 cm (ohne Drehung), jede Änderung hat einen Grund,
    und die gemeldete Punktzahl passt zum zurückgegebenen Layout."""
    from mein_zimmer import erstelle_layout
    basis = erstelle_layout()
    for seed in (100, 105):
        ist, _ = optimiere(basis, iterationen=150, neustarts=1, seed=seed, anzahl_ergebnisse=1, ausgabe=False)[0]
        neu, e_neu, aenderungen, e_ist = korrigiere(ist, iterationen=500, neustarts=1, seed=seed, ausgabe=False)
        assert abs(bewerte(neu).score - e_neu.score) < 1e-6, "Punktzahl passt nicht zum Layout"
        assert e_neu.score >= e_ist.score - 1e-6 or (e_neu.machbar and not e_ist.machbar)
        for a in aenderungen:
            assert a.strecke >= 0.30 or a.gedreht or a.gruende[0].startswith("wandert mit"), f"Mini-Verschiebung: {a.text()}"
            assert a.gruende, f"Änderung ohne Grund: {a.text()}"


# ================================================================== MENSCHENVERSTAND (Lücken im Buch, aus Nutzer-Feedback Runde 1)
def spiegel():
    return Moebel("spiegel", breite=0.6, tiefe=0.04, hoehe=1.6, name="Spiegel")


def test_H08_schrank_steht_an_der_wand():
    r = raum()
    an_der_wand = an_wand(layout(r, s := schrank()), s, "links", 2.0)
    im_raum = layout(r, frei(schrank(), 1.0, 2.0, 90))         # Rückseite 0.7 m vor der linken Wand
    assert strafe(an_der_wand, "H08") == 0
    assert strafe(im_raum, "H08") == 1.0


def test_H09_spiegel_nicht_verdeckt():
    r = raum()
    sp = spiegel()
    an_wand_setzen(sp, layout(r), "links", 2.0)
    verdeckt = layout(r, sp, frei(schrank(), 0.5, 2.0, 90))    # Schrank direkt vor dem Spiegel
    sp2 = spiegel()
    an_wand_setzen(sp2, layout(r), "links", 2.0)
    s2 = an_wand(layout(r, s := schrank()), s, "rechts", 2.0).moebel[0]
    sichtbar = layout(r, sp2, s2)
    assert strafe(verdeckt, "H09") == 1.0
    assert strafe(sichtbar, "H09") == 0


def test_H10_kein_schrank_vor_dem_fenster():
    r = raum()   # Fenster oben Mitte
    vor_fenster = an_wand(layout(r, s := schrank()), s, "oben", 2.0)
    kommode = Moebel("kommode", breite=1.0, tiefe=0.45, hoehe=0.8, name="Kommode")
    niedrig = an_wand(layout(r, kommode), kommode, "oben", 2.0)   # niedrige Kommode unter dem Fenster ist ok
    assert strafe(vor_fenster, "H10") == 1.0
    assert strafe(niedrig, "H10") == 0


def test_H11_arbeitsplatz_frei():
    r = raum()
    tisch = frei(schreibtisch(), 2.0, 2.0, 0)                    # Person schaut nach oben
    blockiert = layout(r, tisch, frei(schrank(), 2.0, 2.6, 180))  # Schrank 0.3 m vor der Tischkante
    tisch2 = frei(schreibtisch(), 2.0, 2.0, 0)
    pflanze_weit = Moebel("pflanze", breite=0.4, tiefe=0.4, hoehe=1.0, name="Pflanze", rund=True, x=3.6, y=3.6)
    assert strafe(blockiert, "H11") == 1.0
    assert strafe(layout(r, tisch2, pflanze_weit), "H11") == 0


def test_herkunft_buch_oder_menschenverstand():
    """Jede Prüfung stammt aus dem Buch (und ist mit einer Buchregel verknüpft) oder ist als Menschenverstand markiert."""
    verknuepft = {p.split(":", 1)[1] for b in BUCHREGELN for p in b.pruefung if p.startswith("grundriss:")}
    for r in REGELN:
        assert r.herkunft in ("buch", "verstand"), r.id
        if r.herkunft == "buch":
            assert r.id in verknuepft, f"{r.id} heißt 'Buch', ist aber mit keiner Buchregel verknüpft"
        else:
            assert r.kategorie == "hart" or r.gewicht <= 1.0, f"{r.id}: Menschenverstand-Regeln sollen das Buch nicht übertönen"


def test_runde1_feedback_wird_erkannt():
    """Die Mängel, die Kevin in Runde 1 kommentiert hat, verletzen jetzt eine Regel."""
    import json
    import os
    from fengshui.modell import Layout as _L
    from mein_zimmer import erstelle_layout
    pfad = os.path.join(os.path.dirname(__file__), "..", "daten", "runde1_vorschlaege.json")
    with open(pfad, encoding="utf-8") as f:
        runde = json.load(f)
    erwartet = {2: "H08", 3: "H11", 5: "H11", 6: "H09", 7: "H10"}
    for v in runde["vorschlaege"]:
        if v["nr"] not in erwartet:
            continue
        lay = erstelle_layout()
        pos = {m["name"]: m for m in v["moebel"]}
        for m in lay.moebel:
            m.x, m.y, m.rot = pos[m.name]["x"], pos[m.name]["y"], pos[m.name]["rot"]
        assert strafe(lay, erwartet[v["nr"]]) > 0, f"Vorschlag {v['nr']}: {erwartet[v['nr']]} schlägt nicht an"


# ================================================================== PRÜFEN & GRADIENT BOOSTING
def test_regel_score_passt_zur_bewertung():
    """Der Score aus gespeicherten Merkmalen (zum Prüfen der Noten) ist derselbe wie die echte Bewertung."""
    from fengshui.ml import merkmale, regel_score
    from mein_zimmer import erstelle_layout
    lay, erg = optimiere(erstelle_layout(), iterationen=200, neustarts=1, seed=4, anzahl_ergebnisse=1, ausgabe=False)[0]
    assert abs(regel_score(merkmale(lay)) - erg.score) < 1e-6


def test_noten_aendern_die_regeln_nicht():
    """Grundsatz Buch + Menschenverstand: gespeicherte Noten dürfen die Gewichte nicht verändern."""
    from fengshui import ml
    assert ml.GEWICHTE_ANPASSEN is False
    assert ml.Personalisierung("gibt_es_nicht.json").gewichte is None


def test_surrogat_merkmale_vollstaendig():
    """Gradient-Boosting-Merkmale: feste Länge, passend zu den Namen, keine fehlenden Werte."""
    import numpy as np
    from fengshui.surrogat import merkmal_namen, merkmale as geo_merkmale
    from mein_zimmer import erstelle_layout
    basis = erstelle_layout()
    rng = random.Random(1)
    for _ in range(5):
        x = geo_merkmale(zufallslayout(basis, rng))
        assert len(x) == len(merkmal_namen(basis))
        assert np.all(np.isfinite(x))
