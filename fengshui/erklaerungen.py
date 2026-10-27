"""
Begründungen aus dem Buch (sinngemäß, Form-Schule Feng Shui) für jede Regel.

Für jede Regel-ID:
    warum   – die Logik hinter der Regel (Chi, fünf Tiere, Elemente, Gefühl im Raum)
    abhilfe – was du tun kannst, wenn sich das Möbel NICHT umstellen lässt

Das Buch betont: Hinter jeder Feng-Shui-Regel steckt ein logischer Grund – meist, wie
sicher, ruhig oder lebendig wir uns in einem Raum fühlen.
"""

ERKLAERUNG: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------------ praktisch / hart
    "H01": {"warum": "Möbel, die sich berühren oder überschneiden, sind im echten Raum nicht möglich und wirken "
                     "gedrängt – zu viele Möbel zählen im Buch selbst als Unordnung.",
            "abhilfe": "Ein Möbel weglassen oder ein kleineres wählen."},
    "H02": {"warum": "Das Möbel passt nicht in den Raum.", "abhilfe": "Maße prüfen oder ein kleineres Möbel wählen."},
    "H03": {"warum": "Die Tür ist der Mund des Raums: Durch sie kommt das Chi herein. Eine blockierte Tür steht "
                     "für einen blockierten Zugang zur Welt.",
            "abhilfe": "Den Bereich, in den die Tür aufschwingt, immer frei lassen."},
    "H04": {"warum": "Chi fließt wie ein Mensch durch den Raum. Wo man sich durchquetschen muss, staut sich die "
                     "Energie und der Raum fühlt sich eng an.",
            "abhilfe": "Mindestens 60 cm Laufweg frei halten; Kleinmöbel reduzieren."},
    "H05": {"warum": "Ohne Platz für Stuhl und Rücken sitzt du eingeklemmt – das Gegenteil der Kommandoposition.",
            "abhilfe": "Etwa 70 cm hinter dem Schreibtisch frei lassen."},
    "H06": {"warum": "Schränke, die man nicht richtig öffnen kann, führen zu Unordnung – und Unordnung blockiert Chi.",
            "abhilfe": "Vor Fronten 60 cm frei lassen."},
    "H07": {"warum": "Spiegel und Bilder brauchen eine echte Wand; über Türen/Fenstern stören sie Licht und Durchgang.",
            "abhilfe": "An eine geschlossene Wandfläche hängen."},
    # ------------------------------------------------------------------ Kommandoposition
    "K01": {"warum": "Die Schildkröte (Rücken) steht für Schutz und Stabilität. Wo du nicht hinsiehst, brauchst du "
                     "eine feste Wand – sonst bleibt der Körper unbewusst in Alarmbereitschaft, und man schläft "
                     "oder arbeitet schlechter.",
            "abhilfe": "Massives, hohes Kopfteil; beim Sofa eine niedrige Konsole dahinter; am Schreibtisch ein "
                       "Stuhl mit hoher Lehne."},
    "K02": {"warum": "Ein Fenster im Rücken ist das Gegenteil der schützenden Schildkröte: Man fühlt sich "
                     "beobachtet und ungeschützt, Zugluft und Licht stören den Schlaf.",
            "abhilfe": "Fensterbank höher als das Kopfteil, massives Kopfteil, schwere Vorhänge nachts schließen."},
    "K03": {"warum": "Wie im Café wählt man instinktiv den Platz, von dem man die Tür sieht. Wer die Tür nicht "
                     "sieht, fühlt sich unbewusst unsicher – jemand könnte unbemerkt hereinkommen.",
            "abhilfe": "Ein Spiegel, in dem du die Tür siehst (nicht im Schlafzimmer!), oder die Tür meist "
                       "geschlossen halten."},
    "K04": {"warum": "Füße in direkter Linie zur Tür: Das Chi strömt direkt auf dich zu, und die Position erinnert "
                     "an einen Sarg, der mit den Füßen voran hinausgetragen wird – sehr ungünstig.",
            "abhilfe": "Paravent oder schweres Möbel (Bank, Truhe) ans Fußende; Bereich vor der Tür ruhig halten."},
    "K05": {"warum": "Ein großes Fenster am Fußende bringt viel Bewegungs-Chi (Licht, Wind) direkt aufs Bett.",
            "abhilfe": "Vorhänge nachts schließen; bei kleinen Fenstern oder ruhigem Ausblick ist es okay."},
    "K06": {"warum": "Durch die Tür kommt das stärkste Chi. Direkt daneben zu schlafen oder zu arbeiten heißt, "
                     "ständig im Durchzug von Energie, Geräuschen und Menschen zu sein – man kommt nicht zur Ruhe.",
            "abhilfe": "So weit wie möglich vom Eingang weg; Tür nachts schließen; Paravent als Puffer."},
    "K07": {"warum": "An der Türwand kann man die Tür nicht überblicken – man sieht nicht, wer hereinkommt.",
            "abhilfe": "Bett an die Wand gegenüber oder schräg gegenüber der Tür stellen."},
    "K08": {"warum": "Balken, schwere Lampen oder Ventilatoren über dir wirken wie eine Klinge über dem Kopf. "
                     "Man weiß, dass nichts passiert – fühlt sich aber trotzdem bedrückt (wie unter dem "
                     "schwankenden Kronleuchter).",
            "abhilfe": "Balken in Deckenfarbe streichen oder verkleiden; Bett so stellen, dass kein Balken quer darüber läuft."},
    "K09": {"warum": "Unter dem niedrigen Teil einer Dachschräge drückt die Decke optisch auf den Kopf.",
            "abhilfe": "Kopf an die hohe Seite; Lampen am niedrigen Ende 'heben' die Decke optisch."},
    "K10": {"warum": "Ein Bett, das man nur von einer Seite betreten kann, ist für eine Person gemacht. Für Paare "
                     "ist beidseitiger Zugang wichtig – für Singles steht er für Offenheit für einen Partner.",
            "abhilfe": "Bett etwas von der Wand abrücken; zwei Nachttische mit gleichem Gewicht."},
    "K11": {"warum": "Kinder schlafen geborgener, wenn eine Längsseite an der Wand liegt.",
            "abhilfe": "Einzelbett mit der Längsseite an die Wand schieben."},
    "K12": {"warum": "Der Vogel (vorne) braucht offenen Raum: Weite vor dir gibt Überblick und das Gefühl, "
                     "planen zu können. Zu wenig Raum wirkt beengend.",
            "abhilfe": "Platz vor Bett/Sofa frei halten; am Wandtisch Bilder oder Pinnwand für 'Tiefe'."},
    "K13": {"warum": "Licht von der Seite ist am angenehmsten zum Arbeiten. Blick ins Fenster blendet und lenkt ab, "
                     "ein Fenster im Rücken gibt das Gefühl, beobachtet zu werden.",
            "abhilfe": "Schreibtisch quer zum Fenster stellen; Vorhang/Rollo gegen Blendung."},
    "K14": {"warum": "Spitze Ecken erzeugen 'tötendes' Sha-Chi: Wie eine Messerspitze, die auf dich zeigt, "
                     "signalisieren sie dem Unterbewusstsein Gefahr – auch wenn sie dich nie berühren.",
            "abhilfe": "Runde Möbel wählen, Ecken mit Pflanzen oder Stoff abmildern, Möbel so drehen, dass die "
                       "Kanten nicht auf Bett oder Sitzplatz zeigen."},
    "K15": {"warum": "In langen Räumen fließt Chi zu schnell – wie in einem Korridor. Ein Bett längs darin fühlt "
                     "sich an wie Schlafen im Flur.",
            "abhilfe": "Möbel quer stellen; Bilder an den Längswänden verbreitern den Raum optisch."},
    "K16": {"warum": "Ein mittig und symmetrisch stehendes Bett verankert den Raum und wirkt ruhig und ausgeglichen.",
            "abhilfe": "Zwei gleich schwere Nachttische und Lampen links und rechts."},
    # ------------------------------------------------------------------ Chi
    "C01": {"warum": "Chi fließt von der Tür zum Fenster. Liegen beide sich gegenüber, schneidet es schnell durch "
                     "den Raum. Wer in dieser Bahn schläft oder arbeitet, sitzt im 'Durchzug' und findet keine Ruhe.",
            "abhilfe": "Paravent, Pflanze oder Möbel in die Bahn stellen, damit das Chi sanft mäandert; "
                       "Vorhänge nachts schließen."},
    "C02": {"warum": "Spiegel verhalten sich wie Türen und Fenster: Sie bringen Bewegung in den Raum und "
                     "verdoppeln, was sie zeigen. Siehst du dich im Bett im Spiegel, entsteht nachts Unruhe; "
                     "gegenüber der Eingangstür lenken sie das Chi wieder hinaus.",
            "abhilfe": "Spiegel so hängen, dass man sich vom Bett aus nicht sieht, oder nachts abdecken; "
                       "nie gegenüber der Tür oder am Fußende."},
    "C03": {"warum": "Pflanzen sind Leben und Yang-Energie (Holz). Im Schlafzimmer sucht man aber Ruhe und "
                     "Dunkelheit; zudem brauchen Pflanzen Licht – eine tote Pflanze ist schlechter als keine.",
            "abhilfe": "Pflanzen gruppiert direkt ans Fenster, weit weg vom Bett; im Zweifel ins Wohnzimmer."},
    "C04": {"warum": "Bildschirme bringen Arbeit und Unruhe ins Schlafzimmer; glänzende schwarze Flächen wirken "
                     "zudem wie Spiegel.",
            "abhilfe": "TV/Computer raus oder nachts abdecken und ausschalten; Handy nicht ans Bett."},
    "C05": {"warum": "Schlafen und Arbeiten brauchen verschiedene Energie. Ohne klare Zonen denkt man im Bett an "
                     "Arbeit. Arbeitsplatz nach vorne (aktiv, hell), Bett nach hinten (ruhig).",
            "abhilfe": "Raumteiler, Teppich oder Regal zur Trennung; Arbeit nie auf dem Bett."},
    "C06": {"warum": "Wasser, Aquarien und Drachen bringen viel Yang-Energie – im Schlafzimmer stört das die Ruhe.",
            "abhilfe": "Ins Wohnzimmer oder Büro stellen."},
    "C07": {"warum": "In älteren Gebäuden überträgt die Außenwand Kälte und Feuchte auf den Schlafplatz.",
            "abhilfe": "Etwas Abstand zur Wand, gut isolierendes Kopfteil."},
    # ------------------------------------------------------------------ Stil
    "S01": {"warum": "Regale und schwere (Glas-)Bilder über dem Kopf sind eine Gefahr, falls sie fallen – und "
                     "auch ohne Sturz wirken sie bedrückend.",
            "abhilfe": "Nur leichte Textilien oder ein Wandgemälde über dem Bett; Regale versetzen."},
    "S02": {"warum": "Stauraum gehört ins untere Drittel, die oberen zwei Drittel bleiben frei für Deko. Hohe "
                     "offene Regale erzeugen aggressives Chi und wirken unordentlich.",
            "abhilfe": "Niedrige Sideboards oder Schränke mit Türen statt hoher offener Regale."},
    "S03": {"warum": "Fenster bringen Licht und Leben. Zugestellte Fenster schneiden die Verbindung nach "
                     "draußen ab und machen den Raum dunkel.",
            "abhilfe": "Nur niedrige Möbel oder Pflanzen vors Fenster; Balkontür immer frei."},
    "S04": {"warum": "Der Esstisch ist das Herz des Hauses und soll mittig stehen, mit Platz rundum, damit "
                     "niemand eingeklemmt sitzt.",
            "abhilfe": "Tisch von der Wand abrücken; wenn nicht möglich, einen Spiegel an die Wand."},
    "S05": {"warum": "Steht der Fernseher im Mittelpunkt, zeigt der Raum, dass er wichtiger ist als die Menschen.",
            "abhilfe": "TV niedrig in eine Ecke, Sitzgruppe zueinander ausrichten."},
    "S06": {"warum": "Sitzmöbel, die sich anschauen, laden zum Gespräch ein. Ein einzelner Stuhl abseits wirkt "
                     "wie ein unwillkommener Gast.",
            "abhilfe": "Sessel diagonal zum Sofa, Couchtisch als Mitte."},
    "S07": {"warum": "Der Fernseher soll nutzbar, aber nicht dominant sein.", "abhilfe": "TV seitlich, nicht frontal zentriert."},
    # ------------------------------------------------------------------ Licht
    "L01": {"warum": "Eine schwere Hängeleuchte über Bett oder Sitzplatz hängt wie eine Last über dir – man "
                     "fühlt sich unbewusst bedroht.",
            "abhilfe": "Leuchte über Couch- oder Esstisch hängen; über dem Bett höchstens eine leichte Papierleuchte."},
    "L02": {"warum": "Die Pendelleuchte über dem Tisch zieht die Menschen an den Tisch und gibt dem Raum ein Zentrum.",
            "abhilfe": "Mittig über dem Tisch aufhängen; nur eine Statement-Leuchte pro Raum."},
    "L03": {"warum": "Natürliches Licht kommt aus vielen Richtungen. Mehrere niedrige Lampen wirken angenehmer "
                     "als ein einzelnes Deckenlicht; eine dunkle Ecke gibt Yin und Tiefe.",
            "abhilfe": "Drei von vier Ecken mit warmen Steh-/Tischleuchten (2700 K) beleuchten."},
    # ------------------------------------------------------------------ Esszimmer
    "E01": {"warum": "Runde Tische haben keine Ecken und keine Rangordnung – alle sind gleich.",
            "abhilfe": "Eckige Tischkanten mit Tischdecke oder Läufer weicher wirken lassen."},
    "E02": {"warum": "Gleiche Stühle in gerader Zahl zeigen Fairness und Gemeinschaft; ein Stuhl abseits oder an "
                     "der Ecke wirkt ausgeschlossen.",
            "abhilfe": "Ersatzstühle aus dem Raum; Stühle gleichmäßig an die Längsseiten."},
    "E03": {"warum": "Die Mitte gehört dem Esstisch, damit die Energie ihn umfließen kann.",
            "abhilfe": "Sideboards und Konsolen an die Wand."},
    "E04": {"warum": "Am Eingang ist zu viel Bewegung – dort kann niemand entspannt essen.",
            "abhilfe": "Konsole oder Pflanze zwischen Tür und Tisch."},
    "E05": {"warum": "Ein Spiegel, der den gedeckten Tisch zeigt, verdoppelt Fülle und Freude.",
            "abhilfe": "Spiegel auf den Tisch ausrichten, nie auf die Tür."},
    "E06": {"warum": "Uhren erzeugen Zeitdruck – beim Essen und Schlafen will man das nicht spüren.",
            "abhilfe": "Uhr in Flur oder Büro hängen."},
    # ------------------------------------------------------------------ Geteiltes Schlafzimmer
    "G01": {"warum": "Ungleiche Betten zeigen ein Ungleichgewicht zwischen den Personen; zusammengeschobene "
                     "Einzelbetten stehen für eine versteckte Trennung.",
            "abhilfe": "Gleich große Betten mit Abstand – oder ein gemeinsames Bett."},
    "G02": {"warum": "Die Füße einer Person zum Kopf einer anderen gelten als respektlos und unruhig.",
            "abhilfe": "Betten parallel oder Kopf an Kopf stellen."},
    "G03": {"warum": "Etagenbetten machen das Zimmer eng; die obere Person hat Decke direkt über sich.",
            "abhilfe": "Wenn nötig: die ältere Person schläft oben."},
    "ST1": {"warum": "In einem Ein-Raum-Apartment braucht das Bett den ruhigsten Teil; Wohnen ist Puffer; Küche "
                     "(Feuer) und Bett (Ruhe) dürfen sich nicht stören.",
            "abhilfe": "Raumteiler zwischen Küche und Bett; Bett nach hinten."},
    # ------------------------------------------------------------------ Küche / Bad
    "KU1": {"warum": "Der Herd steht für Nahrung und inneren Wohlstand – er braucht die Kommandoposition.",
            "abhilfe": "Wenn du beim Kochen mit dem Rücken zur Tür stehst: kleiner Spiegel an der Rückwand."},
    "KU2": {"warum": "Herd (Feuer) und Spüle/Kühlschrank (Wasser) bekämpfen sich. Holz vermittelt zwischen beiden.",
            "abhilfe": "Arbeitsfläche dazwischen oder eine Pflanze (Holz) als Vermittler."},
    "KU3": {"warum": "Ein Kochfeld unter dem Fenster lässt die Energie entweichen.", "abhilfe": "Rollo, Kräuter am Fenster."},
    "KU4": {"warum": "Spiegel verteilen das aggressive Feuer-Chi der Küche im Raum.", "abhilfe": "Spiegel abhängen."},
    "BA1": {"warum": "Das WC ist der 'Abfluss' des Hauses – es soll nicht in der Türlinie oder als Erstes sichtbar "
                     "sein, aber selbst die Tür im Blick haben (Sicherheit).",
            "abhilfe": "Tür geschlossen halten, Deckel zu, WC optisch abschirmen."},
    "BA2": {"warum": "Niemand will beim Baden das WC neben dem Gesicht haben.", "abhilfe": "Waschtisch oder Trennwand dazwischen."},
    "BA3": {"warum": "Die Wanne steht für Erholung und soll das Bad optisch verankern.", "abhilfe": "Wanne als Blickfang dekorieren."},
    "BA4": {"warum": "Mit der Tür im Rücken fühlt man sich am Waschbecken ungeschützt.", "abhilfe": "Spiegel zeigt die Tür."},
    "BA5": {"warum": "Ein Spiegel, der das WC zeigt, verdoppelt das, was man nicht sehen will.", "abhilfe": "Spiegel umhängen."},
}

# Foto-Regeln (aus dem 2D-Bild)
FOTO_ERKLAERUNG: dict[str, str] = {
    "F01": "Elektronik bringt Arbeit und Unruhe ins Schlafzimmer; schwarze Bildschirme wirken nachts wie Spiegel.",
    "F02": "Spiegel wirken wie Türen: Sie bringen Bewegung ins Schlafzimmer und spiegeln dich im Bett.",
    "F03": "Regale über dem Kopf sind wie eine Klinge – Gefahr, falls etwas fällt, und bedrückend.",
    "F04": "Schwere Bilder mit Glas über dem Bett sind gefährlich und belasten unbewusst.",
    "F05": "Schwere Leuchten/Ventilatoren über Bett oder Sitzplatz hängen wie eine Last über dir.",
    "F06": "Ein Fenster hinter dem Kopf nimmt dir den Schutz der Schildkröte im Rücken.",
    "F07": "In Linie mit der Tür strömt das Chi direkt auf dich zu (Sargposition).",
    "F08": "Pflanzen sind Yang (Leben) – im Schlafzimmer zu viel Energie; Kakteen signalisieren mit Stacheln Gefahr.",
    "F09": "Unordnung blockiert den Chi-Fluss und die Gedanken.",
    "F10": "Uhren erzeugen Zeitdruck.",
    "F11": "Wasser/Aquarien bringen zu viel Yang ins Schlafzimmer.",
    "F12": "Blick ins Fenster blendet und lenkt ab.",
    "F13": "Schlafen und Arbeiten brauchen getrennte Zonen.",
    "F14": "Zwei gleich schwere Nachttische geben Balance und Offenheit für einen Partner.",
    "F15": "Hohe offene Regale erzeugen aggressives Chi.",
    "F16": "Mehrere warme Lichtquellen wirken natürlicher als ein Deckenlicht.",
    "F17": "Viele kleine Schränke = viele spitze Ecken.",
    "F18": "Sitzkreis und Couchtisch schaffen Gemeinschaft; der TV soll nicht die Mitte sein.",
    "F19": "Gerade Anzahl gleicher Stühle = Fairness und Gemeinschaft.",
    "F20": "Offene Messer stehen für Aggression.",
    "F21": "Sichtbarer Müll stört den Eindruck von Fülle und Sauberkeit.",
    "F22": "Über dem Kamin wird der Fernseher zum Mittelpunkt des Raums.",
}

# Welche Regeln brauchen welche Objekte im Foto/Grundriss?
BRAUCHT = {
    "tuer": ["K03", "K04", "K06", "K07", "C01", "H03", "E04", "KU1", "BA1", "BA4", "ST1"],
    "fenster": ["K02", "K05", "K13", "C01", "S03"],
}


def erklaerung(rid: str) -> dict[str, str]:
    """Begründung zu einer Prüfung – eigener Text oder die verknüpfte Buchregel."""
    if rid in ERKLAERUNG:
        return ERKLAERUNG[rid]
    from .buchregeln import regeln_zu_pruefung
    br = regeln_zu_pruefung(rid)
    if br:
        return {"warum": br[0].warum, "abhilfe": br[0].abhilfe}
    from .regeln import REGELN
    r = next((r for r in REGELN if r.id == rid), None)
    return {"warum": r.beschreibung if r else "", "abhilfe": ""}
