"""
Tests für die Paarvergleichs-Studie (fengshui/paarvergleich.py, paarvergleich.py)
und die Analyse der Regelkonflikte (fengshui/konflikte.py).

Die Statistik wird mit erfundenen Personen geprüft, deren „wahre“ Vorlieben wir kennen:
Findet die Auswertung sie wieder?
"""
import math
import os
import random
import tempfile

from fengshui.bewertung import bewerte
from fengshui.konflikte import analysiere_konflikte, relativer_score, score_aus_summe
from fengshui.paarvergleich import (Vergleich, bradley_terry, code_details, code_lesen, code_schreiben,
                                    konsistenz, lerne_gewichte, paarplan, uebereinstimmung, wilson)
from tests.test_regeln import bett, frei, layout, raum, schrank, schreibtisch


def _simuliere(staerke: dict[int, float], personen: int, paare: int, rng: random.Random) -> list[Vergleich]:
    out = []
    for p in range(personen):
        for l, r in paarplan(sorted(staerke), paare, 0, rng):
            p_links = 1 / (1 + math.exp(staerke[r] - staerke[l]))
            out.append(Vergleich(f"P{p}", l, r, 1.0 if rng.random() < p_links else 0.0))
    return out


def test_bradley_terry_findet_wahre_reihenfolge():
    wahr = {1: 1.5, 2: 0.8, 3: 0.2, 4: -0.4, 5: -0.9, 6: -1.2}
    geschaetzt = bradley_terry(_simuliere(wahr, 40, 15, random.Random(3)), sorted(wahr))
    assert sorted(wahr, key=lambda n: -geschaetzt[n]) == [1, 2, 3, 4, 5, 6]
    assert abs(sum(geschaetzt.values())) < 1e-6                 # Mittelwert 0
    assert all(abs(geschaetzt[n] - wahr[n] - (sum(geschaetzt.values()) - sum(wahr.values())) / 6) < 0.5
               for n in wahr)


def test_bradley_terry_ohne_sieg_bleibt_endlich():
    v = [Vergleich("A", 1, 2, 1.0), Vergleich("A", 1, 3, 1.0), Vergleich("A", 2, 3, 0.5)]
    s = bradley_terry(v, [1, 2, 3])
    assert all(math.isfinite(x) for x in s.values())
    assert s[1] > s[2] and s[1] > s[3]


def test_paarplan_ausgewogen_mit_kontrolle():
    plan = paarplan(list(range(1, 9)), 15, 2, random.Random(1))
    assert len(plan) == 17
    haupt = {frozenset(p) for p in plan[:15]}
    assert len(haupt) == 15                                       # keine doppelten Paare
    for a, b in plan[15:]:                                        # Wiederholungen: schon gesehen, Seiten getauscht
        assert (b, a) in plan[:15]


def test_antwort_code_hin_und_zurueck():
    code = code_schreiben("runde3", "KN", [(1, 2, 1.0), (3, 4, 0.0), (5, 6, 0.5)])
    runde, person, v = code_lesen(code)
    assert (runde, person) == ("runde3", "KN")
    assert [(x.gewinner, x.ergebnis) for x in v] == [(1, 1.0), (4, 1.0), (None, 0.5)]
    # Format aus dem HTML-Bogen: Kürzel~Vorwissen und Kommentar als 5. Feld
    html_code = "PV1|runde3|KN~etwas|2-1,3=4|Schrank%20vor%20Fenster%2C%20sonst%20ok"
    assert code_lesen(html_code)[1] == "KN"
    d = code_details(html_code)
    assert d == {"person": "KN", "vorwissen": "etwas", "kommentar": "Schrank vor Fenster, sonst ok"}


def test_konsistenz_und_einigkeit():
    v = [Vergleich("A", 1, 2, 1.0), Vergleich("A", 2, 1, 0.0),   # A: zweimal 1 → konsistent
         Vergleich("B", 1, 2, 0.0), Vergleich("B", 2, 1, 0.0)]   # B: erst 2, dann 1 → nicht
    assert konsistenz(v) == (1, 2)
    anteil, n = uebereinstimmung(v)
    assert n == 1 and anteil in (0.0, 1.0)


def test_wilson_intervall():
    lo, hi = wilson(70, 100)
    assert 0.6 < lo < 0.7 < hi < 0.8
    assert wilson(0, 0) == (0.0, 1.0)


def test_ml_findet_die_wichtige_regel():
    """Erfundene Personen achten nur auf Regel A. Das Modell muss A das größte Gewicht geben
    und besser vorhersagen als Buch-Gewichte, die A und B gleich gewichten."""
    rng = random.Random(7)
    merkmale = {n: {"A": rng.random(), "B": rng.random(), "C": rng.random()} for n in range(1, 9)}
    v = []
    for p in range(10):
        for l, r in paarplan(list(range(1, 9)), 20, 0, rng):
            diff = 4 * (merkmale[r]["A"] - merkmale[l]["A"])
            v.append(Vergleich(f"P{p}", l, r, 1.0 if rng.random() < 1 / (1 + math.exp(-diff)) else 0.0))
    g = lerne_gewichte(v, merkmale, {"A": 1.0, "B": 1.0, "C": 1.0})
    assert max(g["gewichte"], key=g["gewichte"].get) == "A"
    assert g["genauigkeit_modell"] >= g["genauigkeit_buch"]


def test_relativer_score_und_formel():
    assert relativer_score(50, 100) == 50 and relativer_score(120, 100) == 100 and relativer_score(5, 0) == 0
    lay = layout(raum(), frei(bett(), 2.0, 2.0, 180), frei(schreibtisch(), 3.2, 0.4, 0))
    erg = bewerte(lay)
    summe = sum(r.gewicht * erg.strafen[r.id] for r in erg.regeln if r.kategorie != "hart")
    assert abs(score_aus_summe(summe) - erg.score) < 1e-9        # gleiche Formel wie bewertung.py


def test_konfliktanalyse_liefert_belegte_ergebnisse():
    lay = layout(raum(), bett(), schreibtisch(), schrank())
    k = analysiere_konflikte(lay, iterationen=250, neustarts=1, max_regeln=2, fortschritt=lambda _: None)
    assert k.bestwert >= k.start_score - 1e-9                     # Analyse kann nur besser werden
    assert k.obergrenze >= k.bestwert - 1e-9
    for x in k.konflikte:
        assert x.art in ("raum", "konflikt", "suche")
        assert x.kostet_punkte >= 0
        if x.art != "raum":
            assert x.preis is not None                            # Preis ist durch einen Grundriss belegt
    assert "Regelkonflikte" in k.text() and "|" in k.markdown()


def test_bogen_enthaelt_daten():
    import paarvergleich
    with tempfile.TemporaryDirectory() as ordner:
        ziel = os.path.join(ordner, "bogen.html")
        paarvergleich.bogen_schreiben("testrunde", {1: "data:image/png;base64,AAAA", 2: "data:image/png;base64,BBBB"},
                                      ziel)
        with open(ziel, encoding="utf-8") as f:
            html = f.read()
    assert "/*DATEN*/" not in html and '"testrunde"' in html and "BBBB" in html
