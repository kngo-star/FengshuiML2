"""
>>> HIER DEIN ZIMMER EINTRAGEN <<<

Miss dein Zimmer aus (in Metern) und trage Türen, Fenster und Möbel ein.
Koordinaten: Ursprung (0,0) = linke untere Ecke in der Draufsicht.
    Wände: "unten" (y=0), "oben" (y=tiefe), "links" (x=0), "rechts" (x=breite)
    Öffnung `von` = Abstand vom Wandanfang (unten/oben: von links gemessen, links/rechts: von unten gemessen)

Möbelmaße: `breite` = quer zur Blickrichtung, `tiefe` = in Blickrichtung
           (beim Bett ist `tiefe` die Bettlänge, z.B. 2.0 m).
"""
from fengshui.modell import Balken, Bewohner, Layout, Moebel, Oeffnung, Raum, Schraege


def erstelle_layout() -> Layout:
    raum = Raum(
        name="Mein Zimmer",
        breite=3.6,
        tiefe=4.2,
        hoehe=2.5,
        raumtyp="schlafzimmer",      # schlafzimmer | buero | wohnzimmer | esszimmer | kinderzimmer | studio
        nord_wand="oben",            # welche Wand zeigt nach Norden? (None, wenn unbekannt)
        oeffnungen=[
            Oeffnung("tuer", wand="unten", von=0.2, breite=0.85),
            Oeffnung("fenster", wand="oben", von=1.0, breite=1.4, bruestung=0.9),
            Oeffnung("fenster", wand="rechts", von=2.2, breite=1.0, bruestung=0.9),
        ],
        balken=[
            # Balken(x1, y1, x2, y2)  – z.B. Balken(0, 2.0, 3.6, 2.2)
        ],
        schraege=None,               # z.B. Schraege(wand="links", hoehe_niedrig=1.2, laenge=1.5)
        altbau=False,
        aussenwaende=["oben", "rechts"],
    )

    moebel = [
        Moebel("bett", breite=1.4, tiefe=2.0, hoehe=0.5, name="Bett"),
        Moebel("nachttisch", breite=0.45, tiefe=0.4, hoehe=0.5, name="Nachttisch L",
               gehoert_zu="Bett", seite="links"),
        Moebel("nachttisch", breite=0.45, tiefe=0.4, hoehe=0.5, name="Nachttisch R",
               gehoert_zu="Bett", seite="rechts"),
        Moebel("schreibtisch", breite=1.2, tiefe=0.6, hoehe=0.75, name="Schreibtisch"),
        Moebel("schrank", breite=1.5, tiefe=0.6, hoehe=2.2, name="Kleiderschrank"),
        Moebel("pflanze", breite=0.4, tiefe=0.4, hoehe=1.0, name="Monstera", rund=True),
        Moebel("spiegel", breite=0.6, tiefe=0.04, hoehe=1.6, name="Spiegel"),
        # Beispiele für weitere Möbel:
        # Moebel("kommode", breite=1.0, tiefe=0.45, hoehe=0.8, name="Kommode"),
        # Moebel("regal", breite=0.8, tiefe=0.35, hoehe=1.0, name="Regal"),
        # Moebel("bild", breite=0.8, tiefe=0.03, name="Bild"),
        # Moebel("bank", breite=1.2, tiefe=0.4, hoehe=0.45, name="Bank", gehoert_zu="Bett", seite="vorne"),
        # Moebel("sofa", breite=2.0, tiefe=0.9, name="Sofa"),
        # Moebel("couchtisch", breite=1.0, tiefe=0.6, hoehe=0.4, name="Couchtisch",
        #        gehoert_zu="Sofa", seite="vorne", abstand=0.45),
        # Fest stehende Möbel (Einbauschrank) mit fest=True und x/y/rot angeben:
        # Moebel("schrank", breite=2.0, tiefe=0.6, hoehe=2.4, name="Einbau", x=1.0, y=3.9, rot=180, fest=True),
    ]

    bewohner = Bewohner(
        paar=False,
        sucht_partner=True,
        viele_bildschirme=False,
        arbeit_wichtiger_als_schlaf=False,
        pflanzen_sind_freunde=True,
    )
    return Layout(raum, moebel, bewohner)


# Für den Ausstattungs-Check (Farben, Licht, Bett, Ordnung …)
PROFIL = {
    "wandfarbe": "weiss",
    "akzentfarben": ["grün", "sand"],
    "lichtfarbe_kelvin": [2700, 4000],
    "leuchtmittel": "opal",
    "anzahl_lichtquellen": 2,
    "pendelleuchte_ueber_bett": False,
    "bettkopfteil": "gepolstert",
    "wasserbett": False,
    "bettwaesche_farbe": "hellgrau",
    "bett_unterbau_vollgestopft": False,
    "kleiderschrank": "freistehend",
    "kleiderschrank_vollgestopft": False,
    "uhr_im_raum": False,
    "smartphone_am_bett": True,
    "computer_im_raum": True,
    "pflanzenarten": ["monstera"],
    "kunstpflanzen": False,
    "notizzettel_an_wand": False,
    "unordnung": False,
    "persoenlichkeit": "ruhig",
    # ---- weitere Angaben für die Buch-Regelbasis (weglassen, wenn unbekannt) ----
    # "bett_typ": "normal",                 # "normal" | "niedrig" | "himmelbett"
    # "nachttisch_material": "holz",        # "glas" wird bemängelt
    # "bett_ungemacht": False,
    # "esstisch_material": "holz",          # "glas" wird bemängelt
    # "esstisch_form": "rund",              # "rund" | "oval" | "quadratisch" | "rechteckig" | "unregelmaessig"
    # "stuehle": "gleich",                  # "gleich" | "verschieden" | "plastik"
    # "schreibtisch_oberflaeche": "matt",   # "glaenzend" wird bemängelt
    # "offene_regale": False,
    # "buecher_liegend": False,
    # "schranktueren_glas": False,
    # "leuchten_form": "rund",              # "rund" | "kegel" | "eckig"
    # "deckenleuchte": "rund",              # "flach_eckig" wird bemängelt
    # "arbeitsleuchte_im_schlafzimmer": False,
    # "spots_auf_sitzplatz": False,
    # "fernseher_hoch_aufgehaengt": False,
    # "fernseher_ueber_kamin": False,
    # "familienfotos_hoch": False,
    # "kunst_als_fueller": False,
    # "bagua_spiegel_innen": False,
    # "windspiel_ueber_bett": False,
    # "spiegel_mangelhaft": False,          # gesprungen, verzerrt, Spiegelfliesen
    # "tote_pflanzen": False,
    # "wasser_stehend": False,
    # "aquarium_ungepflegt": False,
    # "messer_sichtbar": False,
    # "muell_sichtbar": False,
    # "wc_deckel_offen": False,
    # "wc_an_bettwand": False,
    # "bad_lueftung": True,
    # "eingang_dunkel": False,
    # "schuhe_herum": False,
    # "besen_muell_im_eingang": False,
    # "tuer_oeffnet_aussen": False,
    # "esstisch_leer": False,
}
