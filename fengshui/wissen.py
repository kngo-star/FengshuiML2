"""
Wissensbasis (Fakten-Tabellen) – sinngemäß zusammengefasst aus dem Buch
(Form-Schule / "san he" Feng Shui, Kapitel 2–5).

Diese Tabellen werden von den Regeln (regeln.py) und vom Ausstattungs-Check
(ausstattung.py) benutzt. Du kannst sie frei erweitern.
"""

# ----------------------------------------------------------------------------
# Kapitel 2: Fünf Elemente
# ----------------------------------------------------------------------------
ELEMENTE = {
    "feuer": {
        "yin_yang": "yang",
        "farben": ["rot", "orange", "tieforange"],
        "form": "Dreieck / spitz",
        "richtung": "S",
        "jahreszeit": "Sommer",
        "bewegung": "aufwärts",
        "textur": "keine",
        "bedeutung": "Energie, Leidenschaft",
        "hinweis": "Sparsam einsetzen – kleine, kraftvolle Akzente. Ganze Wand rötlich? Dann entsättigen "
                   "(Richtung Terrakotta). Zu viel Feuer stört den Schlaf.",
    },
    "erde": {
        "yin_yang": "ausgeglichen (Mitte)",
        "farben": ["gelb", "hellbraun", "sand", "beige", "warmgrau", "terrakotta", "tan"],
        "form": "Quadrat",
        "richtung": "Mitte",
        "jahreszeit": None,
        "bewegung": "horizontal",
        "textur": "grob, roh",
        "bedeutung": "Balance, Ruhe, Erdung",
        "hinweis": "Für große Flächen geeignet, dann eher entsättigt (warmes Grau statt Gelb). Gelb regt den Appetit an.",
    },
    "metall": {
        "yin_yang": "yin",
        "farben": ["weiss", "hellgrau", "hellblaugrau", "silber", "gold"],
        "form": "Kreis / Kugel",
        "richtung": "W",
        "jahreszeit": "Herbst",
        "bewegung": "nach innen",
        "textur": "glänzend, glatt",
        "bedeutung": "Präzision, Verwandlung, Dichte",
        "hinweis": "Gut fürs Arbeitszimmer. Weiß ist KEINE neutrale Grundfarbe – ganze weiße Räume wirken leicht "
                   "angespannt. Unsicher? Lieber ein mittleres Grau.",
    },
    "wasser": {
        "yin_yang": "yin",
        "farben": ["schwarz", "dunkelblau", "dunkelgrau", "graublau"],
        "form": "fließend / unbestimmt",
        "richtung": "N",
        "jahreszeit": "Winter",
        "bewegung": "abwärts",
        "textur": "zufällig, weich",
        "bedeutung": "Fluss, Tiefe",
        "hinweis": "Nie reines Schwarz für Wände – sehr dunkles Blau/Braun. Schwarz nur als Akzent/Rahmen. "
                   "Blau dämpft den Appetit -> nicht im Esszimmer.",
    },
    "holz": {
        "yin_yang": "yang",
        "farben": ["grün", "hellblau", "gesättigtes blau"],
        "form": "stehendes Rechteck (vertikal)",
        "richtung": "O",
        "jahreszeit": "Frühling",
        "bewegung": "nach außen",
        "textur": "rau, vertikal verlaufend",
        "bedeutung": "Wachstum, Vitalität, Leben",
        "hinweis": "Über Pflanzen und Naturmaterialien zeigen. Grüne Wand nur sehr dezent (Grau mit Grünstich).",
    },
}

# Element-Zyklen (Kapitel 3)
ERZEUGUNG = {"holz": "feuer", "feuer": "erde", "erde": "metall", "metall": "wasser", "wasser": "holz"}
KONTROLLE = {"holz": "erde", "erde": "wasser", "wasser": "feuer", "feuer": "metall", "metall": "holz"}


def element_ausgleich(zu_viel: str) -> dict:
    """Was tun, wenn ein Element dominiert? (Element-Zyklen)"""
    zu_viel = zu_viel.lower()
    kontrolliert_von = [k for k, v in KONTROLLE.items() if v == zu_viel][0]
    geschwaecht_durch = ERZEUGUNG[zu_viel]          # das "Kind" zieht Energie ab
    return {
        "dominantes_element": zu_viel,
        "daempfen_mit": kontrolliert_von,
        "ableiten_mit": geschwaecht_durch,
        "beispiel": {
            "wasser": "Raum dunkel/kalt ohne Sonne: erdfarbener Boden als Basis, Metall-Kugeln/Ornamente, "
                      "Pflanzen (Holz) und ein paar warme Lichtakzente.",
            "erde": "Zu viel Braun/Gelb wirkt wie Wüste: lebendige grüne Pflanzen (Holz) ergänzen.",
            "feuer": "Zu viel Rot/Hitze: Wasser-Elemente (dunkle Blautöne, fließende Formen) bzw. Erde-Töne.",
            "holz": "Zu viel Grün/Vertikales: Metall (runde Formen, Weiß) und Feuer-Akzente.",
            "metall": "Zu viel Weiß/Kühles: Feuer-Akzente (warme Lampen), Wasser-Töne als Tiefe.",
        }[zu_viel],
        "merke": "Alle fünf Elemente sollten immer vorhanden sein – die Zyklen helfen nur bei der Gewichtung. "
                 "Deine eigene Persönlichkeit zählt mit: feurige Menschen brauchen evtl. einen ruhigen Raum.",
    }


FARBE_ZU_ELEMENT = {f: e for e, d in ELEMENTE.items() for f in d["farben"]}

# ----------------------------------------------------------------------------
# Kapitel 3: Himmelsrichtung des Raums / Hauptfensters
# (Südhalbkugel: N und S tauschen)
# ----------------------------------------------------------------------------
HIMMELSRICHTUNG = {
    "N": {
        "element": "wasser", "jahreszeit": "Winter",
        "licht": "nie direkte Sonne; indirekt, gleichmäßig, ruhig, kühl-bläulich",
        "geeignet_fuer": ["buero", "atelier"],
        "wandfarbe": "neutrale bis warme Töne (mehr Yang)",
        "fenster": "möglichst keine Abdeckungen, Licht frei hereinlassen",
        "kunstlicht_abends": "eher kräftig, um fehlende Tagesenergie auszugleichen",
    },
    "S": {
        "element": "feuer", "jahreszeit": "Sommer",
        "licht": "tagsüber dauerhaft starke, rohe Sonne",
        "geeignet_fuer": ["wohnzimmer", "eingang"],
        "wandfarbe": "eher lebendige Farben",
        "fenster": "robuste Pflanzen können das starke Chi abmildern",
        "kunstlicht_abends": "stimmungsvoll und sanft",
    },
    "O": {
        "element": "holz", "jahreszeit": "Frühling",
        "licht": "belebendes Morgenlicht, danach eher kühl",
        "geeignet_fuer": ["kinderzimmer", "schlafzimmer", "wintergarten"],
        "wandfarbe": "wärmere Töne",
        "fenster": "Holz-Elemente passen (aber: Holz = Wachstum, nicht ideal fürs Erwachsenen-Schlafzimmer)",
        "kunstlicht_abends": "etwas kräftiger",
    },
    "W": {
        "element": "metall", "jahreszeit": "Herbst",
        "licht": "reiche, orange-feurige Abendsonne",
        "geeignet_fuer": ["schlafzimmer"],
        "wandfarbe": "kühlere Farben zum Ausgleich",
        "fenster": "",
        "kunstlicht_abends": "sanftes Licht nach Sonnenuntergang",
    },
}

# ----------------------------------------------------------------------------
# Kapitel 4: Raumcharakter
# ----------------------------------------------------------------------------
RAUM_PROFIL = {
    "schlafzimmer": {
        "element": "erde (mehr als feuer)", "yin_yang": "yin",
        "stimmung": "neutral, beruhigend, horizontale Linien, natürliche Töne",
        "hauptmoebel": "bett",
        "lage_in_wohnung": "weit weg von der Wohnungstür, hinter Wohn-/Essbereich; nicht neben/über Küche; nicht direkt am Bad",
    },
    "kinderzimmer": {
        "element": "holz", "yin_yang": "mehr yang",
        "stimmung": "energischer, Pflanzen und Computer sind ok",
        "hauptmoebel": "bett",
        "lage_in_wohnung": "idealerweise Ostseite (Morgensonne = Wachstum)",
    },
    "buero": {
        "element": "je nach Ziel: Wachstum=grün/hellblau, Wohlstand=gold/satte Töne, Stabilität=erdig, "
                   "flexibel=schwarz/dunkelblau, präzise=weiß",
        "yin_yang": "yang",
        "stimmung": "hell, gleichmäßig beleuchtet, ordentlich",
        "hauptmoebel": "schreibtisch",
        "lage_in_wohnung": "Konzentration -> hinterer, ruhiger Teil; Publikumsverkehr -> vorne. Weg von Küche/Bad.",
    },
    "wohnzimmer": {
        "element": "lebendig / yang", "yin_yang": "yang",
        "stimmung": "einladend, Sitzkreis, Pflanzen, Spiegel, evtl. Aquarium",
        "hauptmoebel": "sofa",
        "lage_in_wohnung": "Mitte der Wohnung, von anderen Räumen aus sichtbar",
    },
    "esszimmer": {
        "element": "erde", "yin_yang": "yang",
        "stimmung": "hell, energiegeladen, Fülle (Tisch nie leer), keine Uhren",
        "hauptmoebel": "esstisch",
        "lage_in_wohnung": "zentral, neben der Küche, nicht in Sicht der Wohnungstür",
    },
}

# ----------------------------------------------------------------------------
# Kapitel 5: Licht
# ----------------------------------------------------------------------------
LICHT = {
    "kelvin_wohnen": (2700, 2900),
    "kelvin_minimum": 2500,
    "kelvin_buero_ok": 3500,
    "kelvin_tageslicht_ab": 4000,
    "regeln": [
        "Alle Leuchtmittel in einem Raum mit gleicher Farbtemperatur.",
        "Mehrere Lichtquellen statt eines einzelnen Deckenlichts.",
        "Drei von vier Raumecken beleuchten, eine Ecke bewusst im Schatten (Yin) lassen.",
        "Mehr Licht nahe den Fenstern und in aktiven Zonen, Durchgänge/Ecken dunkler.",
        "Schlafzimmer: immer diffuses Licht (Opal-/Milchglas, Schirme); keine Arbeits-/Spotleuchten.",
        "Yang-Räume (Wohnen/Essen) dürfen klare, funkelnde Leuchtmittel haben.",
        "Nur EINE Statement-Pendelleuchte pro Raum; nie über Sofa, Sitzplatz oder Bett, besser über Couch-/Esstisch.",
        "Pendel-/Deckenleuchten rund (Metall/Himmel) oder dreieckig/kegelig (Feuer) – keine eckigen.",
        "Spots auf Objekte/Kunst richten, nicht auf Sitzplätze oder beliebige Bodenstellen.",
        "Niedrige Decke / Dachschräge: Steh- oder Tischleuchten am niedrigen Ende 'heben' die Decke.",
        "Fensterlose Räume: weiches Licht an die Wände (Uplighter) statt hartem Zentrallicht.",
        "Arbeitsbereich: gleichmäßig hell; Tipp: starker Uplighter gegen weiße Decke = schattenfreies Licht.",
    ],
}

# ----------------------------------------------------------------------------
# Kapitel 5: Pflanzen
# ----------------------------------------------------------------------------
PFLANZEN = {
    "empfohlen": {
        "monstera": "großblättrig, rund, überall geeignet",
        "geldbaum": "großblättrig, rund, überall geeignet",
        "pilea": "großblättrig, rund, überall geeignet",
        "peperomia": "großblättrig, rund, überall geeignet",
        "farn": "weiches Laub, wirkt fruchtbar",
        "jadebaum": "rundblättrige Sukkulente – ok",
        "echeveria": "rundblättrige Sukkulente – ok",
        "orchidee": "Vier Edle: Frühling",
        "bambus": "Vier Edle: Sommer",
        "chrysantheme": "Vier Edle: Herbst (aber auch Trauerblume)",
        "pflaumenbluete": "Vier Edle: Winter / Hoffnung",
    },
    "mit_vorsicht": {
        "kaktus": "spitz, steht für unwirtliches Klima – nicht in die Wohnung (draußen ok, schützt)",
        "aloe vera": "spitzblättrig -> eher Feuer; nur in energiereichen Bereichen",
        "bogenhanf": "spitze Blätter = Feuer; nicht in ruhigen Räumen (Schlafzimmer)",
        "palme": "je nach Blattform: hängend = Holz/Wasser, nach oben spitz = Holz/Feuer -> Wohnzimmer/Küche",
        "dracaena": "wie Palme",
    },
    "vermeiden": {
        "kunstpflanze": "Ungleichgewicht, sammelt Staub – lieber Mobile, Skulpturleuchte oder Obstschale",
        "tote pflanze": "lieber gar keine Pflanze als eine tote",
    },
    "orte": {
        "schlafzimmer": "möglichst keine; wenn doch: als Gruppe direkt am Fenster, Bett so weit weg wie möglich",
        "wohnzimmer": "nicht verstreuen, sondern in Gruppen nahe den Fenstern",
        "esszimmer": "ja, wenn genug Licht",
        "buero": "ja (Wachstum), dort wo Tageslicht hinkommt",
        "kueche": "ja, vermittelt zwischen Feuer und Wasser – aber nicht direkt neben den Herd",
        "bad": "gut (Holz + Wasser), nur mit Fenster",
        "eingang": "breitblättrige Pflanzen, wenn genug Licht",
    },
}

# ----------------------------------------------------------------------------
# Kapitel 5: Spiegel
# ----------------------------------------------------------------------------
SPIEGEL = {
    "gut": ["Wohnzimmer (energiereich)", "Esszimmer (verdoppelt Essen/Fülle)",
            "Arbeitsplatz mit Rücken zur Tür (um die Tür zu sehen)", "abgestandene Räume ohne Leben",
            "fehlende Raumecke ergänzen (nicht im Schlafzimmer)"],
    "schlecht": ["Schlafzimmer (wenn, dann nicht vom Bett aus sichtbar, nie am Fußende)", "außen am Haus",
                 "lange Flure (außer seitlich)", "Küche (vor allem nicht auf den Herd gerichtet)",
                 "direkt gegenüber der Eingangstür", "so, dass er Fernseher oder Türen spiegelt",
                 "hinter dem eigenen Sitzplatz"],
    "qualitaet": ["regelmäßige Form", "zeigt die ganze Person ohne Lücken", "sauber, ohne Risse/Verzerrung",
                  "keine geteilten Spiegel (Spiegelfliesen)", "nicht zu hoch, nicht zu tief hängen"],
    "hinweis": "Glänzende schwarze Flächen (z.B. TV) wirken wie Spiegel.",
}

# ----------------------------------------------------------------------------
# Kapitel 5: Ordnung / Stauraum
# ----------------------------------------------------------------------------
STAURAUM = {
    "plan": {
        "arbeitszimmer": "Bücher, Schreibwaren (auch Kochbücher gehören ins Bücherregal!)",
        "schlafzimmer": "Kleidung",
        "bad": "Pflegeprodukte, Erste Hilfe",
        "abstellraum": "Werkzeug, Putzzeug",
        "kueche": "Kochutensilien",
        "esszimmer": "Besteck, Geschirr",
        "wohnzimmer": "Sammel- und Ausstellungsstücke",
    },
    "regeln": [
        "Alles kategorisieren, Unterkategorien bilden – keine 'Sonstiges'-Kisten.",
        "Unteres Drittel der Wandhöhe = Stauraum; obere zwei Drittel frei für Deko (Bilder, Lampen, Pflanzen).",
        "Keine hohen Bücherregale/Wandregale, keine hoch gestapelten Kisten.",
        "Zu viele Möbel sind auch Unordnung. Türen nie zustellen.",
        "Beschriftete Schranktüren statt Glastüren.",
        "Zettel, Postkarten, Haftnotizen nur innerhalb EINER Pinnwand.",
        "Papiere/Kartons außer Sicht und geordnet; Unbenutztes wegwerfen.",
    ],
}

# ----------------------------------------------------------------------------
# Kapitel 5: Symbolische Objekte (nur Symbole, keine Wunder!)
# ----------------------------------------------------------------------------
OBJEKTE = {
    "bagua_spiegel": "nie im Innenraum; Autor rät generell ab (unfreundliche Geste)",
    "kalebasse": "nimmt schlechte Energie auf, z.B. zwischen Bett und Wand zur Toilette",
    "drache": "sehr viel Energie -> Wohnzimmer, nicht Schlafzimmer/Bad",
    "geldfrosch": "nie direkt am Eingang",
    "fu_hunde": "paarweise am Eingang; von innen nach außen geschaut: Weibchen rechts, Männchen links",
    "mandarinenten": "paarweise, wo Liebe wachsen soll",
    "segelschiff": "Bug zeigt ins Haus (zieht Wohlstand herein)",
    "schildkroete": "hinterer Teil der Wohnung (Berg im Rücken)",
    "windspiel": "bremst Chi: viele Fenster, Durchgänge, Treppe vor der Tür; nie über Bett oder Schreibtisch; hohl ist am besten",
    "mobile": "sanfte Bewegung, beruhigend",
    "lavalampe": "überall ok, aber nicht im Schlafzimmer, wenn sie nachts unruhig ist",
    "uhr": "wo Eile/Präzision gewünscht ist; nicht in Ess- oder Schlafzimmer",
    "familienfotos": "gerahmt auf Beistelltischen nahe bei dir; nicht hoch aufgehängt, nie über Feuer/Kamin",
    "religioese_objekte": "im wichtigsten Raum (Wohnzimmer), nicht im Schlafzimmer, nicht auf dem Boden, nicht in Linie mit dem Bett",
    "aquarium": "Wohlstand & Energie – Büro/Wohnzimmer; nie Schlafzimmer; immer sauber halten",
    "wasser": "immer fließend, nie stehend; nicht 'über' dir; nicht im Schlafzimmer",
    "kristall_klar": "bei zu viel Chi (Tür auf Treppe/Bett) oder in fensterlosen Räumen aufhängen",
    "jade": "steht für Holz/Wachstum",
}

# ----------------------------------------------------------------------------
# Möbel-Formen & -Materialien (Kapitel 4)
# ----------------------------------------------------------------------------
MOEBEL_WISSEN = {
    "esstisch_form": ["rund (am besten)", "oval", "quadratisch (Erde)", "rechteckig (ok, Kopfenden beachten)",
                      "unregelmäßig / zusammengeschobene Tische vermeiden"],
    "esstisch_material": "Holz, Stein, Ton/Terrakotta gut; Glas vermeiden (sonst Tischdecke)",
    "esstisch_stuehle": "alle gleich, gerade Anzahl, keiner an den Ecken, stabil; Ersatzstühle aus dem Raum",
    "schreibtisch_form": "rechteckig = hartes Verhandeln, geschwungen = Kreativität; hell/naturfarben am besten; "
                         "spiegelnde Oberflächen = zu viel Energie",
    "bett_design": "massives oder gepolstertes Kopfteil (je breiter desto besser), stabiler Rahmen, kein Wasserbett, "
                   "niedrige Betten wirken ruhiger, Himmelbetten streng; Luft unter dem Bett, Bettkasten nicht vollstopfen",
    "bettwaesche": "helle, ruhige Farben; wenn dunkel, dann nicht schwarz; Bett morgens machen",
    "nachttische": "paarweise mit gleichem visuellem Gewicht, rund oder niedriger als die Matratze, geschlossen, nicht aus Glas",
    "kleiderschrank": "Einbauschrank > ein großer freistehender > mehrere kleine (viele Ecken); ordentlich, nicht vollgestopft",
    "sofa": "ein Hauptsofa + Sessel; L-Sofa durch Sessel diagonal ergänzen; nicht allein lassen",
}
