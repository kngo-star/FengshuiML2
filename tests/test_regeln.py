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
    zufall = [bewerte(zufallslayout(basis, rng)).score for _ in range(30)]
    (lay, erg), *_ = optimiere(basis, iterationen=800, neustarts=2, seed=1, anzahl_ergebnisse=1, ausgabe=False)
    assert erg.machbar
    assert erg.score > max(zufall)


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
