"""
Ausstattungs-Check (nicht-geometrische Regeln): Farben, Licht, Bett-Design, Pflanzen, Ordnung …

Du beschreibst dein Zimmer als Dictionary (siehe `BEISPIEL_PROFIL`) und bekommst
Empfehlungen aus der Wissensbasis zurück.
"""
from __future__ import annotations

from collections import Counter

from . import wissen as W
from .modell import Raum

BEISPIEL_PROFIL = {
    "wandfarbe": "weiss",                 # Farbname, siehe wissen.FARBE_ZU_ELEMENT
    "akzentfarben": ["grün", "terrakotta"],
    "lichtfarbe_kelvin": [2700, 4000],    # Kelvin aller Leuchtmittel im Raum
    "leuchtmittel": "klar",               # "opal" (diffus) | "klar"
    "anzahl_lichtquellen": 1,
    "pendelleuchte_ueber_bett": False,
    "bettkopfteil": "gepolstert",         # "massiv" | "gepolstert" | "gitter" | "keins"
    "wasserbett": False,
    "bettwaesche_farbe": "hellgrau",
    "bett_unterbau_vollgestopft": False,
    "kleiderschrank": "freistehend",      # "einbau" | "freistehend" | "mehrere"
    "kleiderschrank_vollgestopft": True,
    "uhr_im_raum": False,
    "smartphone_am_bett": True,
    "computer_im_raum": True,
    "pflanzenarten": ["monstera", "kaktus"],
    "kunstpflanzen": False,
    "notizzettel_an_wand": True,
    "unordnung": True,
    "religioese_objekte": False,
    "persoenlichkeit": "ruhig",           # "feurig" | "ruhig" | "gelangweilt"
}

OK, NEIN, INFO = "✓", "✗", "ℹ"


def pruefe_ausstattung(raum: Raum, profil: dict) -> list[tuple[str, str]]:
    erg: list[tuple[str, str]] = []
    rt = raum.raumtyp
    schlaf = rt in ("schlafzimmer", "gaestezimmer", "studio")

    # ---------------- Himmelsrichtung / Licht
    richtungen = [raum.himmelsrichtung(f.wand) for f in raum.fenster]
    richtungen = [r for r in richtungen if r]
    if raum.suedhalbkugel:
        richtungen = [{"N": "S", "S": "N"}.get(r, r) for r in richtungen]
    if richtungen:
        haupt = Counter(richtungen).most_common(1)[0][0]
        h = W.HIMMELSRICHTUNG[haupt]
        erg.append((INFO, f"Hauptfenster nach {haupt} ({h['jahreszeit']}, Element {h['element']}): {h['licht']}."))
        erg.append((INFO, f"Wandfarbe-Empfehlung: {h['wandfarbe']}; Kunstlicht abends: {h['kunstlicht_abends']}."))
        if rt in h["geeignet_fuer"]:
            erg.append((OK, f"Ausrichtung {haupt} passt gut zu einem {rt}."))
        if rt == "schlafzimmer" and haupt == "O":
            erg.append((INFO, "Ostlicht ist belebend – im Erwachsenen-Schlafzimmer Holz-Elemente sparsam einsetzen."))
    else:
        if raum.fenster:
            erg.append((INFO, "Gib `nord_wand` im Raum an, dann bekommst du Farb-/Lichtempfehlungen nach Himmelsrichtung."))
    if not raum.fenster:
        erg.append((NEIN, "Raum ohne Fenster: Nie als Schlafzimmer nutzen; zum Arbeiten nur kurz. "
                          "(Faustregel: Wo keine Pflanze überlebt, soll niemand schlafen.)"))
    elif schlaf and not raum.tueren:
        erg.append((NEIN, "Ein Raum braucht Tür UND Fenster auf verschiedenen Wänden, damit Chi fließen kann."))

    # ---------------- Farben
    wf = profil.get("wandfarbe")
    if wf:
        el = W.FARBE_ZU_ELEMENT.get(wf.lower())
        if wf.lower() in ("weiss", "weiß"):
            erg.append((INFO, "Weiß (Metall) ist keine neutrale Grundfarbe und wirkt leicht angespannt – "
                              "unsicher? Mittleres Grau ist vielseitiger."))
        if wf.lower() == "schwarz":
            erg.append((NEIN, "Nie reines Schwarz für Wände – sehr dunkles Blau oder Braun lässt das Auge ruhen."))
        if el == "feuer":
            erg.append((NEIN if schlaf else INFO, "Rote/orange Wand = viel Feuer. Entsättigen (Terrakotta); "
                                                  "zu viel Feuer stört den Schlaf."))
        if rt == "esszimmer" and wf.lower() in ("blau", "dunkelblau", "hellblau"):
            erg.append((NEIN, "Blau dämpft den Appetit – nicht im Esszimmer."))
        if schlaf and el in ("erde", None) and wf.lower() not in ("schwarz",):
            erg.append((OK, "Ruhige, natürliche Töne passen zum Schlafzimmer (Element Erde)."))
    alle_farben = [wf] + list(profil.get("akzentfarben", [])) if wf else list(profil.get("akzentfarben", []))
    elemente = {W.FARBE_ZU_ELEMENT.get(f.lower()) for f in alle_farben if f}
    elemente.discard(None)
    if elemente:
        fehlend = set(W.ELEMENTE) - elemente
        if fehlend:
            erg.append((INFO, "Farben decken die Elemente " + ", ".join(sorted(elemente)) +
                        " ab. Ergänze über Objekte/Materialien: " + ", ".join(sorted(fehlend)) +
                        " (alle fünf Elemente sollten vorhanden sein)."))

    pers = profil.get("persoenlichkeit")
    if pers == "feurig":
        erg.append((INFO, "Feurige Persönlichkeit: ein beruhigender Raum (Erde/Wasser) gleicht aus."))
    elif pers == "gelangweilt":
        erg.append((INFO, "Wenig Abwechslung im Leben? Feuer-Akzente (rote Details, klare Leuchtmittel) bringen Schwung."))

    # ---------------- Licht
    kel = profil.get("lichtfarbe_kelvin")
    if kel:
        kel = kel if isinstance(kel, list) else [kel]
        if len(set(kel)) > 1:
            erg.append((NEIN, f"Unterschiedliche Lichtfarben ({', '.join(map(str, sorted(set(kel))))} K) – "
                              "alle Leuchtmittel im Raum gleich wählen."))
        for k in set(kel):
            if k < W.LICHT["kelvin_minimum"]:
                erg.append((NEIN, f"{k} K ist zu orange – nicht unter 2500 K."))
            elif k >= W.LICHT["kelvin_tageslicht_ab"] and rt != "buero":
                erg.append((NEIN, f"{k} K imitiert Tageslicht und verwirrt die Sinne – Wohnräume 2700–2900 K."))
            elif W.LICHT["kelvin_wohnen"][0] <= k <= W.LICHT["kelvin_wohnen"][1]:
                erg.append((OK, f"{k} K ist ideal für Wohnräume."))
    if schlaf and profil.get("leuchtmittel") == "klar":
        erg.append((NEIN, "Im Schlafzimmer immer diffuses Licht (Opal-Leuchtmittel, Schirme)."))
    n = profil.get("anzahl_lichtquellen")
    if n is not None and n < 3:
        erg.append((NEIN, f"Nur {n} Lichtquelle(n): besser mehrere niedrige Lichtpunkte – 3 von 4 Ecken beleuchten, "
                          "eine Ecke im Schatten lassen."))
    if profil.get("pendelleuchte_ueber_bett"):
        erg.append((NEIN, "Keine schwere Leuchte über dem Bett – höchstens eine leichte Papierleuchte."))

    # ---------------- Bett
    if schlaf:
        kt = profil.get("bettkopfteil")
        if kt in ("keins", "gitter"):
            erg.append((NEIN, "Bett braucht ein massives oder gepolstertes Kopfteil (je breiter, desto besser)."))
        elif kt:
            erg.append((OK, "Massives/gepolstertes Kopfteil – gut (Schildkröte)."))
        if profil.get("wasserbett"):
            erg.append((NEIN, "Wasserbett unbedingt vermeiden."))
        bw = (profil.get("bettwaesche_farbe") or "").lower()
        if bw == "schwarz":
            erg.append((NEIN, "Bettwäsche: helle, ruhige Farben – wenn dunkel, dann nicht schwarz."))
        if profil.get("bett_unterbau_vollgestopft"):
            erg.append((NEIN, "Bettkasten nicht vollstopfen – Luft muss zirkulieren (sonst Feuchtigkeit)."))
        if profil.get("smartphone_am_bett") or profil.get("computer_im_raum"):
            erg.append((NEIN, "Elektronik aus dem Schlafzimmer; Computer nachts ausschalten, analoge Alternativen "
                              "(Wärmflasche statt Heizdecke)."))
        if profil.get("uhr_im_raum"):
            erg.append((NEIN, "Keine Uhr im Schlafzimmer (Zeitdruck)."))
        ks = profil.get("kleiderschrank")
        if ks == "mehrere":
            erg.append((NEIN, "Mehrere kleine Schränke = viele spitze Ecken. Besser ein großer oder Einbauschrank."))
        elif ks == "einbau":
            erg.append((OK, "Einbauschrank – ideal (ruhig, keine Ecken)."))
        if profil.get("kleiderschrank_vollgestopft"):
            erg.append((NEIN, "Vollgestopfter Kleiderschrank: kein Platz für jemand Neuen im Leben – ausmisten."))
        if profil.get("religioese_objekte"):
            erg.append((NEIN, "Religiöse Objekte besser ins Wohnzimmer, nicht in Linie mit dem Bett."))

    if rt == "esszimmer" and profil.get("uhr_im_raum"):
        erg.append((NEIN, "Keine Uhr im Esszimmer – Gesellschaft statt Eile."))

    # ---------------- Pflanzen
    for art in profil.get("pflanzenarten", []):
        a = art.lower()
        if a in W.PFLANZEN["empfohlen"]:
            erg.append((OK, f"{art}: {W.PFLANZEN['empfohlen'][a]}"))
        elif a in W.PFLANZEN["mit_vorsicht"]:
            erg.append((NEIN, f"{art}: {W.PFLANZEN['mit_vorsicht'][a]}"))
    if profil.get("kunstpflanzen"):
        erg.append((NEIN, "Kunstpflanzen vermeiden – lieber Mobile, Skulpturleuchte oder volle Obstschale."))
    if profil.get("pflanzenarten"):
        erg.append((INFO, "Pflanzen-Ort im " + rt + ": " + W.PFLANZEN["orte"].get(rt, "nahe Fenster, gruppiert")))

    # ---------------- Ordnung
    if profil.get("notizzettel_an_wand"):
        erg.append((NEIN, "Zettel/Postkarten an der Wand = Unordnung. Alles in EINE Pinnwand."))
    if profil.get("unordnung"):
        erg.append((NEIN, "Unordnung: Kategorien bilden (keine 'Sonstiges'-Kiste), alles an seinen Ort; "
                          "Stauraum im unteren Drittel, oben nur Deko."))

    erg.append((INFO, "Erster Eindruck: Gestalte den Raum so, dass er vom Eingang aus gut aussieht und das "
                      "Hauptmöbel (Bett/Schreibtisch/Sofa) den Blick verankert."))
    erg.append((INFO, "Kunst nur, wenn du sie liebst – nichts 'zum Füllen'. Landschaften wirken wie Fenster, "
                      "Porträts wie Spiegel."))
    return erg


def drucke_ausstattung(raum: Raum, profil: dict) -> str:
    return "\n".join(f"  {s} {t}" for s, t in pruefe_ausstattung(raum, profil))
