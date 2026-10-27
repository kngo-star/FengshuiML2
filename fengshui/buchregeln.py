"""
REGELBASIS DES BUCHS – vollständig, strukturiert, maschinenlesbar.

Jede Regel aus dem Buch (Form-Schule-Feng-Shui, Kapitel 2–5) ist hier als WENN-DANN-Regel erfasst,
sinngemäß und in eigenen Worten:

    id          eindeutige Kennung, z. B. "SZ-12"  (Kürzel = Kapitel/Raum)
    kapitel     wo die Regel im Buch steht
    thema       Unterthema (z. B. "Bett – Position")
    raeume      für welche Raumtypen sie gilt ("alle" = überall)
    objekte     welche Dinge sie betrifft (bett, tuer, spiegel …)
    wenn        Bedingung (die Situation)
    dann        Empfehlung (was zu tun ist)
    warum       Begründung aus dem Buch
    abhilfe     was du tun kannst, wenn du nicht umstellen kannst
    prio        1 = wichtig, 2 = mittel, 3 = klein
    pruefung    wie das Programm sie prüft:
                  "grundriss:K04"  → geometrische Prüfung in regeln.py
                  "foto:F02"       → Erkennung direkt im Foto (foto.py)
                  profil-Bedingung → aus deinen Angaben (Farben, Licht …), siehe `profil`
                  leer             → Tipp (wird im Bericht als Checkliste ausgegeben)
    profil      deklarative Bedingungen auf dem PROFIL-Dictionary, z. B.
                  [("leuchtmittel", "==", "klar")]  → Regel greift, wenn alle Bedingungen zutreffen

Diese Form ist für Menschen UND Programme lesbar: Die Analyse findet zu jedem Befund die passende
Buchregel, der Export (regeln_exportieren.py) erzeugt daraus regelbasis.md/.json, und das ML-Modul
lernt Gewichte pro Prüfung.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

SCHLAF = ("schlafzimmer", "kinderzimmer", "gaestezimmer", "studio")
WOHN = ("wohnzimmer", "studio")
ESS = ("esszimmer", "wohnzimmer", "studio", "kueche")
ALLE = ("alle",)


@dataclass
class BuchRegel:
    id: str
    kapitel: str
    thema: str
    raeume: tuple[str, ...]
    objekte: tuple[str, ...]
    wenn: str
    dann: str
    warum: str
    abhilfe: str = ""
    prio: int = 2
    pruefung: tuple[str, ...] = ()
    profil: list[tuple] = field(default_factory=list)
    info: bool = False          # True = Hinweis zum Raum (z. B. Himmelsrichtung), kein Fehler

    def gilt_fuer(self, raumtyp: str) -> bool:
        return "alle" in self.raeume or raumtyp in self.raeume

    @property
    def art(self) -> str:
        if any(p.startswith("grundriss:") for p in self.pruefung):
            return "grundriss"
        if any(p.startswith("foto:") for p in self.pruefung):
            return "foto"
        if self.profil:
            return "profil"
        return "tipp"


BUCHREGELN: list[BuchRegel] = []


def R(id, kapitel, thema, raeume, objekte, wenn, dann, warum, abhilfe="", prio=2, pruefung=(), profil=None,
      info=False):
    BUCHREGELN.append(BuchRegel(id, kapitel, thema, tuple(raeume), tuple(objekte), wenn, dann, warum, abhilfe,
                                prio, tuple(pruefung), list(profil or []), info))


# =====================================================================================================
# KAPITEL 1–2: GRUNDLAGEN
# =====================================================================================================
K = "1–2 Grundlagen"
R("GL-01", K, "Gefühl zuerst", ALLE, (),
  "eine Regel fühlt sich für dich falsch oder unangenehm an",
  "die Regel beiseitelegen und dem eigenen Gefühl folgen",
  "Feng Shui ist gesunder Menschenverstand: Ein Raum soll sich gut anfühlen. Was sich falsch anfühlt, ist nicht "
  "im Sinne von Feng Shui.", "Mit lernen.py deine persönlichen Gewichte trainieren.", 2)
R("GL-02", K, "Yin und Yang", ALLE, (),
  "ein Raum ist nur ruhig/dunkel (Yin) oder nur hell/energiegeladen (Yang)",
  "Gegensätze ausbalancieren – nie das eine ohne das andere",
  "Alles ist Yin oder Yang; ein ausgewogener Raum braucht beides (z. B. abends weiches Licht nach dem hellen Tag).",
  "Ruhige Räume mit etwas Licht/Leben ergänzen, lebhafte Räume mit ruhigen Ecken.", 2)
R("GL-03", K, "Fünf Elemente", ALLE, ("farben", "materialien"),
  "Farben und Materialien zeigen nur einzelne der fünf Elemente",
  "alle fünf Elemente (Feuer, Erde, Metall, Wasser, Holz) im Raum vertreten haben",
  "Die Elemente sind immer verbunden; wo eines ist, sollen auch die anderen vier sein.",
  "Fehlende Elemente über Objekte ergänzen: Holz = Pflanzen, Feuer = warmes Licht/rote Akzente, Erde = "
  "Naturtöne, Metall = runde Formen/Weiß, Wasser = dunkle Blautöne/fließende Formen.", 3,
  profil=[("elemente_fehlen", "wahr", None)])
R("GL-04", K, "Elementzyklen", ALLE, ("farben",),
  "ein Element dominiert stark (z. B. dunkler, kalter Raum = zu viel Wasser)",
  "mit den Element-Zyklen ausgleichen statt nur das Gegenteil hinzuzufügen",
  "Zu viel von einem Element bringt Ungleichgewicht; die Zyklen zeigen, was dämpft oder ableitet.",
  "Zu viel Wasser: erdiger Boden, Metallkugeln, Pflanzen; zu viel Erde (Braun/Gelb): grüne Pflanzen.", 3)
R("GL-05", K, "Persönlichkeit", ALLE, (),
  "die Persönlichkeit ist sehr feurig bzw. das Leben eher langweilig",
  "den Raum gegensätzlich ausgleichen (feurig → beruhigend, langweilig → etwas Feuer)",
  "Auch deine eigene Energie gehört zur Balance des Raums.", "", 3,
  profil=[("persoenlichkeit", "in", ["feurig", "gelangweilt"])], info=True)
R("GL-06", K, "Chi: Lebens-Chi", ALLE, ("pflanzen", "fenster"),
  "ein Raum wirkt leblos",
  "Lebens-Chi (Sheng) hineinbringen: Licht, Luft, sanfte Bewegung, Pflanzen",
  "Sheng-Chi ist Wachstum und Leben – wie ein dichter Wald.", "Pflanzen, Mobile, frische Luft.", 3)
R("GL-07", K, "Chi: totes Chi", ALLE, (),
  "ein Raum ist stickig, staubig, unbewegt (auch wenn er hell ist)",
  "Stillstand vermeiden: lüften, ausmisten, Bewegung hineinbringen",
  "Totes Chi (Si) ist stagnierende Stille, wie in einem verlassenen Haus.", "Lüften, aufräumen, Mobile.", 2,
  profil=[("unordnung", "wahr", None)])
R("GL-08", K, "Chi: tötendes Chi", ALLE, ("ecken", "balken", "leuchten"),
  "spitze Ecken, Balken, schwere Hängeleuchten oder Schrägen zeigen auf dich",
  "solche Strukturen nicht auf Bett, Sofa oder Arbeitsplatz richten",
  "Tötendes Chi (Sha) ist wie ein Messer, das auf dich zeigt: Es wirkt bedrohlich und schwer, auch wenn es dich "
  "nie berührt. Je spitzer der Winkel, desto feindseliger.",
  "Runde Möbel, Ecken mit Pflanzen abmildern, Balken in Deckenfarbe streichen.", 1,
  pruefung=("grundriss:K14", "grundriss:K08"))
R("GL-09", K, "Chi: Bewegungs-Chi", ALLE, ("tuer", "flur"),
  "lange, gerade Wege oder Flure führen durch den Raum",
  "sanfte Kurven statt gerader Linien; je länger gerade, desto stärker das Chi – schlecht zum Schlafen",
  "Bewegungs-Chi fließt entlang von Wegen; gerade Bahnen machen es schnell und unruhig.",
  "Möbel, Teppiche oder Pflanzen so stellen, dass der Weg leicht mäandert.", 2,
  pruefung=("grundriss:C01", "grundriss:K15"))
R("GL-10", K, "Eine Öffnung", ALLE, ("tuer", "fenster"),
  "Chi soll durch dieselbe Öffnung hinein- und hinausfließen (Raum nur mit Tür, ohne Fenster)",
  "ein Raum braucht eine Tür und ein Fenster auf verschiedenen Wänden",
  "Chi kann nicht durch dieselbe Öffnung herein und hinaus – sonst entsteht Stillstand.",
  "Fensterlose Räume nur kurz nutzen; gut lüften, Licht an die Wände.", 1, pruefung=("grundriss:C08",))
R("GL-11", K, "Ein- und Ausgang", ALLE, ("tuer", "fenster"),
  "Eingang und Ausgang (Tür/Fenster) liegen sich genau gegenüber",
  "nicht in der direkten Bahn zwischen beiden sitzen oder schlafen",
  "Liegen Ein- und Ausgang in einer Linie, schneidet das Chi schnell durch den Raum.",
  "Paravent, Pflanze oder Möbel in die Bahn stellen.", 1, pruefung=("grundriss:C01",))
R("GL-12", K, "Ein- und Ausgang nah", ALLE, ("tuer", "fenster"),
  "Eingang und Ausgang liegen sehr nah beieinander",
  "die hinteren Raumteile bewusst beleben",
  "Liegen die Öffnungen dicht beieinander, erreicht das Chi die Tiefe des Raums nicht.",
  "Licht, Pflanzen oder Spiegel in den hinteren Bereich.", 3)
R("GL-13", K, "Große Räume", ALLE, (),
  "ein Raum ist sehr groß",
  "in Zonen gliedern; Bereiche zwischen den Öffnungen gezielt nutzen",
  "In großen Räumen erreicht das Chi nur die Flächen zwischen den Öffnungen; man fühlt sich leicht verloren.",
  "Teppiche und Möbelgruppen schaffen Zonen.", 3)
R("GL-14", K, "Fünf Tiere: Schildkröte", ALLE, ("wand", "bett", "sofa", "schreibtisch"),
  "hinter Bett, Sofa oder Arbeitsplatz ist offener Raum",
  "eine feste Wand oder hohe Lehne in den Rücken (Schildkröte = Schutz)",
  "Die Schildkröte mit ihrem Panzer steht für Schutz und Stabilität dort, wo wir nicht hinsehen.",
  "Hohes Kopfteil, Konsole hinter dem Sofa, Stuhl mit hoher Lehne.", 1, pruefung=("grundriss:K01",))
R("GL-15", K, "Fünf Tiere: Vogel", ALLE, ("bett", "sofa", "schreibtisch"),
  "vor dir ist eine Wand oder es ist eng",
  "Offenheit und Weitblick nach vorne (Vogel)",
  "Der Vogel braucht Raum vor sich, um vorauszuschauen und zu planen.",
  "Platz vor Bett/Sofa frei lassen; vor einer Wand Bilder oder Pinnwand.", 2, pruefung=("grundriss:K12",))
R("GL-16", K, "Fünf Tiere: Drache und Tiger", ALLE, ("bett", "sofa"),
  "links und rechts fehlt jede Unterstützung",
  "seitlichen Halt geben (Armlehnen, Nachttische, Beistelltische)",
  "Drache und Tiger sind wie die Armlehnen eines Sessels: Schutz und Wachstum zu beiden Seiten.",
  "Nachttische, Beistelltische, Sessel neben dem Sofa.", 2, pruefung=("grundriss:K17",))
R("GL-17", K, "Fünf Tiere: Schlange", ALLE, (),
  "alle Regeln sind erfüllt, aber etwas fühlt sich falsch an",
  "auf das innere Gleichgewicht hören",
  "Die Schlange in der Mitte ist dein Geisteszustand – fühlt sich etwas falsch an, ist es das wahrscheinlich.",
  "", 3)

# =====================================================================================================
# KAPITEL 3: ANWENDUNG
# =====================================================================================================
K = "3 Anwendung"
R("AN-01", K, "Kommandoposition", ALLE, ("bett", "sofa", "schreibtisch", "tuer"),
  "der Hauptplatz im Raum (Bett, Sofa, Schreibtisch) wird gewählt",
  "Wand im Rücken, offener Blick nach vorne, Tür im Blick, Halt zu den Seiten",
  "In der Kommandoposition fühlst du dich geschützt und hast den Raum unter Kontrolle – wie im bequemen Sessel "
  "mit Blick über eine Landschaft.", "", 1, pruefung=("grundriss:K01", "grundriss:K03", "grundriss:K12"))
R("AN-02", K, "Fenster im Rücken", ALLE, ("fenster", "bett", "sofa", "schreibtisch"),
  "du sitzt oder liegst mit dem Rücken an einem Fenster, besonders einem, das tiefer als die Hüfte reicht",
  "Rücken an eine feste Wand, nicht ans Fenster",
  "Ein Fenster im Rücken macht verletzlich: Man kann dich von hinten sehen.",
  "Brüstung höher als Lehne/Kopfteil, schwere Vorhänge, massives Kopfteil.", 1, pruefung=("grundriss:K02",))
R("AN-03", K, "Rücken zur Tür", ALLE, ("tuer",),
  "du sitzt oder liegst mit dem Rücken zur Tür",
  "so platzieren, dass die Tür ohne Umdrehen sichtbar ist",
  "Mit der Tür im Rücken fühlt man sich unsicher – jemand könnte unbemerkt hereinkommen.",
  "Spiegel, in dem du die Tür siehst (nicht im Schlafzimmer), Tür schließen.", 1, pruefung=("grundriss:K03",))
R("AN-04", K, "Café-Technik", ALLE, ("tuer", "fenster"),
  "du suchst den besten Platz in einem Raum",
  "nicht direkt an der Tür (Durchgang), nicht am WC, Licht vom Fenster, aber Rücken an der Wand und Blick in "
  "den Raum",
  "So wählt man instinktiv im Café: wenig Durchgang, gutes Licht, geschützter Rücken, Überblick.", "", 2,
  pruefung=("grundriss:K06", "grundriss:K01", "grundriss:K03"))
R("AN-05", K, "Kronleuchter-Effekt", ALLE, ("pendelleuchte", "balken"),
  "über deinem Platz hängt etwas Schweres (Lampe, Balken, Ventilator)",
  "den Platz wechseln oder das Schwere entfernen",
  "Man weiß, dass es nicht fällt, fühlt sich darunter aber trotzdem bedroht.", "", 1,
  pruefung=("grundriss:L01", "grundriss:K08", "foto:F05"))
R("AN-06", K, "Grundriss-Übung", ALLE, ("tuer", "fenster"),
  "du suchst die beste Chi-Position im Raum",
  "Laufwege, Linien von spitzen Ecken und Lichteinfall einzeichnen; der beste Platz liegt ohne Lauf- und "
  "Eckenlinien, aber im Licht",
  "So findet man systematisch Ruhe, Schutz und Licht.", "", 2,
  pruefung=("grundriss:C01", "grundriss:K14"))
R("AN-07", K, "Nordseite", ALLE, ("fenster",),
  "das Hauptfenster zeigt nach Norden (Nordhalbkugel)",
  "neutrale bis warme Wandfarben, keine Vorhänge vor dem Licht, abends eher kräftiges Licht; gut für Büro/Atelier",
  "Nordlicht ist indirekt, gleichmäßig, kühl-bläulich (Wasser, Winter).", "", 3,
  profil=[("hauptrichtung", "==", "N")], info=True)
R("AN-08", K, "Südseite", ALLE, ("fenster",),
  "das Hauptfenster zeigt nach Süden",
  "lebendige Farben; abends weiches, stimmungsvolles Licht; gut für Wohnzimmer und Eingang; robuste Pflanzen "
  "mildern starkes Chi",
  "Südlicht ist stark und roh (Feuer, Sommer).", "", 3, profil=[("hauptrichtung", "==", "S")], info=True)
R("AN-09", K, "Ostseite", ALLE, ("fenster",),
  "das Hauptfenster zeigt nach Osten",
  "wärmere Wandfarben, abends etwas kräftigeres Licht; gut für Kinderzimmer und Wintergarten; Holz-Elemente "
  "(nicht im Erwachsenen-Schlafzimmer)",
  "Ostlicht ist belebendes Morgenlicht (Holz, Frühling, Wachstum).", "", 3, profil=[("hauptrichtung", "==", "O")], info=True)
R("AN-10", K, "Westseite", ALLE, ("fenster",),
  "das Hauptfenster zeigt nach Westen",
  "kühlere Wandfarben, weiches Licht nach Sonnenuntergang; gut für Erwachsenen-Schlafzimmer",
  "Westlicht ist die orange-feurige Abendsonne (Metall, Herbst).", "", 3, profil=[("hauptrichtung", "==", "W")], info=True)
R("AN-11", K, "Südhalbkugel", ALLE, (),
  "du wohnst auf der Südhalbkugel",
  "Nord und Süd in allen Regeln tauschen", "Dort steht die Sonne im Norden.", "Raum(suedhalbkugel=True)", 3)

# =====================================================================================================
# KAPITEL 4: WOHNUNG WÄHLEN
# =====================================================================================================
K = "4 Planung – Wohnung wählen"
R("WO-01", K, "Bausubstanz", ("wohnung",), (),
  "eine Wohnung wird ausgesucht", "auf Dichtheit und Bausubstanz achten (vor allem Wasserschäden)",
  "Die Grundaufgabe eines Hauses ist Schutz vor Regen und Wasser.", "", 2)
R("WO-02", K, "Umgebung", ("wohnung",), (),
  "eine Wohnung wird ausgesucht", "Parks, Grün, saubere Luft in der Nähe; stark befahrene Straßen meiden",
  "Eine laute Straße ist kein Fluss, sondern gewaltsame Energie.", "", 3)
R("WO-03", K, "Bedürfnisse", ("wohnung",), (),
  "eine Wohnung wird ausgesucht", "nach heutigen Bedürfnissen wählen, nicht nach einem Merkmal für in zehn Jahren",
  "Kopf und Herz entscheiden gemeinsam.", "", 3)
R("WO-04", K, "Haus in Kommandoposition", ("wohnung",), (),
  "eine Wohnung wird ausgesucht", "etwas Stabiles im Rücken (Hügel, höheres Gebäude), offener Blick nach vorne, "
  "idealerweise auf Wasser", "Wie die Hauptstadt des Kaisers: Schutz hinten, Weite vorn.", "", 3)
R("WO-05", K, "Gesicht der Wohnung", ("wohnung",), ("tuer", "fenster"),
  "die Ausrichtung der Wohnung wird bestimmt",
  "Haus: Haustür ist das Gesicht; Wohnung/Zimmer: größtes Fenster oder Zimmertür – je nachdem, woher die meiste "
  "Energie kommt", "Danach richten sich die Himmelsrichtungs-Empfehlungen.", "nord_wand im Raum angeben.", 3)

# =====================================================================================================
# KAPITEL 4: EINGANG
# =====================================================================================================
K = "4 Planung – Eingang"
EIN = ("flur", "wohnzimmer", "studio", "kueche", "esszimmer")
R("EI-01", K, "Haupttür", EIN, ("tuer",),
  "es gibt mehrere Türen", "die meistbenutzte Tür als Haupttür behandeln und besonders pflegen",
  "Die Haupttür ist der Mund des Hauses: Alles kommt durch sie herein.", "", 2)
R("EI-02", K, "Eingang feiern", EIN, ("tuer", "licht"),
  "der Eingang ist dunkel oder lieblos",
  "viel Licht und Energie am Eingang; etwas Platz zum Ankommen",
  "Man hat nur eine Chance für den ersten Eindruck – auch für sich selbst.",
  "Helle Leuchte, Pflanze, schönes Objekt.", 2, profil=[("eingang_dunkel", "wahr", None)])
R("EI-03", K, "Zugang nicht aggressiv", EIN, ("flur",),
  "ein langer, gerader Weg oder Flur führt direkt auf die Tür zu",
  "den Weg mäandern lassen oder das Chi innen dämpfen",
  "Wie eine Klinge: Je länger die gerade Strecke, desto stärker das heranrauschende Chi.",
  "Pflanzen am Weg; innen Paravent oder Pendelleuchte als Chi-Bremse.", 2)
R("EI-04", K, "Tür führt in öffentlichen Bereich", EIN, ("tuer", "schlafzimmer"),
  "die Haustür führt zuerst an privaten Räumen (Schlafzimmer) vorbei",
  "den Blick zu den öffentlichen Räumen lenken; private Türen schließen und tarnen",
  "Der Eingang soll in den gemeinschaftlichen Teil führen, nicht in den privaten.",
  "Schlafzimmertüren geschlossen halten, in Wandfarbe streichen, Blickfang am Flurende.", 2)
R("EI-05", K, "Gegenüberliegende Wohnungstüren", ("flur",), ("tuer",),
  "zwei Wohnungstüren liegen sich direkt gegenüber",
  "den Bereich als gemeinsamen Raum mit dem Nachbarn gestalten",
  "Gegenüberliegende Türen wirken konfrontativ.", "Gemeinsam Pflanzen aufstellen.", 3)
R("EI-06", K, "Türfarbe", ("flur",), ("tuer",),
  "die Haustür wird gestrichen",
  "nach Norden/dunkel: schwarz oder Wassertöne; nach Süden/sonnig: Rot",
  "Die Farbe gleicht die Umgebung aus und kündigt das Innere an.", "", 3)
R("EI-07", K, "Fußmatte", ("flur",), ("fussmatte",),
  "die Fußmatte zeigt ein Logo oder Symbol, das du respektierst",
  "keine verehrten Symbole auf der Matte", "Man tritt jeden Tag darauf.", "", 3,
  profil=[("fussmatte_symbol", "wahr", None)])
R("EI-08", K, "Tür öffnet nach innen", ALLE, ("tuer",),
  "die Tür öffnet nach außen", "Türen nach innen öffnen lassen",
  "Eine nach innen öffnende Tür lädt das Chi herein.", "", 3, profil=[("tuer_oeffnet_aussen", "wahr", None)])
R("EI-09", K, "Türgröße", ("flur",), ("tuer",),
  "die Haupttür ist zu klein oder zu groß",
  "proportional zum Haus, aber auffälliger als alle anderen Türen",
  "Zu klein: wenig Glück kommt herein; zu groß: kann das Glück nicht halten.",
  "Seiteneingang mit Pflanzen und Weg betonen.", 3)
R("EI-10", K, "Türmaterial", ("flur",), ("tuer",),
  "die Haupttür hat Glas oder ist eine Fenstertür",
  "massive Holztür; Fenstertüren zählen als Fenster, nicht als Tür",
  "Glas steht für Zerbrechlichkeit, die Tür soll Sicherheit ausstrahlen.", "", 3,
  profil=[("haustuer_glas", "wahr", None)])
R("EI-11", K, "Flur wie ein Zimmer", ("flur",), ("flur",),
  "der Eingangsbereich ist eine Abstellfläche",
  "den Flur wie ein vollwertiges Zimmer behandeln; alles hat seinen Platz",
  "Der Eingang setzt den Ton für die ganze Wohnung.", "Schuhschrank, Garderobe, Ordnung.", 2,
  profil=[("schuhe_herum", "wahr", None)])
R("EI-12", K, "Chi-Bremse im Flur", ("flur",), ("tuer", "paravent", "pendelleuchte"),
  "die Haustür liegt am Ende eines langen Gangs mit viel Chi",
  "Chi-Bremsen innen: Paravent oder Pendelleuchte; aber nicht komplett abblocken",
  "Das heranrauschende Chi soll gedämpft, nicht abgewiesen werden.", "", 2)
R("EI-13", K, "Kein Spiegel gegenüber der Tür", ALLE, ("spiegel", "tuer"),
  "ein Spiegel hängt der Eingangstür direkt gegenüber",
  "Spiegel an eine Seitenwand, nie gegenüber der Tür",
  "Ein Spiegel gegenüber der Tür lenkt das ankommende Chi gleich wieder hinaus.", "Spiegel umhängen.", 1,
  pruefung=("grundriss:C02",))
R("EI-14", K, "Heller Flur", ("flur",), ("licht",),
  "der Eingang ist dunkel", "den Eingangsbereich immer hell halten",
  "Heimkommen soll sich wie ein kleines Fest anfühlen.", "", 2, profil=[("eingang_dunkel", "wahr", None)])
R("EI-15", K, "Pflanzen im Eingang", ("flur",), ("pflanze",),
  "der Eingang hat Tageslicht", "breitblättrige Pflanzen in den Eingang (nur wenn sie dort überleben)",
  "Pflanzen zeigen, dass das Zuhause auf fruchtbarem Boden steht.", "", 3)
R("EI-16", K, "Religiöse Objekte im Eingang", ("flur",), ("altar",),
  "du hast religiöse Objekte oder einen Altar", "sie können in den Eingang, um dich beim Heimkommen zu erinnern",
  "Beim Heimkommen begegnest du deinen Leitbildern.", "", 3)
R("EI-17", K, "Eingang frei", ("flur",), ("tuer",),
  "Möbel stehen im Eingang im Weg", "den Eingang offen und frei halten",
  "Ein ungehinderter Eintritt lässt das Chi sanft hereinfließen.", "", 1, pruefung=("grundriss:H03", "grundriss:H04"))
R("EI-18", K, "Keine Kanten im Eingang", ("flur",), ("regal", "balken"),
  "über oder neben dem Eingang sind spitze Ecken, Balken oder offene Regale",
  "vermeiden; sonst in Wandfarbe streichen oder mit Pflanzen/Licht abmildern",
  "Kanten am Eingang begrüßen dich mit Sha-Chi.", "", 2, pruefung=("grundriss:K14",))
R("EI-19", K, "Tür direkt in den Wohnraum", ("wohnzimmer", "studio"), ("tuer", "paravent"),
  "die Tür führt direkt ohne Flur in den Wohnraum",
  "Paravent oder Tisch mit Blumen als Puffer; Möbel so stellen, dass ein kleiner Eingangsbereich entsteht",
  "Ein Eingangsbereich ist wichtig, um beim Heimkommen anzukommen.", "", 2)
R("EI-20", K, "Kein Putzzeug im Eingang", ("flur",), ("besen", "muell"),
  "Besen, Mopp oder Mülleimer stehen im Eingang", "versteckt oder diskret aufbewahren",
  "Der erste Eindruck soll nicht von Putzzeug und Müll geprägt sein.", "", 2,
  profil=[("besen_muell_im_eingang", "wahr", None)], pruefung=("foto:F21",))
R("EI-21", K, "Schmaler Flur", ("flur",), ("spiegel", "bild"),
  "der Eingang ist ein langer, schmaler, dunkler Gang",
  "Spiegel an die SEITENWAND (nie ans Ende), helle Kunst an beide Seiten, schöne Pendelleuchte, Blickfang am Ende",
  "Spiegel am Ende werfen das Chi hinaus; Kunst an den Seiten bremst den Durchzug.", "", 2)
R("EI-22", K, "Tür in die Küche", ("kueche", "studio"), ("herd", "kuehlschrank"),
  "die Tür führt direkt in die Küche",
  "Küche immer aufgeräumt, Kühlschrank verstecken, Herd/Kochfeld von der Tür aus nicht sichtbar",
  "Der erste Blick soll nicht auf Funktionsgeräte und das Feuer fallen.", "", 2, pruefung=("grundriss:KU1",))
R("EI-23", K, "Tür ins Esszimmer", ("esszimmer",), ("esstisch", "tuer"),
  "die Tür führt direkt ins Esszimmer",
  "freien Weg lassen; Esstisch nicht in den Eingang; kein Stuhl mit dem Rücken zur Tür",
  "Ein blockierter Eingang und ein ungeschützter Sitz direkt an der Tür sind unangenehm.", "", 2,
  pruefung=("grundriss:E04",))
R("EI-24", K, "Treppe gegenüber der Tür", ("flur",), ("treppe",),
  "eine Treppe liegt direkt gegenüber der Haustür",
  "Paravent davor, letzte Stufen drehen oder Statement-Leuchte, um den Blick nach oben zu lenken",
  "Treppen verstärken das Chi: hinauf zu viel, hinunter fließt es ab.", "Windspiel oder Kristall.", 2)
R("EI-25", K, "Erster Blick von der Haustür", ("flur", "studio"), ("wc", "bett", "herd"),
  "von der Haustür sieht man WC, Bett oder Herd",
  "diese von der Haustür aus verbergen; stattdessen einen einladenden Blickfang (z. B. Sofa, Kunst)",
  "Das Erste, was man sieht, setzt den Ton für das ganze Zuhause.", "", 1,
  pruefung=("grundriss:BA1", "grundriss:KU1"))

# =====================================================================================================
# KAPITEL 4: WOHNZIMMER
# =====================================================================================================
K = "4 Planung – Wohnzimmer"
R("WZ-01", K, "Lage", ("wohnung",), ("wohnzimmer",),
  "die Wohnung wird geplant", "Wohnzimmer in die Mitte, von den anderen Räumen sichtbar",
  "Das Wohnzimmer ist der Anker, wo die Familie zusammenkommt.", "", 3)
R("WZ-02", K, "Sitze schauen sich an", WOHN, ("sofa", "sessel"),
  "alle Sitze zeigen in dieselbe Richtung (z. B. zum Fernseher)",
  "Sofa und Sessel einander zuwenden – ein geschlossener Sitzkreis",
  "Zugewandte Sitze laden zum Gespräch ein; der Raum zeigt, dass Menschen wichtiger sind als der TV.",
  "Sessel drehen, Couchtisch als Mitte.", 1, pruefung=("grundriss:S06", "foto:F18"))
R("WZ-03", K, "Genug Sitzplätze", WOHN, ("sofa", "sessel"),
  "es gibt weniger Sitzplätze als Bewohner/Gäste", "genug Plätze für alle Bewohner und Gäste",
  "Im Wohnzimmer ist jeder willkommen.", "", 3)
R("WZ-04", K, "Lebendige Deko", WOHN, ("pflanze", "spiegel", "aquarium"),
  "das Wohnzimmer wirkt leblos", "Pflanzen, Spiegel, evtl. Aquarium – das Wohnzimmer verträgt viel Energie",
  "Es ist der Raum mit dem meisten Leben und positivem Chi.", "", 3, pruefung=("foto:F08",))
R("WZ-05", K, "Spiegel im Wohnzimmer", WOHN, ("spiegel", "tuer", "tv"),
  "ein Spiegel spiegelt Türen oder den Fernseher",
  "Spiegel so hängen, dass sie Schönes zeigen – nicht Türen oder TV; am besten dort, wo man sich ein Fenster wünscht",
  "Spiegel verdoppeln, was sie zeigen; Türen im Spiegel lassen Chi hinausfließen.", "", 2,
  pruefung=("grundriss:C09",))
R("WZ-06", K, "Sofa in Kommandoposition", WOHN, ("sofa", "tuer", "wand"),
  "das Hauptsofa wird platziert",
  "Wand hinter dem Sofa, Platz davor, Blick auf den Eingang; nicht in Linie mit einem Flur, keine Balken darüber",
  "Das Sofa ist der Hauptplatz des Wohnzimmers.", "", 1,
  pruefung=("grundriss:K01", "grundriss:K03", "grundriss:C01", "grundriss:K08"))
R("WZ-07", K, "Ein Hauptsofa", WOHN, ("sofa", "sessel"),
  "es gibt mehrere gleichwertige Sofas", "ein Hauptsofa, ergänzt durch Sessel",
  "Klare Hierarchie bringt Ruhe.", "", 3)
R("WZ-08", K, "Zwei Sofas gegenüber", WOHN, ("sofa", "couchtisch"),
  "zwei Sofas stehen sich über eine leere Fläche gegenüber",
  "einen Couchtisch dazwischenstellen",
  "Zwei Sofas gegenüber wirken konfrontativ und formell; der Tisch entschärft die Spannung.", "", 2,
  pruefung=("grundriss:W01",))
R("WZ-09", K, "L-Sofa", WOHN, ("sofa", "sessel"),
  "ein L-förmiges Sofa steht allein", "ein oder zwei Sessel diagonal zur Ecke stellen",
  "Ein L-Sofa bildet nur einen halben Sitzkreis.", "", 3)
R("WZ-10", K, "Freistehendes Sofa", WOHN, ("sofa", "konsole"),
  "das Sofa kann nicht an eine Wand",
  "niedrige Konsole dahinter oder ein Sofa mit hoher, kräftiger Lehne",
  "Auch ohne Wand braucht der Rücken Schutz (Schildkröte).", "", 2, pruefung=("grundriss:K01",))
R("WZ-11", K, "Dachschräge über dem Sofa", WOHN, ("sofa", "schraege"),
  "das Sofa steht unter dem niedrigen Ende einer Schräge",
  "nicht unter das niedrige Ende; wenn doch, Lampen links und rechts, um die Decke optisch zu heben",
  "Die niedrige Decke drückt optisch auf den Kopf.", "", 2, pruefung=("grundriss:K09",))
R("WZ-12", K, "Sofa nicht allein", WOHN, ("sofa", "sessel", "hocker"),
  "das Sofa steht ohne weitere Sitzmöbel", "mit Sessel, Bank oder Hocker ergänzen",
  "Erst mehrere Sitzplätze bilden eine Gemeinschaft.", "", 3, pruefung=("grundriss:W03", "foto:F18"))
R("WZ-13", K, "Sessel", WOHN, ("sessel", "sofa"),
  "ein Sessel wird platziert",
  "Sessel ergänzt den Sitzkreis und schaut zum Sofa; ist der Sessel dein Hauptplatz, bekommt er die "
  "Kommandoposition", "Nicht alle Sitze sollen in dieselbe Richtung schauen.", "", 2, pruefung=("grundriss:S06",))
R("WZ-14", K, "Couchtisch als Anker", WOHN, ("couchtisch", "sofa"),
  "das Wohnzimmer hat keinen Couchtisch",
  "einen schönen Couchtisch in die Mitte – mit etwas Lebendigem darauf (Blumen, Obst)",
  "Ohne Couchtisch schwebt der Raum um eine Leere; der Tisch verbindet die Sitze und steht für Fülle.",
  "Mindestens ein Beistelltisch.", 2, pruefung=("grundriss:W02", "foto:F18"))
R("WZ-15", K, "Beistelltische", WOHN, ("beistelltisch", "sofa"),
  "das Sofa wirkt klein", "Beistelltische lassen es breiter und großzügiger wirken",
  "Sie erweitern die Fläche des Sofas.", "", 3)
R("WZ-16", K, "Fernseher dezent", WOHN, ("tv",),
  "der Fernseher steht im Mittelpunkt oder hängt hoch an der Wand",
  "TV in eine weniger wichtige Ecke, so tief wie möglich; auf ein großes Möbel mit Lampe als Gegengewicht",
  "Gemeinschaft hat Vorrang vor dem Fernseher.", "TV auf Beinen in eine Ecke stellen.", 2,
  pruefung=("grundriss:S05", "grundriss:S07", "foto:F18"), profil=[("fernseher_hoch_aufgehaengt", "wahr", None)])
R("WZ-17", K, "Kein TV über dem Kamin", WOHN, ("tv", "kamin"),
  "der Fernseher hängt über dem Kamin", "nie über den Kamin",
  "Dort bekommt er zu viel Bedeutung.", "", 2, pruefung=("grundriss:S09", "foto:F22"),
  profil=[("fernseher_ueber_kamin", "wahr", None)])
R("WZ-18", K, "Sideboards", WOHN, ("sideboard",),
  "Stauraum wird gebraucht", "Sideboards mit Lampe/hoher Deko darauf; gute Basis für Bilder darüber",
  "Sie machen den Raum wohnlich und strukturieren die Wand.", "", 3)
R("WZ-19", K, "Viele Lichtquellen", WOHN, ("licht",),
  "das Wohnzimmer hat nur ein Deckenlicht", "Tiefe durch viele verschiedene Lichtquellen",
  "Verschiedene Lichter schaffen Atmosphäre.", "", 2, pruefung=("grundriss:L03",),
  profil=[("anzahl_lichtquellen", "<", 3)])
R("WZ-20", K, "Kronleuchter über dem Couchtisch", WOHN, ("pendelleuchte", "sofa", "couchtisch"),
  "ein Kronleuchter hängt über dem Sofa oder Sitzplätzen",
  "nie über Sitzplätze; über den Couchtisch", "Über den Köpfen wirkt er bedrohlich.", "", 1,
  pruefung=("grundriss:L01", "grundriss:L02"))
R("WZ-21", K, "Kleines Wohnzimmer", WOHN, (),
  "das Wohnzimmer ist klein",
  "weniger, dafür größere Stücke; Größe über Licht/Kunst/bodenlange Vorhänge; großzügige Wege; großer Teppich "
  "(unter mindestens der Hälfte der Möbel)", "Klein ist gemütlich – nicht zu viel hineinzwängen.", "", 3)
R("WZ-22", K, "Langes Wohnzimmer", WOHN, (),
  "das Wohnzimmer ist lang und schmal",
  "Möbel quer stellen, große Kunst an die Längswände, Spiegel nicht ans Ende, Statement-Stück ans Ende, "
  "Meistgenutztes nach vorne", "Im langen Raum fließt das Chi zu schnell.", "", 2, pruefung=("grundriss:K15",))
R("WZ-23", K, "Unregelmäßiges Wohnzimmer", WOHN, ("nische",),
  "das Wohnzimmer ist L-förmig oder hat Nischen",
  "Ecken weich machen statt verschließen; Nischen als Leseecke nutzen; keine Sitzplätze in abgetrennten Nischen",
  "Wer in einer abgetrennten Nische sitzt, fühlt sich ausgeschlossen.", "Spiegel erweitern den Raum.", 3)
R("WZ-24", K, "Viele Türen und Fenster", WOHN, ("tuer", "fenster", "sofa"),
  "das Wohnzimmer hat viele Türen und Fenster",
  "starker Mittelpunkt (großer Couchtisch); Sofa nur vor Fenster, deren Brüstung höher als die Lehne ist; "
  "Durchgänge um die Sitzgruppe herum, nicht hindurch",
  "So bleibt die Sitzgruppe ein ruhiger Anker.", "", 2, pruefung=("grundriss:K02", "grundriss:C01"))

# =====================================================================================================
# KAPITEL 4: ESSZIMMER
# =====================================================================================================
K = "4 Planung – Esszimmer"
R("EZ-01", K, "Lage", ("wohnung",), ("esszimmer",),
  "die Wohnung wird geplant",
  "Esszimmer zentral, nicht direkt am Eingang, neben der Küche, unter den Schlafzimmern (nicht im Keller)",
  "Es ist das Herz des Zuhauses und bringt Familie und Freunde zusammen.", "", 3)
R("EZ-02", K, "Küche vor Fenstern", ("wohnung",), ("esszimmer", "kueche"),
  "du musst wählen: Esszimmer neben der Küche oder mit vielen Fenstern", "die Nähe zur Küche hat Vorrang",
  "Der Weg zwischen Küche und Tisch ist der meistbenutzte.", "", 3)
R("EZ-03", K, "Tisch in der Mitte", ESS, ("esstisch",),
  "der Esstisch steht an der Wand oder in einer Ecke",
  "Tisch mittig, als Mittelpunkt; rundum Platz zum Bewegen",
  "Niemand soll eingeklemmt sitzen oder zur Wand schauen.", "Wenn Wand unvermeidlich: Spiegel dort.", 1,
  pruefung=("grundriss:S04",))
R("EZ-04", K, "Erde-Element", ("esszimmer",), ("farben",),
  "die Farben im Esszimmer sind kräftig",
  "erdige, neutrale Töne – gedämpfter als im Rest der Wohnung",
  "Das Esszimmer ist die ausgleichende Mitte (Erde).", "", 3,
  profil=[("wandfarbe_element", "in", ["feuer", "wasser"])])
R("EZ-05", K, "Pendelleuchte über dem Tisch", ("esszimmer", "kueche", "studio"), ("pendelleuchte", "esstisch"),
  "es fehlt Licht über dem Tisch",
  "schöne Pendelleuchte oder Kronleuchter mittig über dem Tisch (der einzige Ort, der wirklich eine braucht)",
  "Das Licht zieht die Menschen an den Tisch.", "", 2, pruefung=("grundriss:L02",))
R("EZ-06", K, "Spiegel im Esszimmer", ("esszimmer",), ("spiegel",),
  "ein Spiegel hängt im Esszimmer",
  "er soll den Tisch spiegeln, nicht die Tür; ganze, unverzerrte Spiegel",
  "Ein Spiegel verdoppelt Essen und schöne Momente.", "", 2, pruefung=("grundriss:E05", "grundriss:C09"))
R("EZ-07", K, "Fröhliche Kunst", ("esszimmer",), ("bild",),
  "Kunst wird ausgesucht", "fröhliche, lebendige Bilder – gern auch appetitliche Motive",
  "Das Esszimmer will Freude und Energie.", "", 3)
R("EZ-08", K, "Fülle zeigen", ESS, ("esstisch",),
  "der Tisch und die Sideboards sind leer", "immer etwas darauf: Obst oder Blumen; Pflanzen, wenn genug Licht",
  "Ein gedeckter, voller Tisch steht für Überfluss.", "", 3, profil=[("esstisch_leer", "wahr", None)])
R("EZ-09", K, "Keine Uhr", ("esszimmer",), ("uhr",),
  "eine Uhr hängt im Esszimmer", "keine Uhren im Esszimmer",
  "Uhren erzeugen Eile, wo Gemeinschaft zählen soll.", "", 2, pruefung=("grundriss:E06", "foto:F10"),
  profil=[("uhr_im_raum", "wahr", None)])
R("EZ-10", K, "Tisch nicht im Weg", ESS, ("esstisch", "tuer"),
  "der Tisch steht im Eingang oder in einer Linie mit der Tür",
  "Blick zum Eingang, aber nicht im Weg; steht er in Linie mit der Haupttür, Konsole als Schutz",
  "Direkt am Eingang ist zu viel Bewegung.", "", 1, pruefung=("grundriss:E04",))
R("EZ-11", K, "Beste Plätze", ESS, ("stuhl", "tuer"),
  "Gäste werden platziert",
  "die besten Plätze den wichtigsten Gästen; der schlechteste ist der nahe dem Eingang mit dem Rücken zur Tür",
  "Jeder soll möglichst in seiner eigenen Kommandoposition sitzen.", "", 3)
R("EZ-12", K, "Tischform", ESS, ("esstisch",),
  "ein Esstisch wird gewählt",
  "rund ist am besten, dann oval, quadratisch (Erde), rechteckig mit Blick auf die Kopfenden; keine "
  "unregelmäßigen oder zusammengeschobenen Tische",
  "Runde Tische haben keine Ecken und keine Rangordnung.", "", 2, pruefung=("grundriss:E01",),
  profil=[("esstisch_form", "in", ["unregelmaessig", "zusammengeschoben"])])
R("EZ-13", K, "Tischgröße", ESS, ("esstisch",),
  "der Tisch ist viel größer als nötig", "Größe passend zum eigenen Gästeaufkommen",
  "Ein ständig leerer, zu großer Tisch schafft Ungleichgewicht.", "", 3)
R("EZ-14", K, "Tischmaterial", ESS, ("esstisch",),
  "der Esstisch ist aus Glas",
  "Holz, Stein oder Ton/Terrakotta; Glas vermeiden",
  "Glas macht unruhig – man sieht die Beine der anderen beim Essen.", "Beim Essen eine Tischdecke auflegen.", 2,
  profil=[("esstisch_material", "==", "glas")])
R("EZ-15", K, "Gleiche Stühle", ESS, ("stuhl",),
  "die Stühle sind verschieden", "alle Stühle gleich, stabil und solide",
  "Gleiche Stühle vermeiden jede Rangordnung.", "", 2, pruefung=("grundriss:E02",),
  profil=[("stuehle", "==", "verschieden")])
R("EZ-16", K, "Gerade Stuhlzahl", ESS, ("stuhl",),
  "die Stuhlzahl ist ungerade oder Stühle stehen an den Ecken",
  "gerade Anzahl, keiner an den Tischecken", "Gerade Zahl und gleiche Abstände = Fairness und Gemeinschaft.", "",
  2, pruefung=("grundriss:E02", "foto:F19"))
R("EZ-17", K, "Keine Plastikstühle", ESS, ("stuhl",),
  "es sind provisorische Plastikstühle", "solide Stühle; wenn nicht anders möglich, wenigstens bequem und stabil",
  "Plastikstühle wirken wie Kantine oder Hostel.", "", 3, profil=[("stuehle", "==", "plastik")])
R("EZ-18", K, "Ersatzstühle weg", ESS, ("stuhl",),
  "Ersatzstühle stehen am Rand", "Ersatzstühle aus dem Raum nehmen",
  "Einzelne Stühle am Rand stehen für unwillkommene Gäste.", "", 3, pruefung=("grundriss:E02",))
R("EZ-19", K, "Konsolen an die Wand", ("esszimmer",), ("konsole", "sideboard"),
  "Konsolen oder Sideboards stehen frei im Raum",
  "an die Wand; nur Tisch und Stühle in die Mitte; nichts überragt den Tisch bedrohlich",
  "Die Mitte gehört dem Tisch.", "", 2, pruefung=("grundriss:E03",))
R("EZ-20", K, "Kleines Esszimmer", ("esszimmer",), ("esstisch", "stuhl"),
  "das Esszimmer ist klein",
  "kleinerer Tisch, großzügige Stühle mit Armlehnen (oder niedrige Lehnen bei mehr Gästen), große Pendelleuchte "
  "bei hoher Decke, Spiegel, große Kunst", "Nicht alles klein machen – Größe über Wand und Licht.", "", 3)
R("EZ-21", K, "Langes Esszimmer", ("esszimmer",), ("esstisch", "bank"),
  "das Esszimmer ist lang",
  "ovaler statt langer rechteckiger Tisch, Stühle mit Armlehnen, keine langen Bänke, Spiegel an die Längswände "
  "(nicht ans Ende)", "Ovale Tische bremsen das schnelle Chi im langen Raum.", "", 2, pruefung=("grundriss:E07",))
R("EZ-22", K, "Kein fensterloser Essraum", ("esszimmer",), ("fenster",),
  "der Essbereich hat kein Fenster oder liegt im Durchgang/Flur",
  "Räume ohne Fenster meiden; im Flur Konsolen zur Verankerung, großzügige Wege",
  "Das Esszimmer braucht Licht und Luft.", "", 2, pruefung=("grundriss:C08",))
R("EZ-23", K, "Tisch außermittig", ESS, ("esstisch", "pendelleuchte"),
  "der Tisch muss außermittig stehen (für einen breiteren Weg)",
  "Pendelleuchte mittig über den Tisch hängen, um den Fokus zu setzen",
  "Die Leuchte macht den Tisch trotzdem zum Zentrum.", "", 3, pruefung=("grundriss:L02",))

# =====================================================================================================
# KAPITEL 4: KÜCHE
# =====================================================================================================
K = "4 Planung – Küche"
KUE = ("kueche", "studio")
R("KU-01", K, "Eigener Platz", ("wohnung",), ("kueche",),
  "die Wohnung wird geplant",
  "Küche mit eigenem Platz, nicht im Durchgang; nicht in der Mitte; in der hinteren Hälfte",
  "Die Küche steht für Nahrung und inneren Wohlstand, hat aber zu viel Feuer für die Mitte.", "", 3)
R("KU-02", K, "Herd nicht von der Haustür sichtbar", KUE, ("herd", "tuer"),
  "man sieht von der Tür aus den Herd",
  "Herd von der Eingangstür aus nicht sichtbar", "Das Feuer verbrennt das gute Chi, das hereinkommt.", "", 1,
  pruefung=("grundriss:KU1",))
R("KU-03", K, "WC nicht zur Küche", ("wohnung",), ("wc", "kueche"),
  "ein WC liegt der Küche gegenüber", "Tür geschlossen halten",
  "Wasser (WC) und Feuer (Küche) stören sich.", "", 3)
R("KU-04", K, "Küche weg vom Schlafzimmer", ("wohnung", "studio"), ("herd", "bett"),
  "das Schlafzimmer liegt neben oder über der Küche bzw. das Bett nahe am Herd (Studio)",
  "Küche und Schlafbereich trennen; im Studio das Bett weit weg vom Herd",
  "Die Hitze des Feuers stört die Ruhe.", "Raumteiler zwischen Küche und Bett.", 1, pruefung=("grundriss:ST1",))
R("KU-05", K, "Wohnküche", ("kueche",), ("spiegel",),
  "die Küche ist auch Essplatz", "mehr gestalten, aber weiterhin keine Spiegel oder Wasser-Elemente",
  "Die Küche bleibt vom Feuer geprägt.", "", 2, pruefung=("grundriss:KU4",))
R("KU-06", K, "Lüftung", KUE, ("fenster",),
  "die Küche hat kein Fenster", "natürliche Belüftung, Fenster in der Nähe",
  "Die Küche ist Yang und braucht Licht und Luft.", "Mehr Seitenlicht, offener gestalten.", 2,
  pruefung=("grundriss:C08",))
R("KU-07", K, "Herd als Mittelpunkt", KUE, ("herd", "spuele"),
  "Herd und Spüle werden geplant",
  "der Herd ist das zentrale Element, die Spüle zweitrangig; nicht direkt nebeneinander",
  "Feuer und Wasser kämpfen gegeneinander.", "", 1, pruefung=("grundriss:KU2",))
R("KU-08", K, "Feuer und Wasser trennen", KUE, ("herd", "spuele", "kuehlschrank", "geschirrspueler"),
  "Herd steht neben oder gegenüber von Spüle, Kühlschrank oder Spülmaschine",
  "Abstand halten oder Holz (Pflanzen) dazwischen", "Holz vermittelt zwischen Feuer und Wasser.", "", 1,
  pruefung=("grundriss:KU2",))
R("KU-09", K, "Ordnung", KUE, ("geschirr",),
  "schmutziges Geschirr steht herum", "Küche immer aufgeräumt, Geschirr nie stehen lassen",
  "Besonders wenn man sie vom Eingang sieht, prägt sie die Stimmung.", "", 2,
  profil=[("unordnung", "wahr", None)])
R("KU-10", K, "Kein Wasser-Element", ("kueche",), ("farben",),
  "die Küche ist in Wassertönen (Blau, Schwarz, Dunkelgrau) gestaltet",
  "Wasser-Element vermeiden; wenn doch, mit Erdtönen ausgleichen", "Die Küche ist ein Ort des Feuers.", "", 3,
  profil=[("wandfarbe_element", "==", "wasser")])
R("KU-11", K, "Messer verstauen", KUE, ("messer",),
  "Messer liegen offen", "Messer in Schubladen aufbewahren", "Messer stehen für Aggression.", "", 2,
  pruefung=("foto:F20",), profil=[("messer_sichtbar", "wahr", None)])
R("KU-12", K, "Wenig offene Regale", KUE, ("regal",),
  "es gibt viele offene Wandregale", "offene Regale minimieren",
  "Sie erzeugen aggressives Chi und wirken unordentlich.", "", 3, profil=[("offene_regale", "wahr", None)])
R("KU-13", K, "Keine Spiegel", ("kueche",), ("spiegel", "herd"),
  "ein Spiegel hängt in der Küche, vor allem gegenüber dem Herd", "keine Spiegel in der Küche",
  "Sie verteilen das aggressive Chi der Küche.", "", 2, pruefung=("grundriss:KU4",))
R("KU-14", K, "Mülleimer verstecken", KUE, ("muell",),
  "Mülleimer stehen sichtbar", "Müll und Recycling nicht offen zeigen", "Sie stören den Eindruck von Fülle.", "",
  3, pruefung=("foto:F21",), profil=[("muell_sichtbar", "wahr", None)])
R("KU-15", K, "Herd in Kommandoposition", KUE, ("herd", "tuer"),
  "der Herd wird platziert",
  "hinten im Raum, nicht direkt zur Tür, aber von der Kochposition die Tür im Blick",
  "Der Herd ist das wichtigste Element der Küche.", "", 1, pruefung=("grundriss:KU1",))
R("KU-16", K, "Ofen nicht auf Sitzplätze", KUE, ("herd", "stuhl", "sofa"),
  "die Ofentür zeigt auf Sitzplätze", "Ofen weg von Sitzbereichen",
  "Der Ofen strahlt das Feuer nach vorne ab.", "", 2, pruefung=("grundriss:KU5",))
R("KU-17", K, "Kochfeld nicht unters Fenster", KUE, ("herd", "fenster"),
  "das Kochfeld liegt unter einem Fenster",
  "Kochfeld zur Kochinsel oder zur Wand mit Spritzschutz; die Spüle darf unters Fenster",
  "Unter dem Fenster entweicht die Energie.", "", 2, pruefung=("grundriss:KU3",))
R("KU-18", K, "Spüle diskret", KUE, ("spuele",),
  "die Spüle steht im Mittelpunkt", "Spüle zurückhaltend; Fenster oder Kochinsel sind gute Plätze",
  "Die Küche soll warm und feurig sein.", "", 3)
R("KU-19", K, "Kühlschrank", KUE, ("kuehlschrank",),
  "der Kühlschrank fällt auf oder steht neben dem Herd",
  "Kühlschrank einfügen (Farbe wie Küche oder integriert), nicht neben den Herd",
  "Er ist ein Wasser-Gerät, nichts zum Feiern.", "Gute Isolierung zwischen beiden.", 2, pruefung=("grundriss:KU2",))
R("KU-20", K, "Kleine Küche", KUE, (),
  "die Küche ist klein",
  "Kombigeräte, kleinere Geräte, integrierte Geräte, immer aufgeräumt; ohne Oberschränke, wenn genug Stauraum",
  "Integration wirkt ruhiger und größer.", "", 3)
R("KU-21", K, "Lange Küche", KUE, ("pendelleuchte",),
  "die Küche ist lang (Galeerenküche)",
  "breite Pendelleuchten statt einer Reihe kleiner, Geräte an die Stirnwand, großzügige Insel",
  "Eine Reihe kleiner Lampen wirkt wie ein Zugwaggon.", "", 3)
R("KU-22", K, "Unregelmäßige Küche", KUE, (),
  "die Küche hat Nischen oder ist L-förmig",
  "Nischen als Speisekammer, Kühlschrank in Ecken, Arbeitsbereiche in Sichtweite", "", "", 3)
R("KU-23", K, "Fensterlose Küche", KUE, ("fenster", "spiegel"),
  "die Küche hat kein Fenster", "öffnen, viel Seitenlicht – aber keine Spiegel",
  "Energie soll trotzdem fließen.", "", 2, pruefung=("grundriss:C08",))

# =====================================================================================================
# KAPITEL 4: BÜRO
# =====================================================================================================
K = "4 Planung – Büro"
BUE = ("buero", "schlafzimmer", "wohnzimmer", "studio", "kinderzimmer")
R("BU-01", K, "Lage", ("wohnung",), ("buero",),
  "das Arbeitszimmer wird geplant",
  "Konzentration → hinterer, ruhiger Teil; Publikumsverkehr → vorne; weg von Küche und Bad",
  "Die Umgebung muss zur Arbeit passen.", "", 3)
R("BU-02", K, "Funktionen trennen", BUE, ("schreibtisch", "bett", "sofa"),
  "du arbeitest im Wohn- oder Schlafzimmer", "Arbeitsbereich klar von den anderen Funktionen trennen",
  "Vermischte Funktionen stören Arbeit und Erholung.", "Raumteiler, Teppich, eigene Ecke.", 1,
  pruefung=("grundriss:C05",))
R("BU-03", K, "Tageslicht", ("buero",), ("fenster",),
  "das Arbeitszimmer hat kein Fenster",
  "immer bei Tageslicht arbeiten; fensterlose Räume nur kurz (z. B. Online-Meeting)",
  "Ohne Tageslicht fehlt die Energie – nie lange nur unter Kunstlicht arbeiten.", "", 1,
  pruefung=("grundriss:C08",))
R("BU-04", K, "Schreibtisch in Kommandoposition", BUE, ("schreibtisch", "tuer", "wand"),
  "der Schreibtisch wird platziert",
  "Wand hinter dir, nie Rücken zur Tür, Tür im Blick; seitlich zur Tür ist okay",
  "Hier verdienst du dein Geld – du brauchst die beste Umgebung.", "", 1,
  pruefung=("grundriss:K01", "grundriss:K03"))
R("BU-05", K, "Kundeneingang", ("buero",), ("tuer",),
  "Kunden besuchen dich", "einladender, deutlicher Eingang",
  "So finden Kunden und Wohlstand leicht zu dir.", "", 3)
R("BU-06", K, "Farben nach Ziel", ("buero",), ("farben",),
  "Farben werden gewählt",
  "Wachstum: Grün/Hellblau; Wohlstand: Gold/satte Töne; Stabilität: Erdtöne; flexibel: Schwarz/Dunkelblau; "
  "präzise: Weiß", "Die Farben sollen zum Ziel deiner Arbeit passen.", "", 3)
R("BU-07", K, "Kunst im Büro", ("buero",), ("bild",),
  "Bilder werden aufgehängt", "Motive, die deine Arbeit und Wachstum zeigen; keine einschüchternden Porträts",
  "Gesichter können einschüchtern – außer sie inspirieren dich.", "", 3)
R("BU-08", K, "Gleichmäßiges Licht", ("buero",), ("licht",),
  "das Arbeitslicht ist ungleichmäßig", "anders als im Rest der Wohnung: gleichmäßig hell",
  "Konzentration braucht gutes, gleichmäßiges Licht.", "Uplighter gegen eine weiße Decke.", 2)
R("BU-09", K, "Ordnung im Büro", ("buero",), (),
  "der Arbeitsplatz ist unordentlich", "aufgeräumt; Unterlagen sinnvoll kategorisieren",
  "Ordnung im Raum = Ordnung im Kopf.", "", 2, profil=[("unordnung", "wahr", None)])
R("BU-10", K, "Pflanzen im Büro", ("buero",), ("pflanze",),
  "das Büro hat keine Pflanzen", "Pflanzen am Fenster – das Büro ist ein Yang-Bereich",
  "Pflanzen stehen für Wachstum.", "", 3, pruefung=("foto:F08",))
R("BU-11", K, "Aquarium", ("buero",), ("aquarium",),
  "du wünschst dir mehr Energie", "ein gepflegtes Aquarium bringt Wohlstand und Energie",
  "Wasser steht für Wohlstand.", "Nur wenn du es pflegst.", 3)
R("BU-12", K, "Nichts über dem Kopf", BUE, ("balken", "pendelleuchte", "schreibtisch"),
  "über dem Schreibtisch hängt ein Balken oder eine Pendelleuchte", "nicht darunter sitzen",
  "Schweres über dem Kopf belastet unbewusst.", "", 1, pruefung=("grundriss:K08", "grundriss:L01"))
R("BU-13", K, "Nicht zu nah an der Tür", BUE, ("schreibtisch", "tuer"),
  "der Schreibtisch steht direkt an der Tür", "Abstand zur Tür", "Durch die Tür kommt das Chi herein.", "", 2,
  pruefung=("grundriss:K06",))
R("BU-14", K, "Fenster seitlich", BUE, ("schreibtisch", "fenster"),
  "Fenster liegt hinter oder vor dem Schreibtisch",
  "Fenster seitlich (gleichmäßiges Licht); nicht dahinter (beobachtet), nicht davor (Ablenkung, Blendung)",
  "Seitenlicht ist am angenehmsten.", "", 2, pruefung=("grundriss:K13", "grundriss:K02", "foto:F12"))
R("BU-15", K, "Freier Weg", BUE, ("schreibtisch",),
  "der Weg zum Arbeitsplatz ist verstellt", "freier Weg zum Schreibtisch",
  "", "", 2, pruefung=("grundriss:H04", "grundriss:H05"))
R("BU-16", K, "Viele Bildschirme", BUE, ("bildschirm", "wand", "regal"),
  "du arbeitest mit vielen Monitoren", "lieber zur Wand schauen – aber Tür im Blick, keine Wandregale darüber",
  "Bildschirme sind selbst Fenster zur Welt.", "", 2, pruefung=("grundriss:S01",))
R("BU-17", K, "Schreibtischform", BUE, ("schreibtisch",),
  "ein Schreibtisch wird gewählt",
  "rechteckig für Verhandlungen, geschwungen für Kreativität; hell/naturfarben; keine spiegelnden Oberflächen",
  "Spiegelnde Flächen bringen zu viel Energie.", "", 3, profil=[("schreibtisch_oberflaeche", "==", "glaenzend")])
R("BU-18", K, "Keine offenen Regale", BUE, ("regal",),
  "das Büro hat viele offene Regale", "geschlossene Schränke bevorzugen", "Offene Regale erzeugen aggressives Chi.",
  "", 3, pruefung=("grundriss:S02",), profil=[("offene_regale", "wahr", None)])
R("BU-19", K, "Bücher in Reichweite", BUE, ("regal", "schreibtisch"),
  "das Bücherregal steht weit weg", "Regal leicht erreichbar vom Arbeitsplatz; Nachschlagewerke hinter dir, "
  "vorne frei", "Wissen im Rücken stützt dich, freie Sicht vorne klärt die Gedanken.", "", 3,
  pruefung=("grundriss:B01",))
R("BU-20", K, "Bücher aufrecht", BUE, ("buch",),
  "Bücher liegen quer gestapelt", "Bücher aufrecht stellen", "Liegende Bücher wirken unordentlich.", "", 3,
  profil=[("buecher_liegend", "wahr", None)])
R("BU-21", K, "Tagesbett im Büro", ("buero",), ("tagesbett",),
  "im Büro steht ein Sofa oder Tagesbett",
  "die beste Position bleibt dem Schreibtisch; das Tagesbett nicht zur Tür richten",
  "", "", 3, pruefung=("grundriss:B03",))
R("BU-22", K, "Rücken zur Tür unvermeidbar", BUE, ("schreibtisch", "spiegel"),
  "du musst mit dem Rücken zur Tür sitzen",
  "beim Arbeiten die Tür schließen, kleinen Spiegel auf den Tisch, Stuhl mit hoher Lehne",
  "So siehst du, wer kommt.", "", 2, pruefung=("grundriss:K03",))
R("BU-23", K, "Schreibtisch vor der Wand", BUE, ("schreibtisch",),
  "der Schreibtisch steht direkt vor der Wand",
  "tieferen Tisch nehmen, Bilder/Pinnwand an die Wand", "Eine Wand direkt vor dir wirkt unterdrückend.", "", 3,
  pruefung=("grundriss:K12",))
R("BU-24", K, "Fenster vor und hinter dir", BUE, ("schreibtisch", "fenster", "tuer"),
  "Tür und Fenster liegen sich gegenüber, du sitzt dazwischen",
  "lieber zur Wand schauen als mit dem Rücken zur Tür", "", "", 2, pruefung=("grundriss:C01", "grundriss:K03"))
R("BU-25", K, "Geteiltes Büro", ("buero",), ("schreibtisch",),
  "mehrere Personen arbeiten im Raum",
  "Gleichgestellte: niemand in schlechter Position, gleich große Tische; Hierarchie: der/die Ranghöchste bekommt "
  "die Kommandoposition; zu zweit: Tische gegenüber, keiner sieht den Bildschirm des anderen",
  "Ungleich große Tische führen zu Konflikten.", "", 2, pruefung=("grundriss:B02",))

# =====================================================================================================
# KAPITEL 4: SCHLAFZIMMER
# =====================================================================================================
K = "4 Planung – Schlafzimmer"
R("SZ-01", K, "Lage", ("wohnung",), ("schlafzimmer",),
  "die Wohnung wird geplant", "Schlafzimmer weit weg vom Eingang, hinter den öffentlichen Räumen; nicht am Bad, "
  "nicht an der Küche", "Es ist ein Rückzugsort vor der Welt.",
  "Liegt es am Eingang: Tür geschlossen halten und in Wandfarbe streichen.", 3)
R("SZ-02", K, "Bett symmetrisch", SCHLAF, ("bett",),
  "das Bett wird platziert", "symmetrisch, der Rest des Raums unterstützt das Schlafen",
  "Ein mittig stehendes Bett verankert den Raum.", "", 2, pruefung=("grundriss:K16",))
R("SZ-03", K, "Keine Arbeit, kein Sport, kein TV", SCHLAF, ("schreibtisch", "tv", "sport"),
  "im Schlafzimmer stehen Schreibtisch, Sportgeräte oder TV",
  "möglichst vermeiden; sonst eine reine Ruhezone ums Bett", "Im Schlafzimmer soll der Kopf abschalten.", "", 2,
  pruefung=("grundriss:C04", "grundriss:C05"))
R("SZ-04", K, "Erde statt Feuer", SCHLAF, ("farben",),
  "das Schlafzimmer ist in kräftigen Feuerfarben gestaltet",
  "vor allem Erde: horizontale Linien, natürliche, neutrale Töne", "Das Schlafzimmer soll beruhigen.", "", 2,
  profil=[("wandfarbe_element", "==", "feuer")])
R("SZ-05", K, "Keine Ecken aufs Bett", SCHLAF, ("ecken", "bett"),
  "spitze Möbel- oder Wandecken zeigen auf das Bett",
  "Raum quadratisch/rechteckig halten; keine Ecken aufs Bett richten",
  "Spitze Ecken erzeugen tötendes Sha-Chi: Wie eine Messerspitze signalisieren sie dem Unterbewusstsein Gefahr – "
  "gerade im Schlaf, wenn man ungeschützt ist.", "Runde oder niedrige Möbel, Ecken mit Pflanzen oder Stoff abmildern.",
  2, pruefung=("grundriss:K14",))
R("SZ-60", K, "Kein langer Raum", SCHLAF, ("bett",),
  "das Schlafzimmer ist lang und schmal",
  "lange Räume als Schlafzimmer meiden; sonst Bett quer stellen",
  "Im langen Raum bildet sich Bewegungs-Chi – man schläft wie in einem Flur.", "", 2, pruefung=("grundriss:K15",))
R("SZ-06", K, "Großes Schlafzimmer", SCHLAF, ("teppich", "bank"),
  "das Schlafzimmer ist sehr groß",
  "Zonen mit Teppichen schaffen; das Bett mit Bank/Sofa am Fußende schützen",
  "In großen Räumen fühlt man sich ungeschützt und verloren.", "", 3)
R("SZ-07", K, "Tür und Fenster", SCHLAF, ("tuer", "fenster"),
  "das Schlafzimmer hat kein Fenster", "nie einen fensterlosen Raum als Schlafzimmer",
  "Faustregel: Wo eine Pflanze nicht überleben kann, soll niemand schlafen.", "", 1, pruefung=("grundriss:C08",))
R("SZ-08", K, "Viele Fenster", SCHLAF, ("fenster", "vorhang"),
  "das Schlafzimmer hat viele Fenster", "zum Schlafen die Vorhänge schließen",
  "Sonne und Wind dringen zu leicht ein, man fühlt sich ausgesetzt.", "", 2)
R("SZ-09", K, "Nur eine Tür", SCHLAF, ("tuer",),
  "das Schlafzimmer hat mehrere Türen",
  "weitere Türen nur zu privaten Räumen (eigener Balkon ok, Gemeinschaftsterrasse nicht)",
  "Mehrere Türen machen das Schlafzimmer zum Durchgangsraum.", "", 2, profil=[("anzahl_tueren", ">", 1)])
R("SZ-10", K, "Keine Elektronik", SCHLAF, ("tv", "bildschirm", "handy"),
  "TV, Computer oder Handy sind im Schlafzimmer",
  "möglichst entfernen; analoge Alternativen (Wärmflasche statt Heizdecke)",
  "Elektronik bringt Unruhe; schwarze Bildschirme wirken wie Spiegel.", "Nachts ausschalten und abdecken.", 1,
  pruefung=("grundriss:C04", "foto:F01"),
  profil=[("computer_im_raum", "wahr", None)])
R("SZ-11", K, "Handy am Bett", SCHLAF, ("handy",),
  "das Handy liegt am Bett", "Handy außerhalb des Bettbereichs laden", "Es hält den Kopf wach.", "", 2,
  profil=[("smartphone_am_bett", "wahr", None)])
R("SZ-12", K, "Kein Yang im Schlafzimmer", ("schlafzimmer", "gaestezimmer"), ("aquarium", "pflanze", "drache"),
  "Aquarium, Pflanzen oder Drachenbilder sind im Schlafzimmer",
  "vermeiden – außer sie geben dir Ruhe (Pflanzen als Freunde: gruppiert ans Fenster, weit weg vom Bett)",
  "Sie bringen Yang-Energie, das Schlafzimmer braucht Yin.", "", 2,
  pruefung=("grundriss:C06", "grundriss:C03", "foto:F08", "foto:F11"))
R("SZ-13", K, "Kopfteil", SCHLAF, ("bett",),
  "das Bett hat kein oder nur ein Gitter-Kopfteil",
  "massives oder gepolstertes Kopfteil, je größer und breiter desto besser", "Das Kopfteil ist deine Schildkröte.",
  "", 1, profil=[("bettkopfteil", "in", ["keins", "gitter"])])
R("SZ-14", K, "Stabiles Bett", SCHLAF, ("bett",),
  "das Bett ist wackelig oder ein Wasserbett", "stabiler Rahmen; Wasserbetten unbedingt vermeiden",
  "Schlafen braucht Stabilität; Wasser gehört nicht unter den Schlafenden.", "", 1,
  profil=[("wasserbett", "wahr", None)])
R("SZ-15", K, "Himmelbett", SCHLAF, ("bett",),
  "du hast ein Himmelbett", "lieber ein niedriges Bett", "Himmelbetten wirken streng, niedrige Betten ruhig.", "",
  3, profil=[("bett_typ", "==", "himmelbett")])
R("SZ-16", K, "Luft unter dem Bett", SCHLAF, ("bett",),
  "der Bettkasten ist vollgestopft oder das Bett liegt direkt am Boden",
  "Bett etwas über dem Boden, Bettkasten nicht überfüllen", "Luft muss zirkulieren, sonst sammelt sich Feuchtigkeit.",
  "", 2, profil=[("bett_unterbau_vollgestopft", "wahr", None)])
R("SZ-17", K, "Bettwäsche", SCHLAF, ("bettwaesche",),
  "die Bettwäsche ist schwarz", "helle, ruhige Farben; wenn dunkel, dann nicht schwarz",
  "Das Bett soll Ruhe ausstrahlen.", "", 3, profil=[("bettwaesche_farbe", "==", "schwarz")])
R("SZ-18", K, "Bett machen", SCHLAF, ("bett",),
  "das Bett bleibt ungemacht", "morgens das Bett machen", "So staut sich kein abgestandenes Chi.", "", 3,
  profil=[("bett_ungemacht", "wahr", None)])
R("SZ-19", K, "Feste Wand hinter dem Bett", SCHLAF, ("bett", "wand"),
  "das Bett schwebt frei im Raum oder steht an einer niedrigen Trennwand", "Kopfteil an eine feste Wand",
  "Die Schildkröte schützt dich im Schlaf.", "", 1, pruefung=("grundriss:K01",))
R("SZ-20", K, "Nicht ans Fenster", SCHLAF, ("bett", "fenster"),
  "das Kopfteil steht vor einem Fenster",
  "vermeiden; sonst massives Kopfteil, schwere Vorhänge, Brüstung höher als das Kopfteil",
  "Am Fenster fehlt der Schutz im Rücken.", "", 1, pruefung=("grundriss:K02", "foto:F06"))
R("SZ-21", K, "Keine Säulen oder schrägen Wände", SCHLAF, ("bett", "saeule"),
  "das Bett steht an einer Säule oder an einer schrägen/unebenen Wand", "an eine gerade, ebene Wand",
  "Unebene Wände geben keinen stabilen Halt.", "", 2)
R("SZ-22", K, "Raum vor dem Bett", SCHLAF, ("bett",),
  "vor dem Bett ist kaum Platz – oder sehr viel leerer Raum",
  "ausgewogen: genug Platz, aber nicht zu viel offenen Raum vor dem Bett",
  "Zu eng wirkt beengend, zu viel Raum bringt zu viel Chi.", "", 2, pruefung=("grundriss:K12",))
R("SZ-23", K, "Tür im Blick", SCHLAF, ("bett", "tuer"),
  "vom Bett aus sieht man die Tür nicht",
  "breiter Blick über den Raum und auf die Tür; keine hohen Möbel zwischen Bett und Tür",
  "Man will sehen, wer hereinkommt.", "", 1, pruefung=("grundriss:K03",))
R("SZ-24", K, "Nicht an der Türwand", SCHLAF, ("bett", "tuer"),
  "das Bett steht an derselben Wand wie die Tür", "an eine andere Wand",
  "Von dort kann man die Tür nicht überblicken.", "", 1, pruefung=("grundriss:K07",))
R("SZ-25", K, "Von beiden Seiten zugänglich", SCHLAF, ("bett",),
  "das Bett ist nur von einer Seite zugänglich",
  "von beiden Seiten einsteigen können (für Paare Pflicht; für Singles = offen für einen Partner)",
  "Ein Bett an der Wand ist für eine Person gemacht.", "", 1, pruefung=("grundriss:K10",))
R("SZ-26", K, "Nachttische als Paar", SCHLAF, ("nachttisch", "lampe"),
  "es gibt nur einen Nachttisch oder sie sind sehr verschieden",
  "zwei Nachttische und Lampen mit gleichem visuellem Gewicht links und rechts",
  "Gleichgewicht zu beiden Seiten (Drache und Tiger).", "", 2, pruefung=("grundriss:K17", "foto:F14"))
R("SZ-27", K, "Bett in der Ecke", SCHLAF, ("bett",),
  "das Bett steht mit der Längsseite an der Wand in der Ecke",
  "okay für glückliche Singles; wer Romantik sucht, vermeidet es", "Das Bett ist dann nur für eine Person.", "", 3,
  pruefung=("grundriss:K10",))
R("SZ-28", K, "Füße nicht zur Tür", SCHLAF, ("bett", "tuer"),
  "die Füße zeigen in direkter Linie zur Tür",
  "nie in Linie mit der Tür; sonst Paravent oder schweres Möbel am Fußende, Bereich vor der Tür ruhig halten",
  "Das Chi strömt direkt auf dich zu; die Lage erinnert an einen Sarg oder eine Steißgeburt.", "", 1,
  pruefung=("grundriss:K04", "foto:F07"))
R("SZ-29", K, "Füße nicht zum Fenster", SCHLAF, ("bett", "fenster"),
  "die Füße zeigen zu einem großen Fenster", "vermeiden – bei kleinen Fenstern oder ruhigem Ausblick okay",
  "Ein großes Fenster bringt viel Bewegungs-Chi.", "Vorhänge.", 2, pruefung=("grundriss:K05",))
R("SZ-30", K, "Keine Öffnung am Fußende", SCHLAF, ("bett", "schranktuer"),
  "die Füße zeigen zu einer Schranktür oder anderen Öffnung",
  "Türen diskret gestalten und geschlossen halten", "Jede Öffnung bringt Bewegung.", "", 2,
  pruefung=("grundriss:K04",))
R("SZ-31", K, "Tür weit weg", SCHLAF, ("bett", "tuer"),
  "das Bett steht nahe an der Tür", "die Tür so weit wie möglich vom Bett",
  "An der Tür ist das stärkste Chi.", "", 1, pruefung=("grundriss:K06",))
R("SZ-32", K, "Spiegel", SCHLAF, ("spiegel", "bett"),
  "ein Spiegel hängt im Schlafzimmer, vor allem sichtbar vom Bett oder am Fußende",
  "Spiegel vermeiden; wenn doch, nicht vom Bett aus sichtbar",
  "Spiegel verhalten sich wie Türen und bringen Bewegung.", "Nachts abdecken.", 1,
  pruefung=("grundriss:C02", "foto:F02"))
R("SZ-33", K, "Keine Balken über dem Bett", SCHLAF, ("bett", "balken"),
  "ein Balken läuft über das Bett", "Bett so stellen, dass kein Balken quer darüber läuft",
  "Balken sind wie Klingen über dir.", "Abgehängte Decke oder Balken in Deckenfarbe.", 1, pruefung=("grundriss:K08",))
R("SZ-34", K, "Dachschräge", SCHLAF, ("bett", "schraege"),
  "das Bett steht unter einer Dachschräge",
  "Kopf an die hohe Seite, ausgeglichen; beim Satteldach mittig unter den First",
  "Die niedrige Decke drückt auf den Kopf.", "Kräftiges Kopfteil, Lampen heben die Decke optisch.", 2,
  pruefung=("grundriss:K09",))
R("SZ-35", K, "Keine schweren Lampen über dem Bett", SCHLAF, ("bett", "pendelleuchte", "ventilator"),
  "eine schwere Leuchte, ein Ventilator oder eine Skulptur hängt über dem Bett",
  "nichts Schweres über dem Bett; eine leichte Papierleuchte ist okay", "", "", 1,
  pruefung=("grundriss:L01", "foto:F05"), profil=[("pendelleuchte_ueber_bett", "wahr", None)])
R("SZ-36", K, "Keine schweren Bilder über dem Bett", SCHLAF, ("bett", "bild"),
  "ein schweres Bild mit Glas hängt über dem Bett",
  "nur leichte Textilien oder ein Wandgemälde", "Gefährlich, falls es fällt.", "", 1,
  pruefung=("grundriss:S01", "foto:F04"))
R("SZ-37", K, "Keine Regale über dem Bett", SCHLAF, ("bett", "wandregal"),
  "über dem Kopfteil sind Regale oder Wandmöbel", "nie Regale über das Kopfteil", "", "", 1,
  pruefung=("grundriss:S01", "foto:F03"))
R("SZ-38", K, "Kopf nach Norden", SCHLAF, ("bett",),
  "du schläfst mit dem Kopf nach Norden",
  "kann man berücksichtigen, aber nicht auf Kosten anderer Regeln", "Manche Kulturen meiden es (Magnetfeld).", "", 3)
R("SZ-39", K, "Außenwand im Altbau", SCHLAF, ("bett", "wand"),
  "das Bett steht in einem Altbau an der Außenwand", "an eine Innenwand",
  "Die Außenwand überträgt Temperaturschwankungen.", "", 2, pruefung=("grundriss:C07",))
R("SZ-40", K, "Begehbarer Schrank", SCHLAF, ("schranktuer",),
  "ein begehbarer Kleiderschrank liegt im Schlafbereich",
  "außerhalb des Schlafbereichs; sonst die Tür möglichst unauffällig",
  "Eine zusätzliche Tür macht den Raum zum Durchgang; dahinter 'lauert' etwas.", "", 3)
R("SZ-41", K, "Einbauschrank", SCHLAF, ("schrank",),
  "es gibt mehrere kleine Schränke",
  "Einbauschrank > ein großer freistehender > mehrere kleine; freistehende zum Begradigen unebener Wände nutzen",
  "Viele kleine Schränke = viele spitze Ecken.", "", 2, pruefung=("foto:F17",),
  profil=[("kleiderschrank", "==", "mehrere")])
R("SZ-42", K, "Schrank aufgeräumt", SCHLAF, ("schrank",),
  "der Kleiderschrank ist vollgestopft",
  "ausmisten, Platz lassen", "Ein vollgestopfter Schrank sagt: kein Platz für jemand Neuen in deinem Leben.", "", 2,
  profil=[("kleiderschrank_vollgestopft", "wahr", None)])
R("SZ-43", K, "Arbeiten im Schlafzimmer", SCHLAF, ("schreibtisch",),
  "du arbeitest im Schlafzimmer",
  "auf ein Minimum beschränken, nie auf dem Bett arbeiten, eigener Stuhl, Computer nachts aus",
  "Das Bett ist nur für die Ruhe.", "", 2, pruefung=("grundriss:C05",))
R("SZ-44", K, "Schminktisch", SCHLAF, ("schminktisch", "spiegel"),
  "ein Schminktisch mit Spiegel steht im Schlafzimmer", "den Spiegel vom Bett weg richten",
  "Ein Schminktisch passt besser als ein Arbeitstisch – aber der Spiegel soll dich nicht im Bett zeigen.", "", 2,
  pruefung=("grundriss:C02",))
R("SZ-45", K, "Nachttische", SCHLAF, ("nachttisch",),
  "Nachttische haben spitze Ecken, sind höher als die Matratze oder aus Glas",
  "rund oder niedriger als die Matratze, geschlossen, stabil, nicht aus Glas, nicht zu hoch",
  "Ecken am Kopf und hohe Möbel, die über dir aufragen, stören den Schlaf; Glas ist kalt wie ein Spiegel.", "", 2,
  pruefung=("grundriss:K14", "grundriss:K17"), profil=[("nachttisch_material", "==", "glas")])
R("SZ-46", K, "Bad am Schlafzimmer", SCHLAF, ("wc", "bett"),
  "ein Bad grenzt ans Schlafzimmer",
  "Badtür nachts schließen; das WC nicht an derselben Wand wie das Bett; nicht unter Badewanne/WC schlafen",
  "Wasser und Abwasser gehören nicht zum Schlafen; undichte Rohre bedeuten Schimmel.", "Kalebasse zwischen Bett und Wand.",
  2, profil=[("wc_an_bettwand", "wahr", None)])
R("SZ-47", K, "Kleines Schlafzimmer", SCHLAF, ("bett",),
  "das Schlafzimmer ist klein",
  "große Stücke in die hintersten Ecken; das Bett nicht beengen; breites, waagrechtes Kopfteil über die Wand",
  "", "", 3)
R("SZ-48", K, "Langes Schlafzimmer", SCHLAF, ("bett",),
  "das Schlafzimmer ist lang",
  "Bett quer zur Raumlänge; nicht ungeschützt am Raumende; Kunst an die Längswände, keine Spiegel",
  "Ungeschützt am Ende eines langen Raums ist wie Füße zur Tür.", "", 2, pruefung=("grundriss:K15",))
R("SZ-49", K, "Unregelmäßiges Schlafzimmer", SCHLAF, ("schrank",),
  "das Schlafzimmer ist L-förmig oder unregelmäßig",
  "mit Einbauschränken begradigen, die Extra-Ecke als Ankleide nutzen; Kunst statt Spiegel",
  "Im Schlafzimmer stören Spiegel die Ruhe.", "", 3)
R("SZ-50", K, "Viele Türen/Fenster", SCHLAF, ("bett", "tuer", "fenster"),
  "das Schlafzimmer hat viele Türen und Fenster",
  "Bett an den ruhigsten, dunkelsten Punkt abseits der Chi-Bahnen; schwere Vorhänge; Innentüren schließen; "
  "dunklere Farben machen es intimer", "", "", 2, pruefung=("grundriss:C01",))
R("SZ-51", K, "Geteiltes Zimmer: gleiche Betten", SCHLAF, ("bett",),
  "zwei Personen teilen sich das Zimmer",
  "gleich große Betten mit Abstand; nicht Füße zum Kopf des anderen; jeder hat einen eigenen Bereich, niemand "
  "muss durch den Bereich des anderen", "Ungleiche Betten zeigen Ungleichgewicht.", "", 1,
  pruefung=("grundriss:G01", "grundriss:G02"))
R("SZ-52", K, "Etagenbett", SCHLAF, ("etagenbett",),
  "es gibt ein Etagenbett", "möglichst vermeiden; die ältere Person schläft oben", "", "", 3,
  pruefung=("grundriss:G03",))
R("SZ-53", K, "Paare", SCHLAF, ("bett",),
  "ein Paar schläft getrennt",
  "zusammen schlafen; oder zwei getrennte Betten mit Abstand – nie zwei Einzelbetten zusammengeschoben",
  "Zusammengeschobene Betten stehen für eine versteckte, unausweichliche Trennung.", "", 2,
  pruefung=("grundriss:G01",))
R("SZ-54", K, "Paar und Single", SCHLAF, (),
  "ein Paar teilt das Zimmer mit einer Einzelperson", "vermeiden",
  "Die Einzelperson wirkt wie eine dritte Partei in der Beziehung.", "", 3)
R("SZ-55", K, "Kinderzimmer", ("kinderzimmer",), ("pflanze", "bildschirm", "bett"),
  "ein Kinderzimmer wird eingerichtet",
  "mehr Yang: Pflanzen und Computer sind okay; am besten Ostseite; Einzelbett mit Längsseite an die Wand",
  "Kinder brauchen weniger Erholung und mehr Wachstum.", "", 2, pruefung=("grundriss:K11",))
R("SZ-56", K, "Kinder-Schreibtisch", ("kinderzimmer",), ("schreibtisch", "bildschirm"),
  "der Kinder-Schreibtisch steht so, dass die Eltern von der Tür den Bildschirm sehen",
  "lieber nicht – das gibt dem Kind Sicherheit und Respekt", "", "", 3, pruefung=("grundriss:K03",))
R("SZ-57", K, "Keine offenen Regale im Kinderzimmer", ("kinderzimmer",), ("regal",),
  "Bücher stehen in offenen Regalen", "geschlossene Regale", "Offene Regale wirken wie Balken.", "", 3,
  pruefung=("grundriss:S02",))
R("SZ-58", K, "Gästezimmer", ("gaestezimmer",), ("tagesbett",),
  "das Gästezimmer hat eine Schlafcouch", "wie ein Schlafzimmer behandeln; ausgeklappt soll sie in der "
  "Kommandoposition stehen", "", "", 3, pruefung=("grundriss:K01", "grundriss:K03"))
R("SZ-59", K, "Unterwegs", ("unterwegs",), ("bett",),
  "du schläfst im Hotel, Schlafsaal, Schiff oder Zelt",
  "Schlafsaal: Bett am hinteren Ende; Schiff: Kabine mit Fenster; Zelt: Füße nicht zum Eingang",
  "Die gleichen Prinzipien gelten überall.", "", 3)

# =====================================================================================================
# KAPITEL 4: BAD
# =====================================================================================================
K = "4 Planung – Bad"
BAD = ("bad",)
R("BA-01", K, "Lage", ("wohnung",), ("bad",),
  "die Wohnung wird geplant",
  "Bad abseits der Hauptsichtachsen, nie am Eingang, nicht neben Küche oder Schlafzimmer, nicht in der Mitte",
  "Wie beim Körper: Das WC ist der 'Ausgang' und gehört nicht neben den 'Mund' (Haustür).", "", 3)
R("BA-02", K, "Farben", BAD, ("farben",),
  "das Bad ist rot oder in Feuerfarben gestaltet",
  "keine Feuerfarben; Erde und Holz gleichen das Wasser aus", "Feuer zerstört Wasser.", "", 3,
  profil=[("wandfarbe_element", "==", "feuer")])
R("BA-03", K, "Lüftung", BAD, ("fenster",),
  "das Bad ist schlecht belüftet", "gute natürliche oder mechanische Lüftung", "Feuchtigkeit muss raus.", "", 2,
  profil=[("bad_lueftung", "==", False)])
R("BA-04", K, "Kein Spiegel auf das WC", BAD, ("spiegel", "wc"),
  "ein Spiegel spiegelt das WC", "Spiegel umhängen", "", "", 2, pruefung=("grundriss:BA5",))
R("BA-05", K, "WC nicht von der Tür sichtbar", BAD, ("wc", "tuer"),
  "man sieht das WC von der Tür aus", "WC außer Sicht, nicht in Linie mit der Tür, aber mit Blick zur Tür",
  "Sieht man es nicht, mildert sich seine Wirkung; ein Blick zur Tür gibt Sicherheit.", "", 1,
  pruefung=("grundriss:BA1",))
R("BA-06", K, "Licht im Bad", BAD, ("fenster", "licht"),
  "das Bad ist dunkel", "Tageslicht ideal; sonst helle Wände und helle Leuchten", "", "", 2)
R("BA-07", K, "WC-Deckel", BAD, ("wc",),
  "der WC-Deckel bleibt offen", "Deckel immer schließen", "Sonst 'spült man das Glück hinunter'.", "", 3,
  profil=[("wc_deckel_offen", "wahr", None)])
R("BA-08", K, "Pflanzen im Bad", BAD, ("pflanze", "fenster"),
  "das Bad hat ein Fenster", "Pflanzen sind ideal (Holz + Wasser); ohne Fenster keine Pflanzen",
  "Die Feuchtigkeit lässt viele Pflanzen gedeihen.", "", 3)
R("BA-09", K, "WC an der Wand", BAD, ("wc", "wand", "fenster"),
  "das WC steht frei oder unter dem Fenster", "WC an eine feste Wand, nicht unters Fenster",
  "Auch auf dem WC gilt die Kommandoposition.", "", 2, pruefung=("grundriss:BA1",))
R("BA-10", K, "WC weg von der Wanne", BAD, ("wc", "badewanne", "dusche"),
  "das WC steht neben der Badewanne", "Abstand; die Dusche neben dem WC ist eher okay",
  "Niemand will beim Baden das WC neben dem Gesicht haben.", "Waschbecken dazwischen.", 2,
  pruefung=("grundriss:BA2",))
R("BA-11", K, "WC-Nische", BAD, ("wc",),
  "das WC steht offen im Bad", "idealerweise eigener Raum oder eigene Nische", "", "", 3)
R("BA-12", K, "Badewanne", BAD, ("badewanne", "dusche", "tuer"),
  "die Badewanne wird platziert",
  "erstes und wichtigstes Element beim Eintreten, Fußende nicht in Linie zur Tür; Dusche möglichst nicht in Linie",
  "Die Wanne erinnert daran, dass das Bad ein Ort der Erholung ist.", "", 2, pruefung=("grundriss:BA3",))
R("BA-13", K, "Waschbecken", BAD, ("waschbecken", "tuer"),
  "das Waschbecken wird platziert",
  "nicht mit dem Rücken zur Tür; Waschtisch und Spiegel rechtwinklig zur Tür; trennt WC und Wanne",
  "", "", 2, pruefung=("grundriss:BA4",))
R("BA-14", K, "Kleines Bad", BAD, (),
  "das Bad ist klein",
  "nirgends durchquetschen; Standflächen gemeinsam nutzen; Eckmontage ist erlaubt", "", "", 3,
  pruefung=("grundriss:H04",))
R("BA-15", K, "Fensterloses Bad", BAD, ("fenster", "spiegel", "pflanze"),
  "das Bad hat kein Fenster",
  "Lüfter; helle Wandleuchten neben dem Spiegel statt Licht von oben; keine Pflanzen; große Spiegel; "
  "Naturstein; Düfte", "Die Luft darf nicht abstehen.", "", 2)
R("BA-16", K, "Großes Bad", BAD, ("badewanne", "wc"),
  "das Bad ist groß", "auf Erholung ausrichten: Wanne als Anker, WC abschirmen, großzügige Dusche", "", "", 3)
R("BA-17", K, "Unregelmäßiges Bad", BAD, ("wc",),
  "das Bad hat Ecken und Nischen", "WC in eine Ecke als private Nische, Einbauschränke in Nischen", "", "", 3)

# =====================================================================================================
# KAPITEL 4: GEMEINSAME RÄUME
# =====================================================================================================
K = "4 Planung – Gemeinsame Räume"
R("GR-01", K, "Zonen", ("studio", "wohnzimmer", "schlafzimmer"), (),
  "ein Raum hat mehrere Funktionen",
  "in Bereiche gliedern; Funktionen nicht vermischen (nicht im Bett arbeiten, nicht auf dem Sofa essen); "
  "wandelbare Möbel minimieren", "Wir verbinden Orte im Kopf mit Tätigkeiten.", "", 2, pruefung=("grundriss:C05",))
R("GR-02", K, "Nach Aktivität ordnen", ("studio", "wohnzimmer", "schlafzimmer"), (),
  "Bereiche werden verteilt", "ähnlich aktive Tätigkeiten nebeneinander; Ruhiges nah am Bett, Aktives weit weg",
  "", "", 2, pruefung=("grundriss:ST1", "grundriss:C05"))
R("GR-03", K, "Wohnen + Essen", ("wohnzimmer", "studio"), ("esstisch", "sofa"),
  "Wohnen und Essen sind in einem Raum",
  "Esstisch nicht in den Wohnbereich ragen lassen, niedrige Konsole als Trenner; Essbereich näher zur Küche bzw. "
  "zum aktiveren Ende; Pendelleuchten nur über dem Esstisch", "", "", 2, pruefung=("grundriss:L02",))
R("GR-04", K, "Wohnen + Essen + Küche", ("studio", "wohnzimmer"), ("herd", "esstisch", "spiegel"),
  "Wohnen, Essen und Küche sind ein Raum",
  "Küche ruhig (niedrige Schränke, neutrale Farben, aufgeräumt); Esstisch mit mehr Plätzen als die Theke; "
  "Spiegel nur auf der Essseite; Leuchte über dem Tisch, nicht über der Theke",
  "Die Küche ist hier Anhängsel – Essen und Wohnen bestimmen die Stimmung.", "", 2)
R("GR-05", K, "Küche + Essen", ("kueche",), ("esstisch",),
  "der Esstisch steht in der Küche",
  "keine gepolsterten Sitze, lässiger Stil, Pendelleuchte über dem Tisch; isst du an der Theke, sie wie einen Tisch "
  "dekorieren", "", "", 3)
R("GR-06", K, "Arbeiten im Wohnbereich", ("wohnzimmer", "studio", "kueche"), ("schreibtisch", "esstisch"),
  "du arbeitest im Wohnzimmer oder am Esstisch",
  "eigener kleiner Schreibtisch weit weg von Küche, Durchgängen und Eingang; am Esstisch einen festen Arbeitsbereich; "
  "Obst/Blumen beim Arbeiten weg; TV aus; nicht arbeiten, während andere kochen", "", "", 2,
  pruefung=("grundriss:K06",))
R("GR-07", K, "Schlafen + Arbeiten", ("schlafzimmer", "studio"), ("bett", "schreibtisch"),
  "Schlaf- und Arbeitsbereich teilen sich den Raum",
  "Arbeitsbereich näher zur Tür und im helleren Teil, Schlafbereich hinten; ist das Bett nahe der Tür, in eine "
  "geschützte Nische", "Besser im Wohnbereich arbeiten als im Schlafzimmer.", "", 1, pruefung=("grundriss:C05",))
R("GR-08", K, "Studio-Schichten", ("studio",), ("bett", "sofa", "esstisch", "herd"),
  "die ganze Wohnung ist ein Raum",
  "Bett hinten (privat) → Wohnbereich als Puffer → Essen nahe der Küche → Küche weit weg vom Schlafbereich, "
  "eher Richtung Fenster; Eingangsbereich nicht zustellen", "", "", 1, pruefung=("grundriss:ST1",))
R("GR-09", K, "Haustiere: Käfige", ("alle",), ("kaefig",),
  "Vogel, Nager, Fische oder Reptilien werden untergebracht",
  "nicht in Küche (Dämpfe), Bad (Feuchte) oder Schlafzimmer (Unruhe); Käfig an eine Wand, weg vom Eingang",
  "Tiere spüren den Raum oft stärker als wir.", "", 2, pruefung=("grundriss:T01",))
R("GR-10", K, "Haustiere: Hundebox, Kratzbaum", ("alle",), ("hundebox", "kratzbaum"),
  "eine Hundebox oder ein Kratzbaum wird aufgestellt",
  "so, dass das Tier die Tür sieht (Box) bzw. nah bei dir hoch sitzt (Kratzbaum)",
  "Geräusche ohne Quelle machen Tiere ängstlich; Tiere suchen ihre Kommandoposition.", "", 3,
  pruefung=("grundriss:T02",))
R("GR-11", K, "Haustiere: Futter und Klo", ("alle",), ("futternapf", "katzenklo"),
  "Futternapf und Katzenklo werden platziert",
  "getrennt voneinander und vom Schlafplatz; Klo privat; Futter nahe deinem Essplatz", "", "", 3,
  pruefung=("grundriss:T03",))

# =====================================================================================================
# KAPITEL 5: STYLING
# =====================================================================================================
K = "5 Styling – Eindruck"
R("EI5-01", K, "Erster Blick", ALLE, ("tuer", "bett", "sofa", "schreibtisch", "esstisch"),
  "der Raum wird gestaltet",
  "so gestalten, dass er vom Eingang aus gut aussieht; das Hauptmöbel verankert den Blick",
  "Der erste Eindruck zählt – vor allem für dich selbst, jeden Tag beim Heimkommen.", "", 2,
  pruefung=("grundriss:S08",))
R("EI5-02", K, "Stimmung des Bildes", ALLE, (),
  "die Ansicht vom Eingang wird komponiert",
  "Wohnzimmer großzügig und symmetrisch; Schlafzimmer ruhig mit Bett im Zentrum, waagrechten Linien, weichem Licht",
  "", "", 3)
R("EI5-03", K, "Unteres Drittel", ALLE, ("regal", "schrank"),
  "Stauraum hängt hoch an der Wand oder Kisten sind hoch gestapelt",
  "Stauraum ins untere Drittel; oberen zwei Drittel nur Deko (Bilder, Lampen, Pflanzen)",
  "So wirkt der Raum durchdacht und ruhig.", "", 2, pruefung=("grundriss:S02", "foto:F09"))

K = "5 Styling – Ordnung"
R("OR-01", K, "Kategorien", ALLE, (),
  "Dinge liegen ungeordnet herum",
  "alles kategorisieren, Unterkategorien bilden, keine 'Sonstiges'-Kisten",
  "Unordnung gegen deinen Willen blockiert das Chi – und die Gedanken.", "", 1, pruefung=("foto:F09",),
  profil=[("unordnung", "wahr", None)])
R("OR-02", K, "Am Ort der Nutzung", ALLE, (),
  "Dinge sind am falschen Ort", "jedes Ding dort lagern, wo es gebraucht wird (Kochbücher ins Bücherregal!)",
  "Ein gutes System versteht sogar ein Fremder.", "", 3)
R("OR-03", K, "Beschriftung", ALLE, ("schrank",),
  "Schränke haben Glastüren mit unordentlichem Inhalt", "Beschriftungen statt Glastüren",
  "Durch Glas sieht man das Durcheinander.", "", 3, profil=[("schranktueren_glas", "wahr", None)])
R("OR-04", K, "Zu viele Möbel", ALLE, (),
  "der Raum ist vollgestellt", "auch zu viele Möbel sind Unordnung; Türen nie zustellen",
  "Blockierte Türen = blockierter Zugang zur Welt.", "", 1,
  pruefung=("grundriss:H03", "grundriss:H04", "grundriss:H01", "grundriss:H02"))
R("OR-06", K, "Stauraum zugänglich", ALLE, ("schrank", "kommode"),
  "Schränke oder Kommoden lassen sich nicht richtig öffnen", "vor Schrankfronten Platz lassen",
  "Schwer zugänglicher Stauraum führt zu Unordnung.", "", 2, pruefung=("grundriss:H06",))
R("OR-05", K, "Geschmack finden", ALLE, (),
  "du weißt nicht, was dir gefällt",
  "Liste mit Dingen, die du liebst und hasst; das Gehasste entfernen; ein Lieblingsstück als Maßstab",
  "Feng Shui passt den Raum an deine natürlichen Neigungen an.", "", 3)

K = "5 Styling – Licht"
R("LI-01", K, "Gleiche Farbtemperatur", ALLE, ("leuchtmittel",),
  "die Leuchtmittel im Raum haben unterschiedliche Lichtfarben", "alle Leuchtmittel im Raum gleich",
  "Gemischte Lichtfarben wirken unruhig.", "", 2, profil=[("lichtfarbe_kelvin", "verschieden", None)])
R("LI-02", K, "Warmes Licht", ALLE, ("leuchtmittel",),
  "Leuchtmittel sind sehr kalt (≥ 4000 K) oder sehr orange (< 2500 K)",
  "2700–2900 K für Wohnräume; 4000 K nur, wenn die Arbeit es verlangt",
  "Tageslichtweiß verwirrt die Sinne, zu orange wirkt unnatürlich.", "", 2,
  profil=[("lichtfarbe_kelvin", "ausserhalb", (2500, 3500))])
R("LI-03", K, "Diffuses Licht im Schlafzimmer", SCHLAF, ("leuchtmittel",),
  "im Schlafzimmer sind klare, blendende Leuchtmittel",
  "Schlafzimmer immer diffus (Opal/Milchglas, Schirme); klare Leuchtmittel nur in Yang-Räumen",
  "Klares Licht ist Yang, diffuses Yin.", "", 2, profil=[("leuchtmittel", "==", "klar")])
R("LI-04", K, "Mehrere Lichtquellen", ALLE, ("licht",),
  "es gibt nur eine einzelne Lichtquelle", "mehrere niedrige Lichtquellen; aktive Zonen hell, Wege dunkler",
  "In der Natur kommt Licht aus vielen Richtungen.", "", 2, pruefung=("grundriss:L03", "foto:F16"),
  profil=[("anzahl_lichtquellen", "<", 3)])
R("LI-05", K, "Drei von vier Ecken", ALLE, ("stehleuchte", "tischleuchte"),
  "die Raumecken sind unbeleuchtet oder alle gleich hell",
  "drei von vier Ecken beleuchten, eine bewusst im Schatten (Yin)", "", "", 3, pruefung=("grundriss:L03",))
R("LI-06", K, "Licht am Fenster und am Flurende", ALLE, ("stehleuchte",),
  "Licht wird platziert",
  "Lampen vor Fenster (natürlicher Lichtort) und ans Ende langer Räume; unter Schrägen 'heben' sie die Decke",
  "", "", 3)
R("LI-07", K, "Form der Hängeleuchte", ALLE, ("pendelleuchte",),
  "eine Hängeleuchte wird gewählt",
  "rund (Metall/Himmel) oder dreieckig/kegelig (Feuer); keine eckigen, hochkant-rechteckigen oder wellenförmigen",
  "Erde, Holz und Wasser gehören auf den Boden, nicht an die Decke.", "", 3,
  profil=[("leuchten_form", "==", "eckig")])
R("LI-08", K, "Eine Statement-Leuchte", ALLE, ("pendelleuchte",),
  "mehrere Statement-Leuchten hängen im Raum",
  "nur eine pro Raum; bei hoher Decke mittig, sonst über Ess- oder Couchtisch; zwei nur, wenn gleich",
  "", "", 3, pruefung=("grundriss:L02",))
R("LI-09", K, "Downlight-Pendel", ALLE, ("pendelleuchte",),
  "eine Arbeits-Pendelleuchte hängt im Wohnzimmer oder Eingang",
  "nur über Ess-, Küchen- oder Arbeitstischen; nicht höher als der Kopf (Leuchtmittel nicht sichtbar)", "", "", 3)
R("LI-10", K, "Keine Arbeitsleuchte im Schlafzimmer", SCHLAF, ("arbeitsleuchte",),
  "eine gerichtete Arbeitsleuchte steht im Schlafzimmer", "diffuse Tischleuchte statt Arbeitsleuchte", "", "", 3,
  profil=[("arbeitsleuchte_im_schlafzimmer", "wahr", None)])
R("LI-11", K, "Uplighter", ALLE, ("uplighter",),
  "der Raum hat kein Fenster oder eine niedrige Decke",
  "Uplighter, die Licht an Wände und Decke werfen", "Sie wirken wie Licht in einer Grotte.", "", 3)
R("LI-12", K, "Spots", ALLE, ("spot",),
  "Spots sind auf Sitzplätze oder zufällige Bodenstellen gerichtet", "Spots auf Kunst und Tische richten",
  "Licht auf dem Gesicht blendet und stört.", "", 3, profil=[("spots_auf_sitzplatz", "wahr", None)])
R("LI-13", K, "Deckenleuchten", ALLE, ("deckenleuchte",),
  "eine flache, eckige Deckenleuchte ist die Hauptlichtquelle",
  "flache Deckenleuchten vermeiden (flaches Licht); wenn, dann rund", "", "", 3,
  profil=[("deckenleuchte", "==", "flach_eckig")])

K = "5 Styling – Farben"
R("FA-01", K, "Weiß", ALLE, ("farben",),
  "die Wände sind weiß, weil Weiß 'neutral' erscheint",
  "Weiß bewusst wählen (Metall, leicht angespannt); unsicher? Mittleres Grau ist vielseitiger",
  "Weiß ist keine Grundfarbe, sondern ein Ende der Skala.", "", 3, profil=[("wandfarbe", "in", ["weiss", "weiß"])])
R("FA-02", K, "Farbtemperatur", ALLE, ("farben",),
  "Farben werden für einen Raum gewählt",
  "warme Räume (Sonnenseite) kühler, kühle Räume wärmer; Töne untereinander stimmig", "", "", 3)
R("FA-03", K, "Sättigung", ALLE, ("farben",),
  "du bist unsicher bei der Wandfarbe", "weniger gesättigte Töne (Sand statt Gelb, Terrakotta statt Rot)",
  "Weniger Sättigung wirkt ruhiger.", "", 3)
R("FA-04", K, "Feuer sparsam", ALLE, ("farben",),
  "eine ganze Wand ist rot/orange", "Feuer in kleinen, kräftigen Dosen; große Flächen entsättigen (Terrakotta)",
  "Zu viel Feuer stört den Schlaf.", "", 2, profil=[("wandfarbe_element", "==", "feuer")])
R("FA-05", K, "Kein reines Schwarz", ALLE, ("farben",),
  "eine Wand ist schwarz", "nie reines Schwarz – sehr dunkles Blau oder Braun; Schwarz nur als Akzent",
  "Ein leichter Farbton lässt das Auge ruhen.", "", 2, profil=[("wandfarbe", "==", "schwarz")])
R("FA-06", K, "Kein Blau im Esszimmer", ("esszimmer",), ("farben",),
  "das Esszimmer ist blau", "kein Blau im Esszimmer", "Blau dämpft den Appetit.", "", 2,
  profil=[("wandfarbe", "in", ["blau", "dunkelblau", "hellblau", "graublau"])])
R("FA-07", K, "Grün dezent", ALLE, ("farben",),
  "eine Wand wird grün", "sehr dezent (Grau mit Grünstich); Holz lieber über Pflanzen zeigen", "", "", 3,
  profil=[("wandfarbe", "==", "grün")])

K = "5 Styling – Kunst und Objekte"
R("KS-01", K, "Nur Geliebtes", ALLE, ("bild",),
  "Bilder werden zum 'Füllen' der Wand gekauft",
  "nur Kunst, die dich berührt; keine Massenware zum Füllen", "Du siehst sie jeden Tag – sie prägt dich.", "", 2,
  profil=[("kunst_als_fueller", "wahr", None)])
R("KS-02", K, "Uhren", ALLE, ("uhr",),
  "eine Uhr wird aufgehängt", "nur wo Eile und Präzision passen – nicht in Ess- oder Schlafzimmer", "", "", 2,
  pruefung=("grundriss:E06", "foto:F10"))
R("KS-03", K, "Familienfotos", ALLE, ("foto",),
  "Familienfotos hängen hoch an der Wand oder über dem Kamin",
  "gerahmt auf Beistelltische nahe bei dir; nie über ein Feuer",
  "Hoch aufgehängte Porträts wirken wie eine Ausstellung (eher für Verstorbene).", "", 3,
  profil=[("familienfotos_hoch", "wahr", None)])
R("KS-04", K, "Zettel und Postkarten", ALLE, ("pinnwand",),
  "Zettel, Postkarten und Haftnotizen kleben an der Wand", "alles in EINE Pinnwand",
  "Sie sind Unordnung und stören den Gedankenfluss.", "", 2, profil=[("notizzettel_an_wand", "wahr", None)])
R("KS-05", K, "Motiv der Kunst", ALLE, ("bild",),
  "Kunst wird platziert",
  "Landschaften wirken wie Fenster, Menschen wie Spiegel, Grafiken wie Architektur; Porträts ziehen den Blick an; "
  "Worte an der Wand sorgfältig wählen", "", "", 3)
R("KS-06", K, "Vasen", ALLE, ("vase",),
  "Vasen stehen leer", "Vasen mit Blumen oder Obst füllen", "Nur so erfüllen sie ihren Zweck.", "", 3)
R("KS-07", K, "Bagua-Spiegel", ALLE, ("bagua",),
  "ein Bagua-Spiegel hängt in der Wohnung", "nie innen; der Autor rät ganz ab (unfreundliche Geste)", "", "", 2,
  profil=[("bagua_spiegel_innen", "wahr", None)])
R("KS-08", K, "Drachen", ALLE, ("drache",),
  "Drachenmotive werden aufgestellt", "ins Wohnzimmer – nicht ins Schlafzimmer oder Bad",
  "Drachen haben sehr viel Energie.", "", 2, pruefung=("grundriss:C06",))
R("KS-09", K, "Geldfrosch", ALLE, ("frosch",),
  "ein Geldfrosch wird aufgestellt", "nie direkt an den Eingang", "Dort ist zu viel Chi.", "", 3)
R("KS-10", K, "Fu-Hunde", ("flur",), ("fu_hunde",),
  "Fu-Hunde bewachen den Eingang", "immer als Paar; von innen nach außen gesehen: Weibchen rechts, Männchen links",
  "", "", 3)
R("KS-11", K, "Glückssymbole", ALLE, ("symbole",),
  "Glückssymbole werden genutzt",
  "Mandarinenten als Paar, wo Liebe wachsen soll; Segelschiff zeigt ins Haus; Schildkröte nach hinten; "
  "Kalebasse gegen schlechte Energie", "Es sind Symbole – keine Wunder; entscheidend ist dein Gefühl.", "", 3)
R("KS-12", K, "Geräte am richtigen Ort", ALLE, ("kuehlschrank", "mikrowelle"),
  "Küchengeräte stehen im Schlafzimmer", "Geräte dort, wo sie hingehören (Essen in der Küche)",
  "Klare Funktionen verbessern das Wohlbefinden.", "", 2)
R("KS-13", K, "Religiöse Objekte", ALLE, ("altar",),
  "religiöse Objekte stehen im Schlafzimmer, auf dem Boden oder in Linie mit dem Bett",
  "im wichtigsten Raum (Wohnzimmer); nicht im Schlafzimmer, nicht auf dem Boden, nicht in Linie mit dem Bett",
  "Sie haben eine ganz andere Energie als das Schlafzimmer.", "", 2, pruefung=("grundriss:C11",),
  profil=[("religioese_objekte", "wahr", None)])
R("KS-14", K, "Papier und Kartons", ALLE, ("karton",),
  "Papiere und Kartons liegen herum", "methodisch außer Sicht lagern; Unbenutztes wegwerfen",
  "Sie werden zu Unordnung.", "", 2, pruefung=("foto:F09",))
R("KS-15", K, "Bewegte Objekte", ALLE, ("mobile", "lavalampe"),
  "ein bewegtes Objekt wird aufgestellt",
  "Mobiles bringen sanfte Ruhe; was sich nachts unkontrolliert bewegt, gehört nicht ins Schlafzimmer", "", "", 3)
R("KS-16", K, "Windspiel", ALLE, ("windspiel",),
  "ein Windspiel wird aufgehängt",
  "wo zu viele Fenster sind oder in Durchgängen (z. B. Treppe vor der Haustür); nie über Bett oder Schreibtisch; "
  "hohle sind am besten", "Windspiele nehmen Chi auf und bremsen es.", "", 2, pruefung=("grundriss:C10",),
  profil=[("windspiel_ueber_bett", "wahr", None)])
R("KS-17", K, "Kleine Dinge gruppieren", ALLE, ("deko",),
  "kleine Objekte stehen verstreut",
  "in Gruppen oder einer Vitrine zusammenfassen, mit freiem Raum drumherum; große Stücke allein stellen",
  "Verstreutes wirkt zufällig.", "", 3)
R("KS-18", K, "Bilder aufhängen", ALLE, ("bild",),
  "Bilder werden aufgehängt",
  "kleine Bilder über Möbel oder als Gruppe mit einem Hauptbild; Augenhöhe; große Bilder mittig über niedrige "
  "Möbel; über zu hohe Möbel nichts hängen", "", "", 3, pruefung=("grundriss:H07",))
R("KS-19", K, "Größe und Form", ALLE, ("bild",),
  "ein Raum soll größer, höher oder breiter wirken",
  "größere Kunst = mehr Weite; hochformatige Bilder = höhere Decke; querformatige = breiterer Raum; runde Objekte "
  "symmetrisch zentrieren", "", "", 3)
R("KS-20", K, "Farbe über Objekte", ALLE, ("deko",),
  "du traust dich nicht an farbige Wände", "Farbe über Kunst, Skulpturen, Decken – mit Zurückhaltung und Kontrast",
  "", "", 3)

K = "5 Styling – Spiegel und Kristalle"
R("SP-01", K, "Spiegel wie Türen", ALLE, ("spiegel",),
  "ein Spiegel wird aufgehängt",
  "nicht dorthin, wo keine Bewegung sein soll (vor allem ums Bett, nie ans Fußende)",
  "Spiegel sind keine Bilder, sie verhalten sich wie Fenster und Türen.", "", 1, pruefung=("grundriss:C02",))
R("SP-02", K, "Nur Gutes verdoppeln", ALLE, ("spiegel",),
  "ein Spiegel zeigt etwas Unschönes (Herd, WC, Tür, TV)", "Spiegel so ausrichten, dass sie Schönes zeigen",
  "Spiegel verdoppeln alles, was sie zeigen.", "", 2, pruefung=("grundriss:C09", "grundriss:KU4", "grundriss:BA5"))
R("SP-03", K, "Fehlende Ecke", ("wohnzimmer", "esszimmer", "buero", "flur"), ("spiegel",),
  "dem Raum fehlt eine Ecke (L-Form)", "Spiegel ergänzt die Raumform (nicht im Schlafzimmer)", "", "", 3)
R("SP-04", K, "Bildschirme wie Spiegel", ALLE, ("tv",),
  "ein schwarzer Bildschirm spiegelt", "wie einen Spiegel behandeln", "", "", 2, pruefung=("grundriss:C04",))
R("SP-05", K, "Wo Spiegel gut sind", ALLE, ("spiegel",),
  "du suchst einen Platz für einen Spiegel",
  "Wohnzimmer, Esszimmer (gedeckter Tisch), ungeschützter Arbeitsplatz (Tür sehen), abgestandene Räume",
  "", "", 3)
R("SP-06", K, "Wo Spiegel schlecht sind", ALLE, ("spiegel",),
  "ein Spiegel hängt im Schlafzimmer, außen, im langen Flur (frontal) oder in der Küche", "dort vermeiden",
  "", "", 2, pruefung=("grundriss:C02", "grundriss:KU4"))
R("SP-07", K, "Qualität", ALLE, ("spiegel",),
  "der Spiegel ist geteilt (Spiegelfliesen), gesprungen oder verzerrt",
  "regelmäßige Form, ganze Person ohne Lücken, sauber, unverzerrt, nicht geteilt", "", "", 3,
  profil=[("spiegel_mangelhaft", "wahr", None)])
R("SP-08", K, "Höhe", ALLE, ("spiegel",),
  "der Spiegel hängt zu hoch oder zu tief", "Gesicht muss gut sichtbar sein",
  "Zu hoch macht haltlos, zu tief lässt dich bücken.", "", 3)
R("SP-09", K, "Nicht hinter dir", ALLE, ("spiegel",),
  "ein Spiegel hängt hinter deinem Sitzplatz", "nicht hinter dich",
  "Man fühlt sich beobachtet.", "", 2, pruefung=("grundriss:C02",))
R("SP-10", K, "Kristalle", ALLE, ("kristall",),
  "ein Ort hat zu viel oder zu wenig Chi",
  "klare, saubere Kristalle bei zu viel Chi (Tür auf Treppe/Bett) oder in stagnierenden Räumen; Jade für Holz",
  "Kristalle brechen Licht; ihre Kraft liegt in deiner Wahrnehmung.", "", 3)

K = "5 Styling – Wasser"
R("WA-01", K, "Bewegtes Wasser", ALLE, ("brunnen", "aquarium"),
  "Wasser steht still", "Wasser immer bewegt und sauber halten",
  "Stehendes Wasser steht für Verfall (Schimmel, Mücken).", "", 2, profil=[("wasser_stehend", "wahr", None)])
R("WA-02", K, "Kein Wasser über dir", ALLE, ("wasser",),
  "Wasser befindet sich über dir", "Wasser nicht 'über' dir",
  "Wasser oben bedeutet Lecks und Überschwemmung.", "", 3)
R("WA-03", K, "Wasser im Büro, nicht im Schlafzimmer", ALLE, ("aquarium", "brunnen"),
  "ein Wasserobjekt wird aufgestellt", "gut fürs Arbeiten (Wohlstand); nie ins Schlafzimmer",
  "Im Schlafzimmer bringt Wasser zu viel Energie.", "", 2, pruefung=("grundriss:C06", "foto:F11"))
R("WA-04", K, "Aquarium pflegen", ALLE, ("aquarium",),
  "ein Aquarium wird gehalten", "gesund und sauber halten", "", "", 2,
  profil=[("aquarium_ungepflegt", "wahr", None)])
R("WA-05", K, "Ersatz für Wasser", ALLE, ("pflanze", "bild"),
  "es gibt kein Wasser im Raum",
  "Pflanzen, glänzend-blaue Keramik oder ruhige Wasserbilder (keine stürmische See)", "", "", 3)

K = "5 Styling – Pflanzen"
R("PF-01", K, "Pflege", ALLE, ("pflanze",),
  "Pflanzen werden nicht gepflegt", "lieber keine Pflanze als eine tote",
  "Tote Pflanzen stehen für Verfall.", "", 1, profil=[("tote_pflanzen", "wahr", None)])
R("PF-02", K, "Wofür Pflanzen", ALLE, ("pflanze",),
  "der Raum hat spitze Wandecken, grelles Licht, dunkle Bereiche oder lange Flure",
  "Pflanzen verdecken Ecken, mildern Fenster, beleben Yin-Bereiche und lange Flure", "", "", 3)
R("PF-03", K, "Pflanzen im Schlafzimmer", SCHLAF, ("pflanze", "bett"),
  "Pflanzen stehen im Schlafzimmer",
  "möglichst keine; wenn doch, als Gruppe direkt ans Fenster, das Bett weit weg",
  "Pflanzen bringen Energie und konkurrieren nachts um Sauerstoff.", "", 2, pruefung=("grundriss:C03", "foto:F08"))
R("PF-04", K, "Pflanzen gruppieren", ("wohnzimmer", "esszimmer", "studio"), ("pflanze",),
  "Pflanzen sind im Raum verstreut", "in Gruppen nahe den Fenstern", "", "", 3, pruefung=("grundriss:C03",))
R("PF-05", K, "Pflanzen in der Küche", KUE, ("pflanze", "herd"),
  "eine Pflanze steht neben dem Herd", "nicht direkt an den Herd", "Holz nährt Feuer.", "", 3)
R("PF-06", K, "Pflanzen im Bad", BAD, ("pflanze", "fenster"),
  "ein Bad ohne Fenster hat Pflanzen", "Pflanzen nur in Bädern mit Fenster", "", "", 3)
R("PF-07", K, "Beste Pflanzen", ALLE, ("pflanze",),
  "Pflanzen werden ausgesucht",
  "große, weiche, runde Blätter (Monstera, Geldbaum, Peperomia), Farne, rundblättrige Sukkulenten; die vier "
  "Edlen (Orchidee, Bambus, Chrysantheme, Pflaumenblüte)", "", "", 3)
R("PF-08", K, "Kakteen", ALLE, ("kaktus",),
  "ein Kaktus steht in der Wohnung", "Kakteen nach draußen",
  "Stacheln wirken aggressiv und stehen für unwirtliches Klima.", "", 2, pruefung=("foto:F08",),
  profil=[("pflanzenarten", "enthaelt", "kaktus")])
R("PF-09", K, "Spitze Pflanzen", ALLE, ("bogenhanf", "aloe vera", "palme"),
  "Pflanzen mit spitzen Blättern (Bogenhanf, Aloe, aufrechte Palmen) stehen in ruhigen Räumen",
  "als Feuer behandeln: nur in energiereiche Räume", "", "", 3,
  profil=[("pflanzenarten", "enthaelt_eines", ["bogenhanf", "aloe vera", "palme", "dracaena"])])
R("PF-10", K, "Keine Kunstpflanzen", ALLE, ("kunstpflanze",),
  "Kunstpflanzen stehen im Raum", "vermeiden; lieber Mobile, Skulpturleuchte oder volle Obstschale",
  "Sie erneuern sich nicht und sammeln Staub.", "", 2, profil=[("kunstpflanzen", "wahr", None)])
R("PF-11", K, "Nicht grün streichen als Ersatz", ALLE, ("farben",),
  "etwas wird grün gestrichen, um Pflanzen zu ersetzen", "lieber lebendige Alternativen", "Wirkt künstlich.", "", 3)

K = "5 Styling – Garten und Balkon"
R("GB-01", K, "Garten als Raum", ("garten",), (),
  "ein Garten wird gestaltet",
  "Mittelpunkt (Brunnen, Bank, Lichtung), Wege drumherum, Sitzplätze in Kommandoposition, hohe Pflanzen hinten",
  "", "", 3)
R("GB-02", K, "Wasser vorne", ("garten",), ("wasser",),
  "ein Wasserobjekt kommt in den Garten", "vor das Haus, nicht dahinter", "", "", 3)
R("GB-03", K, "Gebogene Wege", ("garten",), (),
  "ein Weg führt gerade auf die Tür zu", "sanft gebogene Wege; vor langer Einfahrt ein Kreisel/Pflanzkübel",
  "Gerade Wege lassen aggressives Chi hereinrauschen.", "", 3)
R("GB-04", K, "Balkon nutzen", ("balkon", "wohnzimmer", "schlafzimmer"), ("balkontuer",),
  "der Balkon ist kahl oder der Zugang zugestellt",
  "Balkon begrünen und nutzen; Zugang nie verstellen; um die Möbel herumgehen können",
  "Den Zugang zu verschließen macht die Raumwirkung nur schlimmer.", "", 1, pruefung=("grundriss:S03",))
R("GB-05", K, "Aussicht", ("balkon", "alle"), ("fenster",),
  "die Aussicht ist schön bzw. unschön",
  "schöne Aussicht nicht verdecken (niedrige Pflanzen, hohe seitlich); unschöne mit üppigen Pflanzen weicher machen, "
  "aber nicht zubauen", "Man braucht das Licht.", "", 3, pruefung=("grundriss:S03",))
R("GB-06", K, "Ohne Außenbereich", ("alle",), ("fenster", "pflanze"),
  "die Wohnung hat keinen Balkon",
  "Bank oder Liege ans Fenster; Pflanzen auf Fensterbänke oder nahe ans Fenster", "So entsteht Naturverbindung.",
  "", 3)


# =====================================================================================================
# AUSWERTUNG
# =====================================================================================================
KAPITEL_PRAEFIX = {"schlafzimmer": "SZ", "kinderzimmer": "SZ", "gaestezimmer": "SZ", "wohnzimmer": "WZ",
                   "esszimmer": "EZ", "kueche": "KU", "buero": "BU", "bad": "BA", "studio": "GR", "flur": "EI"}


def regeln_fuer_raum(raumtyp: str) -> list[BuchRegel]:
    return [r for r in BUCHREGELN if r.gilt_fuer(raumtyp)]


def regeln_zu_pruefung(pruef_id: str, raumtyp: Optional[str] = None) -> list[BuchRegel]:
    """Buchregeln, die durch eine Code-Prüfung (z. B. 'grundriss:K04' oder 'K04') abgedeckt sind."""
    if ":" not in pruef_id:
        pruef_id = ("foto:" if pruef_id.startswith("F") and pruef_id[1:].isdigit() else "grundriss:") + pruef_id
    treffer = [r for r in BUCHREGELN if pruef_id in r.pruefung]
    if raumtyp:
        passend = [r for r in treffer if r.gilt_fuer(raumtyp)]
        treffer = passend or treffer
    # Regeln aus dem Kapitel dieses Raums zuerst, dann raumspezifische vor allgemeinen, dann nach Wichtigkeit
    kap = KAPITEL_PRAEFIX.get(raumtyp or "", "")
    return sorted(treffer, key=lambda r: (not (kap and r.id.startswith(kap + "-")), "alle" in r.raeume,
                                          raumtyp not in r.raeume if raumtyp else 0, r.prio, r.id))


def _bedingung(wert: Any, op: str, ziel: Any) -> Optional[bool]:
    """Wertet eine Profil-Bedingung aus. None = nicht auswertbar (Angabe fehlt)."""
    if wert is None:
        return None
    if op == "wahr":
        return bool(wert)
    if op == "==":
        return str(wert).lower() == str(ziel).lower() if isinstance(ziel, str) else wert == ziel
    if op == "!=":
        return wert != ziel
    if op == "in":
        return str(wert).lower() in [str(z).lower() for z in ziel]
    if op == "<":
        return float(wert) < ziel
    if op == ">":
        return float(wert) > ziel
    liste = wert if isinstance(wert, (list, tuple, set)) else [wert]
    if op == "enthaelt":
        return str(ziel).lower() in [str(x).lower() for x in liste]
    if op == "enthaelt_eines":
        return any(str(x).lower() in [str(z).lower() for z in ziel] for x in liste)
    if op == "verschieden":
        return len(set(liste)) > 1
    if op == "ausserhalb":
        lo, hi = ziel
        return any(not (lo <= float(x) <= hi) for x in liste)
    raise ValueError(f"Unbekannter Operator {op}")


def pruefe_profil(profil: dict, raumtyp: str) -> tuple[list[BuchRegel], list[BuchRegel]]:
    """Wendet alle Profil-Regeln an. Rückgabe: (verletzte Regeln, nicht auswertbare Regeln)."""
    verletzt, offen = [], []
    for r in regeln_fuer_raum(raumtyp):
        if not r.profil:
            continue
        ergebnisse = [_bedingung(profil.get(k), op, z) for k, op, z in r.profil]
        if any(e is None for e in ergebnisse):
            offen.append(r)
        elif all(ergebnisse):
            verletzt.append(r)
    return verletzt, offen


def abgeleitetes_profil(profil: dict, raum=None) -> dict:
    """Ergänzt das Profil um berechnete Felder (Element der Wandfarbe, Hauptrichtung, fehlende Elemente …)."""
    from . import wissen as W
    p = dict(profil)
    wf = (p.get("wandfarbe") or "").lower()
    if wf and "wandfarbe_element" not in p:
        p["wandfarbe_element"] = W.FARBE_ZU_ELEMENT.get(wf)
    farben = [wf] + [f.lower() for f in p.get("akzentfarben", [])] if wf else []
    if farben and "elemente_fehlen" not in p:
        da = {W.FARBE_ZU_ELEMENT.get(f) for f in farben} - {None}
        if p.get("pflanzenarten"):
            da.add("holz")
        p["elemente_fehlen"] = len(da) < 4
    if raum is not None:
        p.setdefault("anzahl_tueren", len([o for o in raum.oeffnungen if o.typ == "tuer"]))
        if raum.fenster and raum.nord_wand and "hauptrichtung" not in p:
            from collections import Counter
            r = Counter(raum.himmelsrichtung(f.wand) for f in raum.fenster).most_common(1)[0][0]
            if raum.suedhalbkugel:
                r = {"N": "S", "S": "N"}.get(r, r)
            p["hauptrichtung"] = r
    return p


def abdeckung() -> dict:
    """Wie viele Buchregeln automatisch geprüft werden."""
    from collections import Counter
    c = Counter(r.art for r in BUCHREGELN)
    return {"gesamt": len(BUCHREGELN), **c,
            "automatisch": c["grundriss"] + c["foto"] + c["profil"]}
