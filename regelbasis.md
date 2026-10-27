# Feng-Shui-Regelbasis

Alle Regeln aus dem Buch, sinngemäß als **WENN → DANN**-Regeln erfasst (Quelle: `fengshui/buchregeln.py`).

**322 Buchregeln** – davon 150 im Grundriss, 9 im Foto und 60 über das Profil automatisch geprüft (219 gesamt); 103 erscheinen als Tipp im Bericht.

Prüfart: 🟢 Grundriss (automatisch) · 🔵 Foto (automatisch) · 🟣 Profil (aus deinen Angaben) · ⚪ Tipp

## Inhalt
- [1–2 Grundlagen](#12-grundlagen) (17)
- [3 Anwendung](#3-anwendung) (11)
- [4 Planung – Wohnung wählen](#4-planung--wohnung-wählen) (5)
- [4 Planung – Eingang](#4-planung--eingang) (25)
- [4 Planung – Wohnzimmer](#4-planung--wohnzimmer) (24)
- [4 Planung – Esszimmer](#4-planung--esszimmer) (23)
- [4 Planung – Küche](#4-planung--küche) (23)
- [4 Planung – Büro](#4-planung--büro) (25)
- [4 Planung – Schlafzimmer](#4-planung--schlafzimmer) (60)
- [4 Planung – Bad](#4-planung--bad) (17)
- [4 Planung – Gemeinsame Räume](#4-planung--gemeinsame-räume) (11)
- [5 Styling – Eindruck](#5-styling--eindruck) (3)
- [5 Styling – Ordnung](#5-styling--ordnung) (6)
- [5 Styling – Licht](#5-styling--licht) (13)
- [5 Styling – Farben](#5-styling--farben) (7)
- [5 Styling – Kunst und Objekte](#5-styling--kunst-und-objekte) (20)
- [5 Styling – Spiegel und Kristalle](#5-styling--spiegel-und-kristalle) (10)
- [5 Styling – Wasser](#5-styling--wasser) (5)
- [5 Styling – Pflanzen](#5-styling--pflanzen) (11)
- [5 Styling – Garten und Balkon](#5-styling--garten-und-balkon) (6)

## 1–2 Grundlagen

### GL-01 · Gefühl zuerst  (mittel, ⚪ Tipp)
- **WENN** eine Regel fühlt sich für dich falsch oder unangenehm an
- **DANN** die Regel beiseitelegen und dem eigenen Gefühl folgen
- **Warum:** Feng Shui ist gesunder Menschenverstand: Ein Raum soll sich gut anfühlen. Was sich falsch anfühlt, ist nicht im Sinne von Feng Shui.
- **Abhilfe:** Mit lernen.py deine persönlichen Gewichte trainieren.
- <sub>Räume: alle Räume</sub>

### GL-02 · Yin und Yang  (mittel, ⚪ Tipp)
- **WENN** ein Raum ist nur ruhig/dunkel (Yin) oder nur hell/energiegeladen (Yang)
- **DANN** Gegensätze ausbalancieren – nie das eine ohne das andere
- **Warum:** Alles ist Yin oder Yang; ein ausgewogener Raum braucht beides (z. B. abends weiches Licht nach dem hellen Tag).
- **Abhilfe:** Ruhige Räume mit etwas Licht/Leben ergänzen, lebhafte Räume mit ruhigen Ecken.
- <sub>Räume: alle Räume</sub>

### GL-03 · Fünf Elemente  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** Farben und Materialien zeigen nur einzelne der fünf Elemente
- **DANN** alle fünf Elemente (Feuer, Erde, Metall, Wasser, Holz) im Raum vertreten haben
- **Warum:** Die Elemente sind immer verbunden; wo eines ist, sollen auch die anderen vier sein.
- **Abhilfe:** Fehlende Elemente über Objekte ergänzen: Holz = Pflanzen, Feuer = warmes Licht/rote Akzente, Erde = Naturtöne, Metall = runde Formen/Weiß, Wasser = dunkle Blautöne/fließende Formen.
- <sub>Räume: alle Räume · Profil: `elemente_fehlen`</sub>

### GL-04 · Elementzyklen  (klein, ⚪ Tipp)
- **WENN** ein Element dominiert stark (z. B. dunkler, kalter Raum = zu viel Wasser)
- **DANN** mit den Element-Zyklen ausgleichen statt nur das Gegenteil hinzuzufügen
- **Warum:** Zu viel von einem Element bringt Ungleichgewicht; die Zyklen zeigen, was dämpft oder ableitet.
- **Abhilfe:** Zu viel Wasser: erdiger Boden, Metallkugeln, Pflanzen; zu viel Erde (Braun/Gelb): grüne Pflanzen.
- <sub>Räume: alle Räume</sub>

### GL-05 · Persönlichkeit  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Persönlichkeit ist sehr feurig bzw. das Leben eher langweilig
- **DANN** den Raum gegensätzlich ausgleichen (feurig → beruhigend, langweilig → etwas Feuer)
- **Warum:** Auch deine eigene Energie gehört zur Balance des Raums.
- <sub>Räume: alle Räume · Profil: `persoenlichkeit in ['feurig', 'gelangweilt']`</sub>

### GL-06 · Chi: Lebens-Chi  (klein, ⚪ Tipp)
- **WENN** ein Raum wirkt leblos
- **DANN** Lebens-Chi (Sheng) hineinbringen: Licht, Luft, sanfte Bewegung, Pflanzen
- **Warum:** Sheng-Chi ist Wachstum und Leben – wie ein dichter Wald.
- **Abhilfe:** Pflanzen, Mobile, frische Luft.
- <sub>Räume: alle Räume</sub>

### GL-07 · Chi: totes Chi  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** ein Raum ist stickig, staubig, unbewegt (auch wenn er hell ist)
- **DANN** Stillstand vermeiden: lüften, ausmisten, Bewegung hineinbringen
- **Warum:** Totes Chi (Si) ist stagnierende Stille, wie in einem verlassenen Haus.
- **Abhilfe:** Lüften, aufräumen, Mobile.
- <sub>Räume: alle Räume · Profil: `unordnung`</sub>

### GL-08 · Chi: tötendes Chi  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** spitze Ecken, Balken, schwere Hängeleuchten oder Schrägen zeigen auf dich
- **DANN** solche Strukturen nicht auf Bett, Sofa oder Arbeitsplatz richten
- **Warum:** Tötendes Chi (Sha) ist wie ein Messer, das auf dich zeigt: Es wirkt bedrohlich und schwer, auch wenn es dich nie berührt. Je spitzer der Winkel, desto feindseliger.
- **Abhilfe:** Runde Möbel, Ecken mit Pflanzen abmildern, Balken in Deckenfarbe streichen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K14`, `grundriss:K08`</sub>

### GL-09 · Chi: Bewegungs-Chi  (mittel, 🟢 Grundriss (automatisch))
- **WENN** lange, gerade Wege oder Flure führen durch den Raum
- **DANN** sanfte Kurven statt gerader Linien; je länger gerade, desto stärker das Chi – schlecht zum Schlafen
- **Warum:** Bewegungs-Chi fließt entlang von Wegen; gerade Bahnen machen es schnell und unruhig.
- **Abhilfe:** Möbel, Teppiche oder Pflanzen so stellen, dass der Weg leicht mäandert.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C01`, `grundriss:K15`</sub>

### GL-10 · Eine Öffnung  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** Chi soll durch dieselbe Öffnung hinein- und hinausfließen (Raum nur mit Tür, ohne Fenster)
- **DANN** ein Raum braucht eine Tür und ein Fenster auf verschiedenen Wänden
- **Warum:** Chi kann nicht durch dieselbe Öffnung herein und hinaus – sonst entsteht Stillstand.
- **Abhilfe:** Fensterlose Räume nur kurz nutzen; gut lüften, Licht an die Wände.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C08`</sub>

### GL-11 · Ein- und Ausgang  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** Eingang und Ausgang (Tür/Fenster) liegen sich genau gegenüber
- **DANN** nicht in der direkten Bahn zwischen beiden sitzen oder schlafen
- **Warum:** Liegen Ein- und Ausgang in einer Linie, schneidet das Chi schnell durch den Raum.
- **Abhilfe:** Paravent, Pflanze oder Möbel in die Bahn stellen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C01`</sub>

### GL-12 · Ein- und Ausgang nah  (klein, ⚪ Tipp)
- **WENN** Eingang und Ausgang liegen sehr nah beieinander
- **DANN** die hinteren Raumteile bewusst beleben
- **Warum:** Liegen die Öffnungen dicht beieinander, erreicht das Chi die Tiefe des Raums nicht.
- **Abhilfe:** Licht, Pflanzen oder Spiegel in den hinteren Bereich.
- <sub>Räume: alle Räume</sub>

### GL-13 · Große Räume  (klein, ⚪ Tipp)
- **WENN** ein Raum ist sehr groß
- **DANN** in Zonen gliedern; Bereiche zwischen den Öffnungen gezielt nutzen
- **Warum:** In großen Räumen erreicht das Chi nur die Flächen zwischen den Öffnungen; man fühlt sich leicht verloren.
- **Abhilfe:** Teppiche und Möbelgruppen schaffen Zonen.
- <sub>Räume: alle Räume</sub>

### GL-14 · Fünf Tiere: Schildkröte  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** hinter Bett, Sofa oder Arbeitsplatz ist offener Raum
- **DANN** eine feste Wand oder hohe Lehne in den Rücken (Schildkröte = Schutz)
- **Warum:** Die Schildkröte mit ihrem Panzer steht für Schutz und Stabilität dort, wo wir nicht hinsehen.
- **Abhilfe:** Hohes Kopfteil, Konsole hinter dem Sofa, Stuhl mit hoher Lehne.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K01`</sub>

### GL-15 · Fünf Tiere: Vogel  (mittel, 🟢 Grundriss (automatisch))
- **WENN** vor dir ist eine Wand oder es ist eng
- **DANN** Offenheit und Weitblick nach vorne (Vogel)
- **Warum:** Der Vogel braucht Raum vor sich, um vorauszuschauen und zu planen.
- **Abhilfe:** Platz vor Bett/Sofa frei lassen; vor einer Wand Bilder oder Pinnwand.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K12`</sub>

### GL-16 · Fünf Tiere: Drache und Tiger  (mittel, 🟢 Grundriss (automatisch))
- **WENN** links und rechts fehlt jede Unterstützung
- **DANN** seitlichen Halt geben (Armlehnen, Nachttische, Beistelltische)
- **Warum:** Drache und Tiger sind wie die Armlehnen eines Sessels: Schutz und Wachstum zu beiden Seiten.
- **Abhilfe:** Nachttische, Beistelltische, Sessel neben dem Sofa.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K17`</sub>

### GL-17 · Fünf Tiere: Schlange  (klein, ⚪ Tipp)
- **WENN** alle Regeln sind erfüllt, aber etwas fühlt sich falsch an
- **DANN** auf das innere Gleichgewicht hören
- **Warum:** Die Schlange in der Mitte ist dein Geisteszustand – fühlt sich etwas falsch an, ist es das wahrscheinlich.
- <sub>Räume: alle Räume</sub>

## 3 Anwendung

### AN-01 · Kommandoposition  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** der Hauptplatz im Raum (Bett, Sofa, Schreibtisch) wird gewählt
- **DANN** Wand im Rücken, offener Blick nach vorne, Tür im Blick, Halt zu den Seiten
- **Warum:** In der Kommandoposition fühlst du dich geschützt und hast den Raum unter Kontrolle – wie im bequemen Sessel mit Blick über eine Landschaft.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K01`, `grundriss:K03`, `grundriss:K12`</sub>

### AN-02 · Fenster im Rücken  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** du sitzt oder liegst mit dem Rücken an einem Fenster, besonders einem, das tiefer als die Hüfte reicht
- **DANN** Rücken an eine feste Wand, nicht ans Fenster
- **Warum:** Ein Fenster im Rücken macht verletzlich: Man kann dich von hinten sehen.
- **Abhilfe:** Brüstung höher als Lehne/Kopfteil, schwere Vorhänge, massives Kopfteil.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K02`</sub>

### AN-03 · Rücken zur Tür  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** du sitzt oder liegst mit dem Rücken zur Tür
- **DANN** so platzieren, dass die Tür ohne Umdrehen sichtbar ist
- **Warum:** Mit der Tür im Rücken fühlt man sich unsicher – jemand könnte unbemerkt hereinkommen.
- **Abhilfe:** Spiegel, in dem du die Tür siehst (nicht im Schlafzimmer), Tür schließen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K03`</sub>

### AN-04 · Café-Technik  (mittel, 🟢 Grundriss (automatisch))
- **WENN** du suchst den besten Platz in einem Raum
- **DANN** nicht direkt an der Tür (Durchgang), nicht am WC, Licht vom Fenster, aber Rücken an der Wand und Blick in den Raum
- **Warum:** So wählt man instinktiv im Café: wenig Durchgang, gutes Licht, geschützter Rücken, Überblick.
- <sub>Räume: alle Räume · Prüfung: `grundriss:K06`, `grundriss:K01`, `grundriss:K03`</sub>

### AN-05 · Kronleuchter-Effekt  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** über deinem Platz hängt etwas Schweres (Lampe, Balken, Ventilator)
- **DANN** den Platz wechseln oder das Schwere entfernen
- **Warum:** Man weiß, dass es nicht fällt, fühlt sich darunter aber trotzdem bedroht.
- <sub>Räume: alle Räume · Prüfung: `grundriss:L01`, `grundriss:K08`, `foto:F05`</sub>

### AN-06 · Grundriss-Übung  (mittel, 🟢 Grundriss (automatisch))
- **WENN** du suchst die beste Chi-Position im Raum
- **DANN** Laufwege, Linien von spitzen Ecken und Lichteinfall einzeichnen; der beste Platz liegt ohne Lauf- und Eckenlinien, aber im Licht
- **Warum:** So findet man systematisch Ruhe, Schutz und Licht.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C01`, `grundriss:K14`</sub>

### AN-07 · Nordseite  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** das Hauptfenster zeigt nach Norden (Nordhalbkugel)
- **DANN** neutrale bis warme Wandfarben, keine Vorhänge vor dem Licht, abends eher kräftiges Licht; gut für Büro/Atelier
- **Warum:** Nordlicht ist indirekt, gleichmäßig, kühl-bläulich (Wasser, Winter).
- <sub>Räume: alle Räume · Profil: `hauptrichtung == N`</sub>

### AN-08 · Südseite  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** das Hauptfenster zeigt nach Süden
- **DANN** lebendige Farben; abends weiches, stimmungsvolles Licht; gut für Wohnzimmer und Eingang; robuste Pflanzen mildern starkes Chi
- **Warum:** Südlicht ist stark und roh (Feuer, Sommer).
- <sub>Räume: alle Räume · Profil: `hauptrichtung == S`</sub>

### AN-09 · Ostseite  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** das Hauptfenster zeigt nach Osten
- **DANN** wärmere Wandfarben, abends etwas kräftigeres Licht; gut für Kinderzimmer und Wintergarten; Holz-Elemente (nicht im Erwachsenen-Schlafzimmer)
- **Warum:** Ostlicht ist belebendes Morgenlicht (Holz, Frühling, Wachstum).
- <sub>Räume: alle Räume · Profil: `hauptrichtung == O`</sub>

### AN-10 · Westseite  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** das Hauptfenster zeigt nach Westen
- **DANN** kühlere Wandfarben, weiches Licht nach Sonnenuntergang; gut für Erwachsenen-Schlafzimmer
- **Warum:** Westlicht ist die orange-feurige Abendsonne (Metall, Herbst).
- <sub>Räume: alle Räume · Profil: `hauptrichtung == W`</sub>

### AN-11 · Südhalbkugel  (klein, ⚪ Tipp)
- **WENN** du wohnst auf der Südhalbkugel
- **DANN** Nord und Süd in allen Regeln tauschen
- **Warum:** Dort steht die Sonne im Norden.
- **Abhilfe:** Raum(suedhalbkugel=True)
- <sub>Räume: alle Räume</sub>

## 4 Planung – Wohnung wählen

### WO-01 · Bausubstanz  (mittel, ⚪ Tipp)
- **WENN** eine Wohnung wird ausgesucht
- **DANN** auf Dichtheit und Bausubstanz achten (vor allem Wasserschäden)
- **Warum:** Die Grundaufgabe eines Hauses ist Schutz vor Regen und Wasser.
- <sub>Räume: wohnung</sub>

### WO-02 · Umgebung  (klein, ⚪ Tipp)
- **WENN** eine Wohnung wird ausgesucht
- **DANN** Parks, Grün, saubere Luft in der Nähe; stark befahrene Straßen meiden
- **Warum:** Eine laute Straße ist kein Fluss, sondern gewaltsame Energie.
- <sub>Räume: wohnung</sub>

### WO-03 · Bedürfnisse  (klein, ⚪ Tipp)
- **WENN** eine Wohnung wird ausgesucht
- **DANN** nach heutigen Bedürfnissen wählen, nicht nach einem Merkmal für in zehn Jahren
- **Warum:** Kopf und Herz entscheiden gemeinsam.
- <sub>Räume: wohnung</sub>

### WO-04 · Haus in Kommandoposition  (klein, ⚪ Tipp)
- **WENN** eine Wohnung wird ausgesucht
- **DANN** etwas Stabiles im Rücken (Hügel, höheres Gebäude), offener Blick nach vorne, idealerweise auf Wasser
- **Warum:** Wie die Hauptstadt des Kaisers: Schutz hinten, Weite vorn.
- <sub>Räume: wohnung</sub>

### WO-05 · Gesicht der Wohnung  (klein, ⚪ Tipp)
- **WENN** die Ausrichtung der Wohnung wird bestimmt
- **DANN** Haus: Haustür ist das Gesicht; Wohnung/Zimmer: größtes Fenster oder Zimmertür – je nachdem, woher die meiste Energie kommt
- **Warum:** Danach richten sich die Himmelsrichtungs-Empfehlungen.
- **Abhilfe:** nord_wand im Raum angeben.
- <sub>Räume: wohnung</sub>

## 4 Planung – Eingang

### EI-01 · Haupttür  (mittel, ⚪ Tipp)
- **WENN** es gibt mehrere Türen
- **DANN** die meistbenutzte Tür als Haupttür behandeln und besonders pflegen
- **Warum:** Die Haupttür ist der Mund des Hauses: Alles kommt durch sie herein.
- <sub>Räume: flur, wohnzimmer, studio, kueche, esszimmer</sub>

### EI-02 · Eingang feiern  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** der Eingang ist dunkel oder lieblos
- **DANN** viel Licht und Energie am Eingang; etwas Platz zum Ankommen
- **Warum:** Man hat nur eine Chance für den ersten Eindruck – auch für sich selbst.
- **Abhilfe:** Helle Leuchte, Pflanze, schönes Objekt.
- <sub>Räume: flur, wohnzimmer, studio, kueche, esszimmer · Profil: `eingang_dunkel`</sub>

### EI-03 · Zugang nicht aggressiv  (mittel, ⚪ Tipp)
- **WENN** ein langer, gerader Weg oder Flur führt direkt auf die Tür zu
- **DANN** den Weg mäandern lassen oder das Chi innen dämpfen
- **Warum:** Wie eine Klinge: Je länger die gerade Strecke, desto stärker das heranrauschende Chi.
- **Abhilfe:** Pflanzen am Weg; innen Paravent oder Pendelleuchte als Chi-Bremse.
- <sub>Räume: flur, wohnzimmer, studio, kueche, esszimmer</sub>

### EI-04 · Tür führt in öffentlichen Bereich  (mittel, ⚪ Tipp)
- **WENN** die Haustür führt zuerst an privaten Räumen (Schlafzimmer) vorbei
- **DANN** den Blick zu den öffentlichen Räumen lenken; private Türen schließen und tarnen
- **Warum:** Der Eingang soll in den gemeinschaftlichen Teil führen, nicht in den privaten.
- **Abhilfe:** Schlafzimmertüren geschlossen halten, in Wandfarbe streichen, Blickfang am Flurende.
- <sub>Räume: flur, wohnzimmer, studio, kueche, esszimmer</sub>

### EI-05 · Gegenüberliegende Wohnungstüren  (klein, ⚪ Tipp)
- **WENN** zwei Wohnungstüren liegen sich direkt gegenüber
- **DANN** den Bereich als gemeinsamen Raum mit dem Nachbarn gestalten
- **Warum:** Gegenüberliegende Türen wirken konfrontativ.
- **Abhilfe:** Gemeinsam Pflanzen aufstellen.
- <sub>Räume: flur</sub>

### EI-06 · Türfarbe  (klein, ⚪ Tipp)
- **WENN** die Haustür wird gestrichen
- **DANN** nach Norden/dunkel: schwarz oder Wassertöne; nach Süden/sonnig: Rot
- **Warum:** Die Farbe gleicht die Umgebung aus und kündigt das Innere an.
- <sub>Räume: flur</sub>

### EI-07 · Fußmatte  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Fußmatte zeigt ein Logo oder Symbol, das du respektierst
- **DANN** keine verehrten Symbole auf der Matte
- **Warum:** Man tritt jeden Tag darauf.
- <sub>Räume: flur · Profil: `fussmatte_symbol`</sub>

### EI-08 · Tür öffnet nach innen  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Tür öffnet nach außen
- **DANN** Türen nach innen öffnen lassen
- **Warum:** Eine nach innen öffnende Tür lädt das Chi herein.
- <sub>Räume: alle Räume · Profil: `tuer_oeffnet_aussen`</sub>

### EI-09 · Türgröße  (klein, ⚪ Tipp)
- **WENN** die Haupttür ist zu klein oder zu groß
- **DANN** proportional zum Haus, aber auffälliger als alle anderen Türen
- **Warum:** Zu klein: wenig Glück kommt herein; zu groß: kann das Glück nicht halten.
- **Abhilfe:** Seiteneingang mit Pflanzen und Weg betonen.
- <sub>Räume: flur</sub>

### EI-10 · Türmaterial  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Haupttür hat Glas oder ist eine Fenstertür
- **DANN** massive Holztür; Fenstertüren zählen als Fenster, nicht als Tür
- **Warum:** Glas steht für Zerbrechlichkeit, die Tür soll Sicherheit ausstrahlen.
- <sub>Räume: flur · Profil: `haustuer_glas`</sub>

### EI-11 · Flur wie ein Zimmer  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** der Eingangsbereich ist eine Abstellfläche
- **DANN** den Flur wie ein vollwertiges Zimmer behandeln; alles hat seinen Platz
- **Warum:** Der Eingang setzt den Ton für die ganze Wohnung.
- **Abhilfe:** Schuhschrank, Garderobe, Ordnung.
- <sub>Räume: flur · Profil: `schuhe_herum`</sub>

### EI-12 · Chi-Bremse im Flur  (mittel, ⚪ Tipp)
- **WENN** die Haustür liegt am Ende eines langen Gangs mit viel Chi
- **DANN** Chi-Bremsen innen: Paravent oder Pendelleuchte; aber nicht komplett abblocken
- **Warum:** Das heranrauschende Chi soll gedämpft, nicht abgewiesen werden.
- <sub>Räume: flur</sub>

### EI-13 · Kein Spiegel gegenüber der Tür  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel hängt der Eingangstür direkt gegenüber
- **DANN** Spiegel an eine Seitenwand, nie gegenüber der Tür
- **Warum:** Ein Spiegel gegenüber der Tür lenkt das ankommende Chi gleich wieder hinaus.
- **Abhilfe:** Spiegel umhängen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C02`</sub>

### EI-14 · Heller Flur  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** der Eingang ist dunkel
- **DANN** den Eingangsbereich immer hell halten
- **Warum:** Heimkommen soll sich wie ein kleines Fest anfühlen.
- <sub>Räume: flur · Profil: `eingang_dunkel`</sub>

### EI-15 · Pflanzen im Eingang  (klein, ⚪ Tipp)
- **WENN** der Eingang hat Tageslicht
- **DANN** breitblättrige Pflanzen in den Eingang (nur wenn sie dort überleben)
- **Warum:** Pflanzen zeigen, dass das Zuhause auf fruchtbarem Boden steht.
- <sub>Räume: flur</sub>

### EI-16 · Religiöse Objekte im Eingang  (klein, ⚪ Tipp)
- **WENN** du hast religiöse Objekte oder einen Altar
- **DANN** sie können in den Eingang, um dich beim Heimkommen zu erinnern
- **Warum:** Beim Heimkommen begegnest du deinen Leitbildern.
- <sub>Räume: flur</sub>

### EI-17 · Eingang frei  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** Möbel stehen im Eingang im Weg
- **DANN** den Eingang offen und frei halten
- **Warum:** Ein ungehinderter Eintritt lässt das Chi sanft hereinfließen.
- <sub>Räume: flur · Prüfung: `grundriss:H03`, `grundriss:H04`</sub>

### EI-18 · Keine Kanten im Eingang  (mittel, 🟢 Grundriss (automatisch))
- **WENN** über oder neben dem Eingang sind spitze Ecken, Balken oder offene Regale
- **DANN** vermeiden; sonst in Wandfarbe streichen oder mit Pflanzen/Licht abmildern
- **Warum:** Kanten am Eingang begrüßen dich mit Sha-Chi.
- <sub>Räume: flur · Prüfung: `grundriss:K14`</sub>

### EI-19 · Tür direkt in den Wohnraum  (mittel, ⚪ Tipp)
- **WENN** die Tür führt direkt ohne Flur in den Wohnraum
- **DANN** Paravent oder Tisch mit Blumen als Puffer; Möbel so stellen, dass ein kleiner Eingangsbereich entsteht
- **Warum:** Ein Eingangsbereich ist wichtig, um beim Heimkommen anzukommen.
- <sub>Räume: wohnzimmer, studio</sub>

### EI-20 · Kein Putzzeug im Eingang  (mittel, 🔵 Foto (automatisch))
- **WENN** Besen, Mopp oder Mülleimer stehen im Eingang
- **DANN** versteckt oder diskret aufbewahren
- **Warum:** Der erste Eindruck soll nicht von Putzzeug und Müll geprägt sein.
- <sub>Räume: flur · Prüfung: `foto:F21` · Profil: `besen_muell_im_eingang`</sub>

### EI-21 · Schmaler Flur  (mittel, ⚪ Tipp)
- **WENN** der Eingang ist ein langer, schmaler, dunkler Gang
- **DANN** Spiegel an die SEITENWAND (nie ans Ende), helle Kunst an beide Seiten, schöne Pendelleuchte, Blickfang am Ende
- **Warum:** Spiegel am Ende werfen das Chi hinaus; Kunst an den Seiten bremst den Durchzug.
- <sub>Räume: flur</sub>

### EI-22 · Tür in die Küche  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Tür führt direkt in die Küche
- **DANN** Küche immer aufgeräumt, Kühlschrank verstecken, Herd/Kochfeld von der Tür aus nicht sichtbar
- **Warum:** Der erste Blick soll nicht auf Funktionsgeräte und das Feuer fallen.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU1`</sub>

### EI-23 · Tür ins Esszimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Tür führt direkt ins Esszimmer
- **DANN** freien Weg lassen; Esstisch nicht in den Eingang; kein Stuhl mit dem Rücken zur Tür
- **Warum:** Ein blockierter Eingang und ein ungeschützter Sitz direkt an der Tür sind unangenehm.
- <sub>Räume: esszimmer · Prüfung: `grundriss:E04`</sub>

### EI-24 · Treppe gegenüber der Tür  (mittel, ⚪ Tipp)
- **WENN** eine Treppe liegt direkt gegenüber der Haustür
- **DANN** Paravent davor, letzte Stufen drehen oder Statement-Leuchte, um den Blick nach oben zu lenken
- **Warum:** Treppen verstärken das Chi: hinauf zu viel, hinunter fließt es ab.
- **Abhilfe:** Windspiel oder Kristall.
- <sub>Räume: flur</sub>

### EI-25 · Erster Blick von der Haustür  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** von der Haustür sieht man WC, Bett oder Herd
- **DANN** diese von der Haustür aus verbergen; stattdessen einen einladenden Blickfang (z. B. Sofa, Kunst)
- **Warum:** Das Erste, was man sieht, setzt den Ton für das ganze Zuhause.
- <sub>Räume: flur, studio · Prüfung: `grundriss:BA1`, `grundriss:KU1`</sub>

## 4 Planung – Wohnzimmer

### WZ-01 · Lage  (klein, ⚪ Tipp)
- **WENN** die Wohnung wird geplant
- **DANN** Wohnzimmer in die Mitte, von den anderen Räumen sichtbar
- **Warum:** Das Wohnzimmer ist der Anker, wo die Familie zusammenkommt.
- <sub>Räume: wohnung</sub>

### WZ-02 · Sitze schauen sich an  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** alle Sitze zeigen in dieselbe Richtung (z. B. zum Fernseher)
- **DANN** Sofa und Sessel einander zuwenden – ein geschlossener Sitzkreis
- **Warum:** Zugewandte Sitze laden zum Gespräch ein; der Raum zeigt, dass Menschen wichtiger sind als der TV.
- **Abhilfe:** Sessel drehen, Couchtisch als Mitte.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:S06`, `foto:F18`</sub>

### WZ-03 · Genug Sitzplätze  (klein, ⚪ Tipp)
- **WENN** es gibt weniger Sitzplätze als Bewohner/Gäste
- **DANN** genug Plätze für alle Bewohner und Gäste
- **Warum:** Im Wohnzimmer ist jeder willkommen.
- <sub>Räume: wohnzimmer, studio</sub>

### WZ-04 · Lebendige Deko  (klein, 🔵 Foto (automatisch))
- **WENN** das Wohnzimmer wirkt leblos
- **DANN** Pflanzen, Spiegel, evtl. Aquarium – das Wohnzimmer verträgt viel Energie
- **Warum:** Es ist der Raum mit dem meisten Leben und positivem Chi.
- <sub>Räume: wohnzimmer, studio · Prüfung: `foto:F08`</sub>

### WZ-05 · Spiegel im Wohnzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel spiegelt Türen oder den Fernseher
- **DANN** Spiegel so hängen, dass sie Schönes zeigen – nicht Türen oder TV; am besten dort, wo man sich ein Fenster wünscht
- **Warum:** Spiegel verdoppeln, was sie zeigen; Türen im Spiegel lassen Chi hinausfließen.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:C09`</sub>

### WZ-06 · Sofa in Kommandoposition  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Hauptsofa wird platziert
- **DANN** Wand hinter dem Sofa, Platz davor, Blick auf den Eingang; nicht in Linie mit einem Flur, keine Balken darüber
- **Warum:** Das Sofa ist der Hauptplatz des Wohnzimmers.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:K01`, `grundriss:K03`, `grundriss:C01`, `grundriss:K08`</sub>

### WZ-07 · Ein Hauptsofa  (klein, ⚪ Tipp)
- **WENN** es gibt mehrere gleichwertige Sofas
- **DANN** ein Hauptsofa, ergänzt durch Sessel
- **Warum:** Klare Hierarchie bringt Ruhe.
- <sub>Räume: wohnzimmer, studio</sub>

### WZ-08 · Zwei Sofas gegenüber  (mittel, 🟢 Grundriss (automatisch))
- **WENN** zwei Sofas stehen sich über eine leere Fläche gegenüber
- **DANN** einen Couchtisch dazwischenstellen
- **Warum:** Zwei Sofas gegenüber wirken konfrontativ und formell; der Tisch entschärft die Spannung.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:W01`</sub>

### WZ-09 · L-Sofa  (klein, ⚪ Tipp)
- **WENN** ein L-förmiges Sofa steht allein
- **DANN** ein oder zwei Sessel diagonal zur Ecke stellen
- **Warum:** Ein L-Sofa bildet nur einen halben Sitzkreis.
- <sub>Räume: wohnzimmer, studio</sub>

### WZ-10 · Freistehendes Sofa  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Sofa kann nicht an eine Wand
- **DANN** niedrige Konsole dahinter oder ein Sofa mit hoher, kräftiger Lehne
- **Warum:** Auch ohne Wand braucht der Rücken Schutz (Schildkröte).
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:K01`</sub>

### WZ-11 · Dachschräge über dem Sofa  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Sofa steht unter dem niedrigen Ende einer Schräge
- **DANN** nicht unter das niedrige Ende; wenn doch, Lampen links und rechts, um die Decke optisch zu heben
- **Warum:** Die niedrige Decke drückt optisch auf den Kopf.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:K09`</sub>

### WZ-12 · Sofa nicht allein  (klein, 🟢 Grundriss (automatisch))
- **WENN** das Sofa steht ohne weitere Sitzmöbel
- **DANN** mit Sessel, Bank oder Hocker ergänzen
- **Warum:** Erst mehrere Sitzplätze bilden eine Gemeinschaft.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:W03`, `foto:F18`</sub>

### WZ-13 · Sessel  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Sessel wird platziert
- **DANN** Sessel ergänzt den Sitzkreis und schaut zum Sofa; ist der Sessel dein Hauptplatz, bekommt er die Kommandoposition
- **Warum:** Nicht alle Sitze sollen in dieselbe Richtung schauen.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:S06`</sub>

### WZ-14 · Couchtisch als Anker  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Wohnzimmer hat keinen Couchtisch
- **DANN** einen schönen Couchtisch in die Mitte – mit etwas Lebendigem darauf (Blumen, Obst)
- **Warum:** Ohne Couchtisch schwebt der Raum um eine Leere; der Tisch verbindet die Sitze und steht für Fülle.
- **Abhilfe:** Mindestens ein Beistelltisch.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:W02`, `foto:F18`</sub>

### WZ-15 · Beistelltische  (klein, ⚪ Tipp)
- **WENN** das Sofa wirkt klein
- **DANN** Beistelltische lassen es breiter und großzügiger wirken
- **Warum:** Sie erweitern die Fläche des Sofas.
- <sub>Räume: wohnzimmer, studio</sub>

### WZ-16 · Fernseher dezent  (mittel, 🟢 Grundriss (automatisch))
- **WENN** der Fernseher steht im Mittelpunkt oder hängt hoch an der Wand
- **DANN** TV in eine weniger wichtige Ecke, so tief wie möglich; auf ein großes Möbel mit Lampe als Gegengewicht
- **Warum:** Gemeinschaft hat Vorrang vor dem Fernseher.
- **Abhilfe:** TV auf Beinen in eine Ecke stellen.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:S05`, `grundriss:S07`, `foto:F18` · Profil: `fernseher_hoch_aufgehaengt`</sub>

### WZ-17 · Kein TV über dem Kamin  (mittel, 🟢 Grundriss (automatisch))
- **WENN** der Fernseher hängt über dem Kamin
- **DANN** nie über den Kamin
- **Warum:** Dort bekommt er zu viel Bedeutung.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:S09`, `foto:F22` · Profil: `fernseher_ueber_kamin`</sub>

### WZ-18 · Sideboards  (klein, ⚪ Tipp)
- **WENN** Stauraum wird gebraucht
- **DANN** Sideboards mit Lampe/hoher Deko darauf; gute Basis für Bilder darüber
- **Warum:** Sie machen den Raum wohnlich und strukturieren die Wand.
- <sub>Räume: wohnzimmer, studio</sub>

### WZ-19 · Viele Lichtquellen  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Wohnzimmer hat nur ein Deckenlicht
- **DANN** Tiefe durch viele verschiedene Lichtquellen
- **Warum:** Verschiedene Lichter schaffen Atmosphäre.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:L03` · Profil: `anzahl_lichtquellen < 3`</sub>

### WZ-20 · Kronleuchter über dem Couchtisch  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** ein Kronleuchter hängt über dem Sofa oder Sitzplätzen
- **DANN** nie über Sitzplätze; über den Couchtisch
- **Warum:** Über den Köpfen wirkt er bedrohlich.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:L01`, `grundriss:L02`</sub>

### WZ-21 · Kleines Wohnzimmer  (klein, ⚪ Tipp)
- **WENN** das Wohnzimmer ist klein
- **DANN** weniger, dafür größere Stücke; Größe über Licht/Kunst/bodenlange Vorhänge; großzügige Wege; großer Teppich (unter mindestens der Hälfte der Möbel)
- **Warum:** Klein ist gemütlich – nicht zu viel hineinzwängen.
- <sub>Räume: wohnzimmer, studio</sub>

### WZ-22 · Langes Wohnzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Wohnzimmer ist lang und schmal
- **DANN** Möbel quer stellen, große Kunst an die Längswände, Spiegel nicht ans Ende, Statement-Stück ans Ende, Meistgenutztes nach vorne
- **Warum:** Im langen Raum fließt das Chi zu schnell.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:K15`</sub>

### WZ-23 · Unregelmäßiges Wohnzimmer  (klein, ⚪ Tipp)
- **WENN** das Wohnzimmer ist L-förmig oder hat Nischen
- **DANN** Ecken weich machen statt verschließen; Nischen als Leseecke nutzen; keine Sitzplätze in abgetrennten Nischen
- **Warum:** Wer in einer abgetrennten Nische sitzt, fühlt sich ausgeschlossen.
- **Abhilfe:** Spiegel erweitern den Raum.
- <sub>Räume: wohnzimmer, studio</sub>

### WZ-24 · Viele Türen und Fenster  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Wohnzimmer hat viele Türen und Fenster
- **DANN** starker Mittelpunkt (großer Couchtisch); Sofa nur vor Fenster, deren Brüstung höher als die Lehne ist; Durchgänge um die Sitzgruppe herum, nicht hindurch
- **Warum:** So bleibt die Sitzgruppe ein ruhiger Anker.
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:K02`, `grundriss:C01`</sub>

## 4 Planung – Esszimmer

### EZ-01 · Lage  (klein, ⚪ Tipp)
- **WENN** die Wohnung wird geplant
- **DANN** Esszimmer zentral, nicht direkt am Eingang, neben der Küche, unter den Schlafzimmern (nicht im Keller)
- **Warum:** Es ist das Herz des Zuhauses und bringt Familie und Freunde zusammen.
- <sub>Räume: wohnung</sub>

### EZ-02 · Küche vor Fenstern  (klein, ⚪ Tipp)
- **WENN** du musst wählen: Esszimmer neben der Küche oder mit vielen Fenstern
- **DANN** die Nähe zur Küche hat Vorrang
- **Warum:** Der Weg zwischen Küche und Tisch ist der meistbenutzte.
- <sub>Räume: wohnung</sub>

### EZ-03 · Tisch in der Mitte  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** der Esstisch steht an der Wand oder in einer Ecke
- **DANN** Tisch mittig, als Mittelpunkt; rundum Platz zum Bewegen
- **Warum:** Niemand soll eingeklemmt sitzen oder zur Wand schauen.
- **Abhilfe:** Wenn Wand unvermeidlich: Spiegel dort.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Prüfung: `grundriss:S04`</sub>

### EZ-04 · Erde-Element  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Farben im Esszimmer sind kräftig
- **DANN** erdige, neutrale Töne – gedämpfter als im Rest der Wohnung
- **Warum:** Das Esszimmer ist die ausgleichende Mitte (Erde).
- <sub>Räume: esszimmer · Profil: `wandfarbe_element in ['feuer', 'wasser']`</sub>

### EZ-05 · Pendelleuchte über dem Tisch  (mittel, 🟢 Grundriss (automatisch))
- **WENN** es fehlt Licht über dem Tisch
- **DANN** schöne Pendelleuchte oder Kronleuchter mittig über dem Tisch (der einzige Ort, der wirklich eine braucht)
- **Warum:** Das Licht zieht die Menschen an den Tisch.
- <sub>Räume: esszimmer, kueche, studio · Prüfung: `grundriss:L02`</sub>

### EZ-06 · Spiegel im Esszimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel hängt im Esszimmer
- **DANN** er soll den Tisch spiegeln, nicht die Tür; ganze, unverzerrte Spiegel
- **Warum:** Ein Spiegel verdoppelt Essen und schöne Momente.
- <sub>Räume: esszimmer · Prüfung: `grundriss:E05`, `grundriss:C09`</sub>

### EZ-07 · Fröhliche Kunst  (klein, ⚪ Tipp)
- **WENN** Kunst wird ausgesucht
- **DANN** fröhliche, lebendige Bilder – gern auch appetitliche Motive
- **Warum:** Das Esszimmer will Freude und Energie.
- <sub>Räume: esszimmer</sub>

### EZ-08 · Fülle zeigen  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** der Tisch und die Sideboards sind leer
- **DANN** immer etwas darauf: Obst oder Blumen; Pflanzen, wenn genug Licht
- **Warum:** Ein gedeckter, voller Tisch steht für Überfluss.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Profil: `esstisch_leer`</sub>

### EZ-09 · Keine Uhr  (mittel, 🟢 Grundriss (automatisch))
- **WENN** eine Uhr hängt im Esszimmer
- **DANN** keine Uhren im Esszimmer
- **Warum:** Uhren erzeugen Eile, wo Gemeinschaft zählen soll.
- <sub>Räume: esszimmer · Prüfung: `grundriss:E06`, `foto:F10` · Profil: `uhr_im_raum`</sub>

### EZ-10 · Tisch nicht im Weg  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** der Tisch steht im Eingang oder in einer Linie mit der Tür
- **DANN** Blick zum Eingang, aber nicht im Weg; steht er in Linie mit der Haupttür, Konsole als Schutz
- **Warum:** Direkt am Eingang ist zu viel Bewegung.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Prüfung: `grundriss:E04`</sub>

### EZ-11 · Beste Plätze  (klein, ⚪ Tipp)
- **WENN** Gäste werden platziert
- **DANN** die besten Plätze den wichtigsten Gästen; der schlechteste ist der nahe dem Eingang mit dem Rücken zur Tür
- **Warum:** Jeder soll möglichst in seiner eigenen Kommandoposition sitzen.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche</sub>

### EZ-12 · Tischform  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Esstisch wird gewählt
- **DANN** rund ist am besten, dann oval, quadratisch (Erde), rechteckig mit Blick auf die Kopfenden; keine unregelmäßigen oder zusammengeschobenen Tische
- **Warum:** Runde Tische haben keine Ecken und keine Rangordnung.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Prüfung: `grundriss:E01` · Profil: `esstisch_form in ['unregelmaessig', 'zusammengeschoben']`</sub>

### EZ-13 · Tischgröße  (klein, ⚪ Tipp)
- **WENN** der Tisch ist viel größer als nötig
- **DANN** Größe passend zum eigenen Gästeaufkommen
- **Warum:** Ein ständig leerer, zu großer Tisch schafft Ungleichgewicht.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche</sub>

### EZ-14 · Tischmaterial  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** der Esstisch ist aus Glas
- **DANN** Holz, Stein oder Ton/Terrakotta; Glas vermeiden
- **Warum:** Glas macht unruhig – man sieht die Beine der anderen beim Essen.
- **Abhilfe:** Beim Essen eine Tischdecke auflegen.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Profil: `esstisch_material == glas`</sub>

### EZ-15 · Gleiche Stühle  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Stühle sind verschieden
- **DANN** alle Stühle gleich, stabil und solide
- **Warum:** Gleiche Stühle vermeiden jede Rangordnung.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Prüfung: `grundriss:E02` · Profil: `stuehle == verschieden`</sub>

### EZ-16 · Gerade Stuhlzahl  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Stuhlzahl ist ungerade oder Stühle stehen an den Ecken
- **DANN** gerade Anzahl, keiner an den Tischecken
- **Warum:** Gerade Zahl und gleiche Abstände = Fairness und Gemeinschaft.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Prüfung: `grundriss:E02`, `foto:F19`</sub>

### EZ-17 · Keine Plastikstühle  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** es sind provisorische Plastikstühle
- **DANN** solide Stühle; wenn nicht anders möglich, wenigstens bequem und stabil
- **Warum:** Plastikstühle wirken wie Kantine oder Hostel.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Profil: `stuehle == plastik`</sub>

### EZ-18 · Ersatzstühle weg  (klein, 🟢 Grundriss (automatisch))
- **WENN** Ersatzstühle stehen am Rand
- **DANN** Ersatzstühle aus dem Raum nehmen
- **Warum:** Einzelne Stühle am Rand stehen für unwillkommene Gäste.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Prüfung: `grundriss:E02`</sub>

### EZ-19 · Konsolen an die Wand  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Konsolen oder Sideboards stehen frei im Raum
- **DANN** an die Wand; nur Tisch und Stühle in die Mitte; nichts überragt den Tisch bedrohlich
- **Warum:** Die Mitte gehört dem Tisch.
- <sub>Räume: esszimmer · Prüfung: `grundriss:E03`</sub>

### EZ-20 · Kleines Esszimmer  (klein, ⚪ Tipp)
- **WENN** das Esszimmer ist klein
- **DANN** kleinerer Tisch, großzügige Stühle mit Armlehnen (oder niedrige Lehnen bei mehr Gästen), große Pendelleuchte bei hoher Decke, Spiegel, große Kunst
- **Warum:** Nicht alles klein machen – Größe über Wand und Licht.
- <sub>Räume: esszimmer</sub>

### EZ-21 · Langes Esszimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Esszimmer ist lang
- **DANN** ovaler statt langer rechteckiger Tisch, Stühle mit Armlehnen, keine langen Bänke, Spiegel an die Längswände (nicht ans Ende)
- **Warum:** Ovale Tische bremsen das schnelle Chi im langen Raum.
- <sub>Räume: esszimmer · Prüfung: `grundriss:E07`</sub>

### EZ-22 · Kein fensterloser Essraum  (mittel, 🟢 Grundriss (automatisch))
- **WENN** der Essbereich hat kein Fenster oder liegt im Durchgang/Flur
- **DANN** Räume ohne Fenster meiden; im Flur Konsolen zur Verankerung, großzügige Wege
- **Warum:** Das Esszimmer braucht Licht und Luft.
- <sub>Räume: esszimmer · Prüfung: `grundriss:C08`</sub>

### EZ-23 · Tisch außermittig  (klein, 🟢 Grundriss (automatisch))
- **WENN** der Tisch muss außermittig stehen (für einen breiteren Weg)
- **DANN** Pendelleuchte mittig über den Tisch hängen, um den Fokus zu setzen
- **Warum:** Die Leuchte macht den Tisch trotzdem zum Zentrum.
- <sub>Räume: esszimmer, wohnzimmer, studio, kueche · Prüfung: `grundriss:L02`</sub>

## 4 Planung – Küche

### KU-01 · Eigener Platz  (klein, ⚪ Tipp)
- **WENN** die Wohnung wird geplant
- **DANN** Küche mit eigenem Platz, nicht im Durchgang; nicht in der Mitte; in der hinteren Hälfte
- **Warum:** Die Küche steht für Nahrung und inneren Wohlstand, hat aber zu viel Feuer für die Mitte.
- <sub>Räume: wohnung</sub>

### KU-02 · Herd nicht von der Haustür sichtbar  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** man sieht von der Tür aus den Herd
- **DANN** Herd von der Eingangstür aus nicht sichtbar
- **Warum:** Das Feuer verbrennt das gute Chi, das hereinkommt.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU1`</sub>

### KU-03 · WC nicht zur Küche  (klein, ⚪ Tipp)
- **WENN** ein WC liegt der Küche gegenüber
- **DANN** Tür geschlossen halten
- **Warum:** Wasser (WC) und Feuer (Küche) stören sich.
- <sub>Räume: wohnung</sub>

### KU-04 · Küche weg vom Schlafzimmer  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Schlafzimmer liegt neben oder über der Küche bzw. das Bett nahe am Herd (Studio)
- **DANN** Küche und Schlafbereich trennen; im Studio das Bett weit weg vom Herd
- **Warum:** Die Hitze des Feuers stört die Ruhe.
- **Abhilfe:** Raumteiler zwischen Küche und Bett.
- <sub>Räume: wohnung, studio · Prüfung: `grundriss:ST1`</sub>

### KU-05 · Wohnküche  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Küche ist auch Essplatz
- **DANN** mehr gestalten, aber weiterhin keine Spiegel oder Wasser-Elemente
- **Warum:** Die Küche bleibt vom Feuer geprägt.
- <sub>Räume: kueche · Prüfung: `grundriss:KU4`</sub>

### KU-06 · Lüftung  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Küche hat kein Fenster
- **DANN** natürliche Belüftung, Fenster in der Nähe
- **Warum:** Die Küche ist Yang und braucht Licht und Luft.
- **Abhilfe:** Mehr Seitenlicht, offener gestalten.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:C08`</sub>

### KU-07 · Herd als Mittelpunkt  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** Herd und Spüle werden geplant
- **DANN** der Herd ist das zentrale Element, die Spüle zweitrangig; nicht direkt nebeneinander
- **Warum:** Feuer und Wasser kämpfen gegeneinander.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU2`</sub>

### KU-08 · Feuer und Wasser trennen  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** Herd steht neben oder gegenüber von Spüle, Kühlschrank oder Spülmaschine
- **DANN** Abstand halten oder Holz (Pflanzen) dazwischen
- **Warum:** Holz vermittelt zwischen Feuer und Wasser.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU2`</sub>

### KU-09 · Ordnung  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** schmutziges Geschirr steht herum
- **DANN** Küche immer aufgeräumt, Geschirr nie stehen lassen
- **Warum:** Besonders wenn man sie vom Eingang sieht, prägt sie die Stimmung.
- <sub>Räume: kueche, studio · Profil: `unordnung`</sub>

### KU-10 · Kein Wasser-Element  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Küche ist in Wassertönen (Blau, Schwarz, Dunkelgrau) gestaltet
- **DANN** Wasser-Element vermeiden; wenn doch, mit Erdtönen ausgleichen
- **Warum:** Die Küche ist ein Ort des Feuers.
- <sub>Räume: kueche · Profil: `wandfarbe_element == wasser`</sub>

### KU-11 · Messer verstauen  (mittel, 🔵 Foto (automatisch))
- **WENN** Messer liegen offen
- **DANN** Messer in Schubladen aufbewahren
- **Warum:** Messer stehen für Aggression.
- <sub>Räume: kueche, studio · Prüfung: `foto:F20` · Profil: `messer_sichtbar`</sub>

### KU-12 · Wenig offene Regale  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** es gibt viele offene Wandregale
- **DANN** offene Regale minimieren
- **Warum:** Sie erzeugen aggressives Chi und wirken unordentlich.
- <sub>Räume: kueche, studio · Profil: `offene_regale`</sub>

### KU-13 · Keine Spiegel  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel hängt in der Küche, vor allem gegenüber dem Herd
- **DANN** keine Spiegel in der Küche
- **Warum:** Sie verteilen das aggressive Chi der Küche.
- <sub>Räume: kueche · Prüfung: `grundriss:KU4`</sub>

### KU-14 · Mülleimer verstecken  (klein, 🔵 Foto (automatisch))
- **WENN** Mülleimer stehen sichtbar
- **DANN** Müll und Recycling nicht offen zeigen
- **Warum:** Sie stören den Eindruck von Fülle.
- <sub>Räume: kueche, studio · Prüfung: `foto:F21` · Profil: `muell_sichtbar`</sub>

### KU-15 · Herd in Kommandoposition  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** der Herd wird platziert
- **DANN** hinten im Raum, nicht direkt zur Tür, aber von der Kochposition die Tür im Blick
- **Warum:** Der Herd ist das wichtigste Element der Küche.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU1`</sub>

### KU-16 · Ofen nicht auf Sitzplätze  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Ofentür zeigt auf Sitzplätze
- **DANN** Ofen weg von Sitzbereichen
- **Warum:** Der Ofen strahlt das Feuer nach vorne ab.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU5`</sub>

### KU-17 · Kochfeld nicht unters Fenster  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Kochfeld liegt unter einem Fenster
- **DANN** Kochfeld zur Kochinsel oder zur Wand mit Spritzschutz; die Spüle darf unters Fenster
- **Warum:** Unter dem Fenster entweicht die Energie.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU3`</sub>

### KU-18 · Spüle diskret  (klein, ⚪ Tipp)
- **WENN** die Spüle steht im Mittelpunkt
- **DANN** Spüle zurückhaltend; Fenster oder Kochinsel sind gute Plätze
- **Warum:** Die Küche soll warm und feurig sein.
- <sub>Räume: kueche, studio</sub>

### KU-19 · Kühlschrank  (mittel, 🟢 Grundriss (automatisch))
- **WENN** der Kühlschrank fällt auf oder steht neben dem Herd
- **DANN** Kühlschrank einfügen (Farbe wie Küche oder integriert), nicht neben den Herd
- **Warum:** Er ist ein Wasser-Gerät, nichts zum Feiern.
- **Abhilfe:** Gute Isolierung zwischen beiden.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:KU2`</sub>

### KU-20 · Kleine Küche  (klein, ⚪ Tipp)
- **WENN** die Küche ist klein
- **DANN** Kombigeräte, kleinere Geräte, integrierte Geräte, immer aufgeräumt; ohne Oberschränke, wenn genug Stauraum
- **Warum:** Integration wirkt ruhiger und größer.
- <sub>Räume: kueche, studio</sub>

### KU-21 · Lange Küche  (klein, ⚪ Tipp)
- **WENN** die Küche ist lang (Galeerenküche)
- **DANN** breite Pendelleuchten statt einer Reihe kleiner, Geräte an die Stirnwand, großzügige Insel
- **Warum:** Eine Reihe kleiner Lampen wirkt wie ein Zugwaggon.
- <sub>Räume: kueche, studio</sub>

### KU-22 · Unregelmäßige Küche  (klein, ⚪ Tipp)
- **WENN** die Küche hat Nischen oder ist L-förmig
- **DANN** Nischen als Speisekammer, Kühlschrank in Ecken, Arbeitsbereiche in Sichtweite
- <sub>Räume: kueche, studio</sub>

### KU-23 · Fensterlose Küche  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Küche hat kein Fenster
- **DANN** öffnen, viel Seitenlicht – aber keine Spiegel
- **Warum:** Energie soll trotzdem fließen.
- <sub>Räume: kueche, studio · Prüfung: `grundriss:C08`</sub>

## 4 Planung – Büro

### BU-01 · Lage  (klein, ⚪ Tipp)
- **WENN** das Arbeitszimmer wird geplant
- **DANN** Konzentration → hinterer, ruhiger Teil; Publikumsverkehr → vorne; weg von Küche und Bad
- **Warum:** Die Umgebung muss zur Arbeit passen.
- <sub>Räume: wohnung</sub>

### BU-02 · Funktionen trennen  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** du arbeitest im Wohn- oder Schlafzimmer
- **DANN** Arbeitsbereich klar von den anderen Funktionen trennen
- **Warum:** Vermischte Funktionen stören Arbeit und Erholung.
- **Abhilfe:** Raumteiler, Teppich, eigene Ecke.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:C05`</sub>

### BU-03 · Tageslicht  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Arbeitszimmer hat kein Fenster
- **DANN** immer bei Tageslicht arbeiten; fensterlose Räume nur kurz (z. B. Online-Meeting)
- **Warum:** Ohne Tageslicht fehlt die Energie – nie lange nur unter Kunstlicht arbeiten.
- <sub>Räume: buero · Prüfung: `grundriss:C08`</sub>

### BU-04 · Schreibtisch in Kommandoposition  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** der Schreibtisch wird platziert
- **DANN** Wand hinter dir, nie Rücken zur Tür, Tür im Blick; seitlich zur Tür ist okay
- **Warum:** Hier verdienst du dein Geld – du brauchst die beste Umgebung.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:K01`, `grundriss:K03`</sub>

### BU-05 · Kundeneingang  (klein, ⚪ Tipp)
- **WENN** Kunden besuchen dich
- **DANN** einladender, deutlicher Eingang
- **Warum:** So finden Kunden und Wohlstand leicht zu dir.
- <sub>Räume: buero</sub>

### BU-06 · Farben nach Ziel  (klein, ⚪ Tipp)
- **WENN** Farben werden gewählt
- **DANN** Wachstum: Grün/Hellblau; Wohlstand: Gold/satte Töne; Stabilität: Erdtöne; flexibel: Schwarz/Dunkelblau; präzise: Weiß
- **Warum:** Die Farben sollen zum Ziel deiner Arbeit passen.
- <sub>Räume: buero</sub>

### BU-07 · Kunst im Büro  (klein, ⚪ Tipp)
- **WENN** Bilder werden aufgehängt
- **DANN** Motive, die deine Arbeit und Wachstum zeigen; keine einschüchternden Porträts
- **Warum:** Gesichter können einschüchtern – außer sie inspirieren dich.
- <sub>Räume: buero</sub>

### BU-08 · Gleichmäßiges Licht  (mittel, ⚪ Tipp)
- **WENN** das Arbeitslicht ist ungleichmäßig
- **DANN** anders als im Rest der Wohnung: gleichmäßig hell
- **Warum:** Konzentration braucht gutes, gleichmäßiges Licht.
- **Abhilfe:** Uplighter gegen eine weiße Decke.
- <sub>Räume: buero</sub>

### BU-09 · Ordnung im Büro  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** der Arbeitsplatz ist unordentlich
- **DANN** aufgeräumt; Unterlagen sinnvoll kategorisieren
- **Warum:** Ordnung im Raum = Ordnung im Kopf.
- <sub>Räume: buero · Profil: `unordnung`</sub>

### BU-10 · Pflanzen im Büro  (klein, 🔵 Foto (automatisch))
- **WENN** das Büro hat keine Pflanzen
- **DANN** Pflanzen am Fenster – das Büro ist ein Yang-Bereich
- **Warum:** Pflanzen stehen für Wachstum.
- <sub>Räume: buero · Prüfung: `foto:F08`</sub>

### BU-11 · Aquarium  (klein, ⚪ Tipp)
- **WENN** du wünschst dir mehr Energie
- **DANN** ein gepflegtes Aquarium bringt Wohlstand und Energie
- **Warum:** Wasser steht für Wohlstand.
- **Abhilfe:** Nur wenn du es pflegst.
- <sub>Räume: buero</sub>

### BU-12 · Nichts über dem Kopf  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** über dem Schreibtisch hängt ein Balken oder eine Pendelleuchte
- **DANN** nicht darunter sitzen
- **Warum:** Schweres über dem Kopf belastet unbewusst.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:K08`, `grundriss:L01`</sub>

### BU-13 · Nicht zu nah an der Tür  (mittel, 🟢 Grundriss (automatisch))
- **WENN** der Schreibtisch steht direkt an der Tür
- **DANN** Abstand zur Tür
- **Warum:** Durch die Tür kommt das Chi herein.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:K06`</sub>

### BU-14 · Fenster seitlich  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Fenster liegt hinter oder vor dem Schreibtisch
- **DANN** Fenster seitlich (gleichmäßiges Licht); nicht dahinter (beobachtet), nicht davor (Ablenkung, Blendung)
- **Warum:** Seitenlicht ist am angenehmsten.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:K13`, `grundriss:K02`, `foto:F12`</sub>

### BU-15 · Freier Weg  (mittel, 🟢 Grundriss (automatisch))
- **WENN** der Weg zum Arbeitsplatz ist verstellt
- **DANN** freier Weg zum Schreibtisch
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:H04`, `grundriss:H05`</sub>

### BU-16 · Viele Bildschirme  (mittel, 🟢 Grundriss (automatisch))
- **WENN** du arbeitest mit vielen Monitoren
- **DANN** lieber zur Wand schauen – aber Tür im Blick, keine Wandregale darüber
- **Warum:** Bildschirme sind selbst Fenster zur Welt.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:S01`</sub>

### BU-17 · Schreibtischform  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** ein Schreibtisch wird gewählt
- **DANN** rechteckig für Verhandlungen, geschwungen für Kreativität; hell/naturfarben; keine spiegelnden Oberflächen
- **Warum:** Spiegelnde Flächen bringen zu viel Energie.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Profil: `schreibtisch_oberflaeche == glaenzend`</sub>

### BU-18 · Keine offenen Regale  (klein, 🟢 Grundriss (automatisch))
- **WENN** das Büro hat viele offene Regale
- **DANN** geschlossene Schränke bevorzugen
- **Warum:** Offene Regale erzeugen aggressives Chi.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:S02` · Profil: `offene_regale`</sub>

### BU-19 · Bücher in Reichweite  (klein, 🟢 Grundriss (automatisch))
- **WENN** das Bücherregal steht weit weg
- **DANN** Regal leicht erreichbar vom Arbeitsplatz; Nachschlagewerke hinter dir, vorne frei
- **Warum:** Wissen im Rücken stützt dich, freie Sicht vorne klärt die Gedanken.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:B01`</sub>

### BU-20 · Bücher aufrecht  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** Bücher liegen quer gestapelt
- **DANN** Bücher aufrecht stellen
- **Warum:** Liegende Bücher wirken unordentlich.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Profil: `buecher_liegend`</sub>

### BU-21 · Tagesbett im Büro  (klein, 🟢 Grundriss (automatisch))
- **WENN** im Büro steht ein Sofa oder Tagesbett
- **DANN** die beste Position bleibt dem Schreibtisch; das Tagesbett nicht zur Tür richten
- <sub>Räume: buero · Prüfung: `grundriss:B03`</sub>

### BU-22 · Rücken zur Tür unvermeidbar  (mittel, 🟢 Grundriss (automatisch))
- **WENN** du musst mit dem Rücken zur Tür sitzen
- **DANN** beim Arbeiten die Tür schließen, kleinen Spiegel auf den Tisch, Stuhl mit hoher Lehne
- **Warum:** So siehst du, wer kommt.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:K03`</sub>

### BU-23 · Schreibtisch vor der Wand  (klein, 🟢 Grundriss (automatisch))
- **WENN** der Schreibtisch steht direkt vor der Wand
- **DANN** tieferen Tisch nehmen, Bilder/Pinnwand an die Wand
- **Warum:** Eine Wand direkt vor dir wirkt unterdrückend.
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:K12`</sub>

### BU-24 · Fenster vor und hinter dir  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Tür und Fenster liegen sich gegenüber, du sitzt dazwischen
- **DANN** lieber zur Wand schauen als mit dem Rücken zur Tür
- <sub>Räume: buero, schlafzimmer, wohnzimmer, studio, kinderzimmer · Prüfung: `grundriss:C01`, `grundriss:K03`</sub>

### BU-25 · Geteiltes Büro  (mittel, 🟢 Grundriss (automatisch))
- **WENN** mehrere Personen arbeiten im Raum
- **DANN** Gleichgestellte: niemand in schlechter Position, gleich große Tische; Hierarchie: der/die Ranghöchste bekommt die Kommandoposition; zu zweit: Tische gegenüber, keiner sieht den Bildschirm des anderen
- **Warum:** Ungleich große Tische führen zu Konflikten.
- <sub>Räume: buero · Prüfung: `grundriss:B02`</sub>

## 4 Planung – Schlafzimmer

### SZ-01 · Lage  (klein, ⚪ Tipp)
- **WENN** die Wohnung wird geplant
- **DANN** Schlafzimmer weit weg vom Eingang, hinter den öffentlichen Räumen; nicht am Bad, nicht an der Küche
- **Warum:** Es ist ein Rückzugsort vor der Welt.
- **Abhilfe:** Liegt es am Eingang: Tür geschlossen halten und in Wandfarbe streichen.
- <sub>Räume: wohnung</sub>

### SZ-02 · Bett symmetrisch  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Bett wird platziert
- **DANN** symmetrisch, der Rest des Raums unterstützt das Schlafen
- **Warum:** Ein mittig stehendes Bett verankert den Raum.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K16`</sub>

### SZ-03 · Keine Arbeit, kein Sport, kein TV  (mittel, 🟢 Grundriss (automatisch))
- **WENN** im Schlafzimmer stehen Schreibtisch, Sportgeräte oder TV
- **DANN** möglichst vermeiden; sonst eine reine Ruhezone ums Bett
- **Warum:** Im Schlafzimmer soll der Kopf abschalten.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C04`, `grundriss:C05`</sub>

### SZ-04 · Erde statt Feuer  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** das Schlafzimmer ist in kräftigen Feuerfarben gestaltet
- **DANN** vor allem Erde: horizontale Linien, natürliche, neutrale Töne
- **Warum:** Das Schlafzimmer soll beruhigen.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `wandfarbe_element == feuer`</sub>

### SZ-05 · Keine Ecken aufs Bett  (mittel, 🟢 Grundriss (automatisch))
- **WENN** spitze Möbel- oder Wandecken zeigen auf das Bett
- **DANN** Raum quadratisch/rechteckig halten; keine Ecken aufs Bett richten
- **Warum:** Spitze Ecken erzeugen tötendes Sha-Chi: Wie eine Messerspitze signalisieren sie dem Unterbewusstsein Gefahr – gerade im Schlaf, wenn man ungeschützt ist.
- **Abhilfe:** Runde oder niedrige Möbel, Ecken mit Pflanzen oder Stoff abmildern.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K14`</sub>

### SZ-60 · Kein langer Raum  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Schlafzimmer ist lang und schmal
- **DANN** lange Räume als Schlafzimmer meiden; sonst Bett quer stellen
- **Warum:** Im langen Raum bildet sich Bewegungs-Chi – man schläft wie in einem Flur.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K15`</sub>

### SZ-06 · Großes Schlafzimmer  (klein, ⚪ Tipp)
- **WENN** das Schlafzimmer ist sehr groß
- **DANN** Zonen mit Teppichen schaffen; das Bett mit Bank/Sofa am Fußende schützen
- **Warum:** In großen Räumen fühlt man sich ungeschützt und verloren.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-07 · Tür und Fenster  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Schlafzimmer hat kein Fenster
- **DANN** nie einen fensterlosen Raum als Schlafzimmer
- **Warum:** Faustregel: Wo eine Pflanze nicht überleben kann, soll niemand schlafen.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C08`</sub>

### SZ-08 · Viele Fenster  (mittel, ⚪ Tipp)
- **WENN** das Schlafzimmer hat viele Fenster
- **DANN** zum Schlafen die Vorhänge schließen
- **Warum:** Sonne und Wind dringen zu leicht ein, man fühlt sich ausgesetzt.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-09 · Nur eine Tür  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** das Schlafzimmer hat mehrere Türen
- **DANN** weitere Türen nur zu privaten Räumen (eigener Balkon ok, Gemeinschaftsterrasse nicht)
- **Warum:** Mehrere Türen machen das Schlafzimmer zum Durchgangsraum.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `anzahl_tueren > 1`</sub>

### SZ-10 · Keine Elektronik  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** TV, Computer oder Handy sind im Schlafzimmer
- **DANN** möglichst entfernen; analoge Alternativen (Wärmflasche statt Heizdecke)
- **Warum:** Elektronik bringt Unruhe; schwarze Bildschirme wirken wie Spiegel.
- **Abhilfe:** Nachts ausschalten und abdecken.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C04`, `foto:F01` · Profil: `computer_im_raum`</sub>

### SZ-11 · Handy am Bett  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** das Handy liegt am Bett
- **DANN** Handy außerhalb des Bettbereichs laden
- **Warum:** Es hält den Kopf wach.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `smartphone_am_bett`</sub>

### SZ-12 · Kein Yang im Schlafzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Aquarium, Pflanzen oder Drachenbilder sind im Schlafzimmer
- **DANN** vermeiden – außer sie geben dir Ruhe (Pflanzen als Freunde: gruppiert ans Fenster, weit weg vom Bett)
- **Warum:** Sie bringen Yang-Energie, das Schlafzimmer braucht Yin.
- <sub>Räume: schlafzimmer, gaestezimmer · Prüfung: `grundriss:C06`, `grundriss:C03`, `foto:F08`, `foto:F11`</sub>

### SZ-13 · Kopfteil  (wichtig, 🟣 Profil (aus deinen Angaben))
- **WENN** das Bett hat kein oder nur ein Gitter-Kopfteil
- **DANN** massives oder gepolstertes Kopfteil, je größer und breiter desto besser
- **Warum:** Das Kopfteil ist deine Schildkröte.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `bettkopfteil in ['keins', 'gitter']`</sub>

### SZ-14 · Stabiles Bett  (wichtig, 🟣 Profil (aus deinen Angaben))
- **WENN** das Bett ist wackelig oder ein Wasserbett
- **DANN** stabiler Rahmen; Wasserbetten unbedingt vermeiden
- **Warum:** Schlafen braucht Stabilität; Wasser gehört nicht unter den Schlafenden.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `wasserbett`</sub>

### SZ-15 · Himmelbett  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** du hast ein Himmelbett
- **DANN** lieber ein niedriges Bett
- **Warum:** Himmelbetten wirken streng, niedrige Betten ruhig.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `bett_typ == himmelbett`</sub>

### SZ-16 · Luft unter dem Bett  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** der Bettkasten ist vollgestopft oder das Bett liegt direkt am Boden
- **DANN** Bett etwas über dem Boden, Bettkasten nicht überfüllen
- **Warum:** Luft muss zirkulieren, sonst sammelt sich Feuchtigkeit.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `bett_unterbau_vollgestopft`</sub>

### SZ-17 · Bettwäsche  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Bettwäsche ist schwarz
- **DANN** helle, ruhige Farben; wenn dunkel, dann nicht schwarz
- **Warum:** Das Bett soll Ruhe ausstrahlen.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `bettwaesche_farbe == schwarz`</sub>

### SZ-18 · Bett machen  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** das Bett bleibt ungemacht
- **DANN** morgens das Bett machen
- **Warum:** So staut sich kein abgestandenes Chi.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `bett_ungemacht`</sub>

### SZ-19 · Feste Wand hinter dem Bett  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Bett schwebt frei im Raum oder steht an einer niedrigen Trennwand
- **DANN** Kopfteil an eine feste Wand
- **Warum:** Die Schildkröte schützt dich im Schlaf.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K01`</sub>

### SZ-20 · Nicht ans Fenster  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Kopfteil steht vor einem Fenster
- **DANN** vermeiden; sonst massives Kopfteil, schwere Vorhänge, Brüstung höher als das Kopfteil
- **Warum:** Am Fenster fehlt der Schutz im Rücken.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K02`, `foto:F06`</sub>

### SZ-21 · Keine Säulen oder schrägen Wände  (mittel, ⚪ Tipp)
- **WENN** das Bett steht an einer Säule oder an einer schrägen/unebenen Wand
- **DANN** an eine gerade, ebene Wand
- **Warum:** Unebene Wände geben keinen stabilen Halt.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-22 · Raum vor dem Bett  (mittel, 🟢 Grundriss (automatisch))
- **WENN** vor dem Bett ist kaum Platz – oder sehr viel leerer Raum
- **DANN** ausgewogen: genug Platz, aber nicht zu viel offenen Raum vor dem Bett
- **Warum:** Zu eng wirkt beengend, zu viel Raum bringt zu viel Chi.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K12`</sub>

### SZ-23 · Tür im Blick  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** vom Bett aus sieht man die Tür nicht
- **DANN** breiter Blick über den Raum und auf die Tür; keine hohen Möbel zwischen Bett und Tür
- **Warum:** Man will sehen, wer hereinkommt.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K03`</sub>

### SZ-24 · Nicht an der Türwand  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Bett steht an derselben Wand wie die Tür
- **DANN** an eine andere Wand
- **Warum:** Von dort kann man die Tür nicht überblicken.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K07`</sub>

### SZ-25 · Von beiden Seiten zugänglich  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Bett ist nur von einer Seite zugänglich
- **DANN** von beiden Seiten einsteigen können (für Paare Pflicht; für Singles = offen für einen Partner)
- **Warum:** Ein Bett an der Wand ist für eine Person gemacht.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K10`</sub>

### SZ-26 · Nachttische als Paar  (mittel, 🟢 Grundriss (automatisch))
- **WENN** es gibt nur einen Nachttisch oder sie sind sehr verschieden
- **DANN** zwei Nachttische und Lampen mit gleichem visuellem Gewicht links und rechts
- **Warum:** Gleichgewicht zu beiden Seiten (Drache und Tiger).
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K17`, `foto:F14`</sub>

### SZ-27 · Bett in der Ecke  (klein, 🟢 Grundriss (automatisch))
- **WENN** das Bett steht mit der Längsseite an der Wand in der Ecke
- **DANN** okay für glückliche Singles; wer Romantik sucht, vermeidet es
- **Warum:** Das Bett ist dann nur für eine Person.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K10`</sub>

### SZ-28 · Füße nicht zur Tür  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** die Füße zeigen in direkter Linie zur Tür
- **DANN** nie in Linie mit der Tür; sonst Paravent oder schweres Möbel am Fußende, Bereich vor der Tür ruhig halten
- **Warum:** Das Chi strömt direkt auf dich zu; die Lage erinnert an einen Sarg oder eine Steißgeburt.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K04`, `foto:F07`</sub>

### SZ-29 · Füße nicht zum Fenster  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Füße zeigen zu einem großen Fenster
- **DANN** vermeiden – bei kleinen Fenstern oder ruhigem Ausblick okay
- **Warum:** Ein großes Fenster bringt viel Bewegungs-Chi.
- **Abhilfe:** Vorhänge.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K05`</sub>

### SZ-30 · Keine Öffnung am Fußende  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Füße zeigen zu einer Schranktür oder anderen Öffnung
- **DANN** Türen diskret gestalten und geschlossen halten
- **Warum:** Jede Öffnung bringt Bewegung.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K04`</sub>

### SZ-31 · Tür weit weg  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** das Bett steht nahe an der Tür
- **DANN** die Tür so weit wie möglich vom Bett
- **Warum:** An der Tür ist das stärkste Chi.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K06`</sub>

### SZ-32 · Spiegel  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel hängt im Schlafzimmer, vor allem sichtbar vom Bett oder am Fußende
- **DANN** Spiegel vermeiden; wenn doch, nicht vom Bett aus sichtbar
- **Warum:** Spiegel verhalten sich wie Türen und bringen Bewegung.
- **Abhilfe:** Nachts abdecken.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C02`, `foto:F02`</sub>

### SZ-33 · Keine Balken über dem Bett  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** ein Balken läuft über das Bett
- **DANN** Bett so stellen, dass kein Balken quer darüber läuft
- **Warum:** Balken sind wie Klingen über dir.
- **Abhilfe:** Abgehängte Decke oder Balken in Deckenfarbe.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K08`</sub>

### SZ-34 · Dachschräge  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Bett steht unter einer Dachschräge
- **DANN** Kopf an die hohe Seite, ausgeglichen; beim Satteldach mittig unter den First
- **Warum:** Die niedrige Decke drückt auf den Kopf.
- **Abhilfe:** Kräftiges Kopfteil, Lampen heben die Decke optisch.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K09`</sub>

### SZ-35 · Keine schweren Lampen über dem Bett  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** eine schwere Leuchte, ein Ventilator oder eine Skulptur hängt über dem Bett
- **DANN** nichts Schweres über dem Bett; eine leichte Papierleuchte ist okay
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:L01`, `foto:F05` · Profil: `pendelleuchte_ueber_bett`</sub>

### SZ-36 · Keine schweren Bilder über dem Bett  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** ein schweres Bild mit Glas hängt über dem Bett
- **DANN** nur leichte Textilien oder ein Wandgemälde
- **Warum:** Gefährlich, falls es fällt.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:S01`, `foto:F04`</sub>

### SZ-37 · Keine Regale über dem Bett  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** über dem Kopfteil sind Regale oder Wandmöbel
- **DANN** nie Regale über das Kopfteil
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:S01`, `foto:F03`</sub>

### SZ-38 · Kopf nach Norden  (klein, ⚪ Tipp)
- **WENN** du schläfst mit dem Kopf nach Norden
- **DANN** kann man berücksichtigen, aber nicht auf Kosten anderer Regeln
- **Warum:** Manche Kulturen meiden es (Magnetfeld).
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-39 · Außenwand im Altbau  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Bett steht in einem Altbau an der Außenwand
- **DANN** an eine Innenwand
- **Warum:** Die Außenwand überträgt Temperaturschwankungen.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C07`</sub>

### SZ-40 · Begehbarer Schrank  (klein, ⚪ Tipp)
- **WENN** ein begehbarer Kleiderschrank liegt im Schlafbereich
- **DANN** außerhalb des Schlafbereichs; sonst die Tür möglichst unauffällig
- **Warum:** Eine zusätzliche Tür macht den Raum zum Durchgang; dahinter 'lauert' etwas.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-41 · Einbauschrank  (mittel, 🔵 Foto (automatisch))
- **WENN** es gibt mehrere kleine Schränke
- **DANN** Einbauschrank > ein großer freistehender > mehrere kleine; freistehende zum Begradigen unebener Wände nutzen
- **Warum:** Viele kleine Schränke = viele spitze Ecken.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `foto:F17` · Profil: `kleiderschrank == mehrere`</sub>

### SZ-42 · Schrank aufgeräumt  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** der Kleiderschrank ist vollgestopft
- **DANN** ausmisten, Platz lassen
- **Warum:** Ein vollgestopfter Schrank sagt: kein Platz für jemand Neuen in deinem Leben.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `kleiderschrank_vollgestopft`</sub>

### SZ-43 · Arbeiten im Schlafzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** du arbeitest im Schlafzimmer
- **DANN** auf ein Minimum beschränken, nie auf dem Bett arbeiten, eigener Stuhl, Computer nachts aus
- **Warum:** Das Bett ist nur für die Ruhe.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C05`</sub>

### SZ-44 · Schminktisch  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Schminktisch mit Spiegel steht im Schlafzimmer
- **DANN** den Spiegel vom Bett weg richten
- **Warum:** Ein Schminktisch passt besser als ein Arbeitstisch – aber der Spiegel soll dich nicht im Bett zeigen.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C02`</sub>

### SZ-45 · Nachttische  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Nachttische haben spitze Ecken, sind höher als die Matratze oder aus Glas
- **DANN** rund oder niedriger als die Matratze, geschlossen, stabil, nicht aus Glas, nicht zu hoch
- **Warum:** Ecken am Kopf und hohe Möbel, die über dir aufragen, stören den Schlaf; Glas ist kalt wie ein Spiegel.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K14`, `grundriss:K17` · Profil: `nachttisch_material == glas`</sub>

### SZ-46 · Bad am Schlafzimmer  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** ein Bad grenzt ans Schlafzimmer
- **DANN** Badtür nachts schließen; das WC nicht an derselben Wand wie das Bett; nicht unter Badewanne/WC schlafen
- **Warum:** Wasser und Abwasser gehören nicht zum Schlafen; undichte Rohre bedeuten Schimmel.
- **Abhilfe:** Kalebasse zwischen Bett und Wand.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `wc_an_bettwand`</sub>

### SZ-47 · Kleines Schlafzimmer  (klein, ⚪ Tipp)
- **WENN** das Schlafzimmer ist klein
- **DANN** große Stücke in die hintersten Ecken; das Bett nicht beengen; breites, waagrechtes Kopfteil über die Wand
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-48 · Langes Schlafzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Schlafzimmer ist lang
- **DANN** Bett quer zur Raumlänge; nicht ungeschützt am Raumende; Kunst an die Längswände, keine Spiegel
- **Warum:** Ungeschützt am Ende eines langen Raums ist wie Füße zur Tür.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:K15`</sub>

### SZ-49 · Unregelmäßiges Schlafzimmer  (klein, ⚪ Tipp)
- **WENN** das Schlafzimmer ist L-förmig oder unregelmäßig
- **DANN** mit Einbauschränken begradigen, die Extra-Ecke als Ankleide nutzen; Kunst statt Spiegel
- **Warum:** Im Schlafzimmer stören Spiegel die Ruhe.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-50 · Viele Türen/Fenster  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Schlafzimmer hat viele Türen und Fenster
- **DANN** Bett an den ruhigsten, dunkelsten Punkt abseits der Chi-Bahnen; schwere Vorhänge; Innentüren schließen; dunklere Farben machen es intimer
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C01`</sub>

### SZ-51 · Geteiltes Zimmer: gleiche Betten  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** zwei Personen teilen sich das Zimmer
- **DANN** gleich große Betten mit Abstand; nicht Füße zum Kopf des anderen; jeder hat einen eigenen Bereich, niemand muss durch den Bereich des anderen
- **Warum:** Ungleiche Betten zeigen Ungleichgewicht.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:G01`, `grundriss:G02`</sub>

### SZ-52 · Etagenbett  (klein, 🟢 Grundriss (automatisch))
- **WENN** es gibt ein Etagenbett
- **DANN** möglichst vermeiden; die ältere Person schläft oben
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:G03`</sub>

### SZ-53 · Paare  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Paar schläft getrennt
- **DANN** zusammen schlafen; oder zwei getrennte Betten mit Abstand – nie zwei Einzelbetten zusammengeschoben
- **Warum:** Zusammengeschobene Betten stehen für eine versteckte, unausweichliche Trennung.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:G01`</sub>

### SZ-54 · Paar und Single  (klein, ⚪ Tipp)
- **WENN** ein Paar teilt das Zimmer mit einer Einzelperson
- **DANN** vermeiden
- **Warum:** Die Einzelperson wirkt wie eine dritte Partei in der Beziehung.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio</sub>

### SZ-55 · Kinderzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Kinderzimmer wird eingerichtet
- **DANN** mehr Yang: Pflanzen und Computer sind okay; am besten Ostseite; Einzelbett mit Längsseite an die Wand
- **Warum:** Kinder brauchen weniger Erholung und mehr Wachstum.
- <sub>Räume: kinderzimmer · Prüfung: `grundriss:K11`</sub>

### SZ-56 · Kinder-Schreibtisch  (klein, 🟢 Grundriss (automatisch))
- **WENN** der Kinder-Schreibtisch steht so, dass die Eltern von der Tür den Bildschirm sehen
- **DANN** lieber nicht – das gibt dem Kind Sicherheit und Respekt
- <sub>Räume: kinderzimmer · Prüfung: `grundriss:K03`</sub>

### SZ-57 · Keine offenen Regale im Kinderzimmer  (klein, 🟢 Grundriss (automatisch))
- **WENN** Bücher stehen in offenen Regalen
- **DANN** geschlossene Regale
- **Warum:** Offene Regale wirken wie Balken.
- <sub>Räume: kinderzimmer · Prüfung: `grundriss:S02`</sub>

### SZ-58 · Gästezimmer  (klein, 🟢 Grundriss (automatisch))
- **WENN** das Gästezimmer hat eine Schlafcouch
- **DANN** wie ein Schlafzimmer behandeln; ausgeklappt soll sie in der Kommandoposition stehen
- <sub>Räume: gaestezimmer · Prüfung: `grundriss:K01`, `grundriss:K03`</sub>

### SZ-59 · Unterwegs  (klein, ⚪ Tipp)
- **WENN** du schläfst im Hotel, Schlafsaal, Schiff oder Zelt
- **DANN** Schlafsaal: Bett am hinteren Ende; Schiff: Kabine mit Fenster; Zelt: Füße nicht zum Eingang
- **Warum:** Die gleichen Prinzipien gelten überall.
- <sub>Räume: unterwegs</sub>

## 4 Planung – Bad

### BA-01 · Lage  (klein, ⚪ Tipp)
- **WENN** die Wohnung wird geplant
- **DANN** Bad abseits der Hauptsichtachsen, nie am Eingang, nicht neben Küche oder Schlafzimmer, nicht in der Mitte
- **Warum:** Wie beim Körper: Das WC ist der 'Ausgang' und gehört nicht neben den 'Mund' (Haustür).
- <sub>Räume: wohnung</sub>

### BA-02 · Farben  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** das Bad ist rot oder in Feuerfarben gestaltet
- **DANN** keine Feuerfarben; Erde und Holz gleichen das Wasser aus
- **Warum:** Feuer zerstört Wasser.
- <sub>Räume: bad · Profil: `wandfarbe_element == feuer`</sub>

### BA-03 · Lüftung  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** das Bad ist schlecht belüftet
- **DANN** gute natürliche oder mechanische Lüftung
- **Warum:** Feuchtigkeit muss raus.
- <sub>Räume: bad · Profil: `bad_lueftung == False`</sub>

### BA-04 · Kein Spiegel auf das WC  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel spiegelt das WC
- **DANN** Spiegel umhängen
- <sub>Räume: bad · Prüfung: `grundriss:BA5`</sub>

### BA-05 · WC nicht von der Tür sichtbar  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** man sieht das WC von der Tür aus
- **DANN** WC außer Sicht, nicht in Linie mit der Tür, aber mit Blick zur Tür
- **Warum:** Sieht man es nicht, mildert sich seine Wirkung; ein Blick zur Tür gibt Sicherheit.
- <sub>Räume: bad · Prüfung: `grundriss:BA1`</sub>

### BA-06 · Licht im Bad  (mittel, ⚪ Tipp)
- **WENN** das Bad ist dunkel
- **DANN** Tageslicht ideal; sonst helle Wände und helle Leuchten
- <sub>Räume: bad</sub>

### BA-07 · WC-Deckel  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** der WC-Deckel bleibt offen
- **DANN** Deckel immer schließen
- **Warum:** Sonst 'spült man das Glück hinunter'.
- <sub>Räume: bad · Profil: `wc_deckel_offen`</sub>

### BA-08 · Pflanzen im Bad  (klein, ⚪ Tipp)
- **WENN** das Bad hat ein Fenster
- **DANN** Pflanzen sind ideal (Holz + Wasser); ohne Fenster keine Pflanzen
- **Warum:** Die Feuchtigkeit lässt viele Pflanzen gedeihen.
- <sub>Räume: bad</sub>

### BA-09 · WC an der Wand  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das WC steht frei oder unter dem Fenster
- **DANN** WC an eine feste Wand, nicht unters Fenster
- **Warum:** Auch auf dem WC gilt die Kommandoposition.
- <sub>Räume: bad · Prüfung: `grundriss:BA1`</sub>

### BA-10 · WC weg von der Wanne  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das WC steht neben der Badewanne
- **DANN** Abstand; die Dusche neben dem WC ist eher okay
- **Warum:** Niemand will beim Baden das WC neben dem Gesicht haben.
- **Abhilfe:** Waschbecken dazwischen.
- <sub>Räume: bad · Prüfung: `grundriss:BA2`</sub>

### BA-11 · WC-Nische  (klein, ⚪ Tipp)
- **WENN** das WC steht offen im Bad
- **DANN** idealerweise eigener Raum oder eigene Nische
- <sub>Räume: bad</sub>

### BA-12 · Badewanne  (mittel, 🟢 Grundriss (automatisch))
- **WENN** die Badewanne wird platziert
- **DANN** erstes und wichtigstes Element beim Eintreten, Fußende nicht in Linie zur Tür; Dusche möglichst nicht in Linie
- **Warum:** Die Wanne erinnert daran, dass das Bad ein Ort der Erholung ist.
- <sub>Räume: bad · Prüfung: `grundriss:BA3`</sub>

### BA-13 · Waschbecken  (mittel, 🟢 Grundriss (automatisch))
- **WENN** das Waschbecken wird platziert
- **DANN** nicht mit dem Rücken zur Tür; Waschtisch und Spiegel rechtwinklig zur Tür; trennt WC und Wanne
- <sub>Räume: bad · Prüfung: `grundriss:BA4`</sub>

### BA-14 · Kleines Bad  (klein, 🟢 Grundriss (automatisch))
- **WENN** das Bad ist klein
- **DANN** nirgends durchquetschen; Standflächen gemeinsam nutzen; Eckmontage ist erlaubt
- <sub>Räume: bad · Prüfung: `grundriss:H04`</sub>

### BA-15 · Fensterloses Bad  (mittel, ⚪ Tipp)
- **WENN** das Bad hat kein Fenster
- **DANN** Lüfter; helle Wandleuchten neben dem Spiegel statt Licht von oben; keine Pflanzen; große Spiegel; Naturstein; Düfte
- **Warum:** Die Luft darf nicht abstehen.
- <sub>Räume: bad</sub>

### BA-16 · Großes Bad  (klein, ⚪ Tipp)
- **WENN** das Bad ist groß
- **DANN** auf Erholung ausrichten: Wanne als Anker, WC abschirmen, großzügige Dusche
- <sub>Räume: bad</sub>

### BA-17 · Unregelmäßiges Bad  (klein, ⚪ Tipp)
- **WENN** das Bad hat Ecken und Nischen
- **DANN** WC in eine Ecke als private Nische, Einbauschränke in Nischen
- <sub>Räume: bad</sub>

## 4 Planung – Gemeinsame Räume

### GR-01 · Zonen  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Raum hat mehrere Funktionen
- **DANN** in Bereiche gliedern; Funktionen nicht vermischen (nicht im Bett arbeiten, nicht auf dem Sofa essen); wandelbare Möbel minimieren
- **Warum:** Wir verbinden Orte im Kopf mit Tätigkeiten.
- <sub>Räume: studio, wohnzimmer, schlafzimmer · Prüfung: `grundriss:C05`</sub>

### GR-02 · Nach Aktivität ordnen  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Bereiche werden verteilt
- **DANN** ähnlich aktive Tätigkeiten nebeneinander; Ruhiges nah am Bett, Aktives weit weg
- <sub>Räume: studio, wohnzimmer, schlafzimmer · Prüfung: `grundriss:ST1`, `grundriss:C05`</sub>

### GR-03 · Wohnen + Essen  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Wohnen und Essen sind in einem Raum
- **DANN** Esstisch nicht in den Wohnbereich ragen lassen, niedrige Konsole als Trenner; Essbereich näher zur Küche bzw. zum aktiveren Ende; Pendelleuchten nur über dem Esstisch
- <sub>Räume: wohnzimmer, studio · Prüfung: `grundriss:L02`</sub>

### GR-04 · Wohnen + Essen + Küche  (mittel, ⚪ Tipp)
- **WENN** Wohnen, Essen und Küche sind ein Raum
- **DANN** Küche ruhig (niedrige Schränke, neutrale Farben, aufgeräumt); Esstisch mit mehr Plätzen als die Theke; Spiegel nur auf der Essseite; Leuchte über dem Tisch, nicht über der Theke
- **Warum:** Die Küche ist hier Anhängsel – Essen und Wohnen bestimmen die Stimmung.
- <sub>Räume: studio, wohnzimmer</sub>

### GR-05 · Küche + Essen  (klein, ⚪ Tipp)
- **WENN** der Esstisch steht in der Küche
- **DANN** keine gepolsterten Sitze, lässiger Stil, Pendelleuchte über dem Tisch; isst du an der Theke, sie wie einen Tisch dekorieren
- <sub>Räume: kueche</sub>

### GR-06 · Arbeiten im Wohnbereich  (mittel, 🟢 Grundriss (automatisch))
- **WENN** du arbeitest im Wohnzimmer oder am Esstisch
- **DANN** eigener kleiner Schreibtisch weit weg von Küche, Durchgängen und Eingang; am Esstisch einen festen Arbeitsbereich; Obst/Blumen beim Arbeiten weg; TV aus; nicht arbeiten, während andere kochen
- <sub>Räume: wohnzimmer, studio, kueche · Prüfung: `grundriss:K06`</sub>

### GR-07 · Schlafen + Arbeiten  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** Schlaf- und Arbeitsbereich teilen sich den Raum
- **DANN** Arbeitsbereich näher zur Tür und im helleren Teil, Schlafbereich hinten; ist das Bett nahe der Tür, in eine geschützte Nische
- **Warum:** Besser im Wohnbereich arbeiten als im Schlafzimmer.
- <sub>Räume: schlafzimmer, studio · Prüfung: `grundriss:C05`</sub>

### GR-08 · Studio-Schichten  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** die ganze Wohnung ist ein Raum
- **DANN** Bett hinten (privat) → Wohnbereich als Puffer → Essen nahe der Küche → Küche weit weg vom Schlafbereich, eher Richtung Fenster; Eingangsbereich nicht zustellen
- <sub>Räume: studio · Prüfung: `grundriss:ST1`</sub>

### GR-09 · Haustiere: Käfige  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Vogel, Nager, Fische oder Reptilien werden untergebracht
- **DANN** nicht in Küche (Dämpfe), Bad (Feuchte) oder Schlafzimmer (Unruhe); Käfig an eine Wand, weg vom Eingang
- **Warum:** Tiere spüren den Raum oft stärker als wir.
- <sub>Räume: alle Räume · Prüfung: `grundriss:T01`</sub>

### GR-10 · Haustiere: Hundebox, Kratzbaum  (klein, 🟢 Grundriss (automatisch))
- **WENN** eine Hundebox oder ein Kratzbaum wird aufgestellt
- **DANN** so, dass das Tier die Tür sieht (Box) bzw. nah bei dir hoch sitzt (Kratzbaum)
- **Warum:** Geräusche ohne Quelle machen Tiere ängstlich; Tiere suchen ihre Kommandoposition.
- <sub>Räume: alle Räume · Prüfung: `grundriss:T02`</sub>

### GR-11 · Haustiere: Futter und Klo  (klein, 🟢 Grundriss (automatisch))
- **WENN** Futternapf und Katzenklo werden platziert
- **DANN** getrennt voneinander und vom Schlafplatz; Klo privat; Futter nahe deinem Essplatz
- <sub>Räume: alle Räume · Prüfung: `grundriss:T03`</sub>

## 5 Styling – Eindruck

### EI5-01 · Erster Blick  (mittel, 🟢 Grundriss (automatisch))
- **WENN** der Raum wird gestaltet
- **DANN** so gestalten, dass er vom Eingang aus gut aussieht; das Hauptmöbel verankert den Blick
- **Warum:** Der erste Eindruck zählt – vor allem für dich selbst, jeden Tag beim Heimkommen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:S08`</sub>

### EI5-02 · Stimmung des Bildes  (klein, ⚪ Tipp)
- **WENN** die Ansicht vom Eingang wird komponiert
- **DANN** Wohnzimmer großzügig und symmetrisch; Schlafzimmer ruhig mit Bett im Zentrum, waagrechten Linien, weichem Licht
- <sub>Räume: alle Räume</sub>

### EI5-03 · Unteres Drittel  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Stauraum hängt hoch an der Wand oder Kisten sind hoch gestapelt
- **DANN** Stauraum ins untere Drittel; oberen zwei Drittel nur Deko (Bilder, Lampen, Pflanzen)
- **Warum:** So wirkt der Raum durchdacht und ruhig.
- <sub>Räume: alle Räume · Prüfung: `grundriss:S02`, `foto:F09`</sub>

## 5 Styling – Ordnung

### OR-01 · Kategorien  (wichtig, 🔵 Foto (automatisch))
- **WENN** Dinge liegen ungeordnet herum
- **DANN** alles kategorisieren, Unterkategorien bilden, keine 'Sonstiges'-Kisten
- **Warum:** Unordnung gegen deinen Willen blockiert das Chi – und die Gedanken.
- <sub>Räume: alle Räume · Prüfung: `foto:F09` · Profil: `unordnung`</sub>

### OR-02 · Am Ort der Nutzung  (klein, ⚪ Tipp)
- **WENN** Dinge sind am falschen Ort
- **DANN** jedes Ding dort lagern, wo es gebraucht wird (Kochbücher ins Bücherregal!)
- **Warum:** Ein gutes System versteht sogar ein Fremder.
- <sub>Räume: alle Räume</sub>

### OR-03 · Beschriftung  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** Schränke haben Glastüren mit unordentlichem Inhalt
- **DANN** Beschriftungen statt Glastüren
- **Warum:** Durch Glas sieht man das Durcheinander.
- <sub>Räume: alle Räume · Profil: `schranktueren_glas`</sub>

### OR-04 · Zu viele Möbel  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** der Raum ist vollgestellt
- **DANN** auch zu viele Möbel sind Unordnung; Türen nie zustellen
- **Warum:** Blockierte Türen = blockierter Zugang zur Welt.
- <sub>Räume: alle Räume · Prüfung: `grundriss:H03`, `grundriss:H04`, `grundriss:H01`, `grundriss:H02`</sub>

### OR-06 · Stauraum zugänglich  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Schränke oder Kommoden lassen sich nicht richtig öffnen
- **DANN** vor Schrankfronten Platz lassen
- **Warum:** Schwer zugänglicher Stauraum führt zu Unordnung.
- <sub>Räume: alle Räume · Prüfung: `grundriss:H06`</sub>

### OR-05 · Geschmack finden  (klein, ⚪ Tipp)
- **WENN** du weißt nicht, was dir gefällt
- **DANN** Liste mit Dingen, die du liebst und hasst; das Gehasste entfernen; ein Lieblingsstück als Maßstab
- **Warum:** Feng Shui passt den Raum an deine natürlichen Neigungen an.
- <sub>Räume: alle Räume</sub>

## 5 Styling – Licht

### LI-01 · Gleiche Farbtemperatur  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** die Leuchtmittel im Raum haben unterschiedliche Lichtfarben
- **DANN** alle Leuchtmittel im Raum gleich
- **Warum:** Gemischte Lichtfarben wirken unruhig.
- <sub>Räume: alle Räume · Profil: `lichtfarbe_kelvin`</sub>

### LI-02 · Warmes Licht  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** Leuchtmittel sind sehr kalt (≥ 4000 K) oder sehr orange (< 2500 K)
- **DANN** 2700–2900 K für Wohnräume; 4000 K nur, wenn die Arbeit es verlangt
- **Warum:** Tageslichtweiß verwirrt die Sinne, zu orange wirkt unnatürlich.
- <sub>Räume: alle Räume · Profil: `lichtfarbe_kelvin ausserhalb (2500, 3500)`</sub>

### LI-03 · Diffuses Licht im Schlafzimmer  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** im Schlafzimmer sind klare, blendende Leuchtmittel
- **DANN** Schlafzimmer immer diffus (Opal/Milchglas, Schirme); klare Leuchtmittel nur in Yang-Räumen
- **Warum:** Klares Licht ist Yang, diffuses Yin.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `leuchtmittel == klar`</sub>

### LI-04 · Mehrere Lichtquellen  (mittel, 🟢 Grundriss (automatisch))
- **WENN** es gibt nur eine einzelne Lichtquelle
- **DANN** mehrere niedrige Lichtquellen; aktive Zonen hell, Wege dunkler
- **Warum:** In der Natur kommt Licht aus vielen Richtungen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:L03`, `foto:F16` · Profil: `anzahl_lichtquellen < 3`</sub>

### LI-05 · Drei von vier Ecken  (klein, 🟢 Grundriss (automatisch))
- **WENN** die Raumecken sind unbeleuchtet oder alle gleich hell
- **DANN** drei von vier Ecken beleuchten, eine bewusst im Schatten (Yin)
- <sub>Räume: alle Räume · Prüfung: `grundriss:L03`</sub>

### LI-06 · Licht am Fenster und am Flurende  (klein, ⚪ Tipp)
- **WENN** Licht wird platziert
- **DANN** Lampen vor Fenster (natürlicher Lichtort) und ans Ende langer Räume; unter Schrägen 'heben' sie die Decke
- <sub>Räume: alle Räume</sub>

### LI-07 · Form der Hängeleuchte  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** eine Hängeleuchte wird gewählt
- **DANN** rund (Metall/Himmel) oder dreieckig/kegelig (Feuer); keine eckigen, hochkant-rechteckigen oder wellenförmigen
- **Warum:** Erde, Holz und Wasser gehören auf den Boden, nicht an die Decke.
- <sub>Räume: alle Räume · Profil: `leuchten_form == eckig`</sub>

### LI-08 · Eine Statement-Leuchte  (klein, 🟢 Grundriss (automatisch))
- **WENN** mehrere Statement-Leuchten hängen im Raum
- **DANN** nur eine pro Raum; bei hoher Decke mittig, sonst über Ess- oder Couchtisch; zwei nur, wenn gleich
- <sub>Räume: alle Räume · Prüfung: `grundriss:L02`</sub>

### LI-09 · Downlight-Pendel  (klein, ⚪ Tipp)
- **WENN** eine Arbeits-Pendelleuchte hängt im Wohnzimmer oder Eingang
- **DANN** nur über Ess-, Küchen- oder Arbeitstischen; nicht höher als der Kopf (Leuchtmittel nicht sichtbar)
- <sub>Räume: alle Räume</sub>

### LI-10 · Keine Arbeitsleuchte im Schlafzimmer  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** eine gerichtete Arbeitsleuchte steht im Schlafzimmer
- **DANN** diffuse Tischleuchte statt Arbeitsleuchte
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Profil: `arbeitsleuchte_im_schlafzimmer`</sub>

### LI-11 · Uplighter  (klein, ⚪ Tipp)
- **WENN** der Raum hat kein Fenster oder eine niedrige Decke
- **DANN** Uplighter, die Licht an Wände und Decke werfen
- **Warum:** Sie wirken wie Licht in einer Grotte.
- <sub>Räume: alle Räume</sub>

### LI-12 · Spots  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** Spots sind auf Sitzplätze oder zufällige Bodenstellen gerichtet
- **DANN** Spots auf Kunst und Tische richten
- **Warum:** Licht auf dem Gesicht blendet und stört.
- <sub>Räume: alle Räume · Profil: `spots_auf_sitzplatz`</sub>

### LI-13 · Deckenleuchten  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** eine flache, eckige Deckenleuchte ist die Hauptlichtquelle
- **DANN** flache Deckenleuchten vermeiden (flaches Licht); wenn, dann rund
- <sub>Räume: alle Räume · Profil: `deckenleuchte == flach_eckig`</sub>

## 5 Styling – Farben

### FA-01 · Weiß  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** die Wände sind weiß, weil Weiß 'neutral' erscheint
- **DANN** Weiß bewusst wählen (Metall, leicht angespannt); unsicher? Mittleres Grau ist vielseitiger
- **Warum:** Weiß ist keine Grundfarbe, sondern ein Ende der Skala.
- <sub>Räume: alle Räume · Profil: `wandfarbe in ['weiss', 'weiß']`</sub>

### FA-02 · Farbtemperatur  (klein, ⚪ Tipp)
- **WENN** Farben werden für einen Raum gewählt
- **DANN** warme Räume (Sonnenseite) kühler, kühle Räume wärmer; Töne untereinander stimmig
- <sub>Räume: alle Räume</sub>

### FA-03 · Sättigung  (klein, ⚪ Tipp)
- **WENN** du bist unsicher bei der Wandfarbe
- **DANN** weniger gesättigte Töne (Sand statt Gelb, Terrakotta statt Rot)
- **Warum:** Weniger Sättigung wirkt ruhiger.
- <sub>Räume: alle Räume</sub>

### FA-04 · Feuer sparsam  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** eine ganze Wand ist rot/orange
- **DANN** Feuer in kleinen, kräftigen Dosen; große Flächen entsättigen (Terrakotta)
- **Warum:** Zu viel Feuer stört den Schlaf.
- <sub>Räume: alle Räume · Profil: `wandfarbe_element == feuer`</sub>

### FA-05 · Kein reines Schwarz  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** eine Wand ist schwarz
- **DANN** nie reines Schwarz – sehr dunkles Blau oder Braun; Schwarz nur als Akzent
- **Warum:** Ein leichter Farbton lässt das Auge ruhen.
- <sub>Räume: alle Räume · Profil: `wandfarbe == schwarz`</sub>

### FA-06 · Kein Blau im Esszimmer  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** das Esszimmer ist blau
- **DANN** kein Blau im Esszimmer
- **Warum:** Blau dämpft den Appetit.
- <sub>Räume: esszimmer · Profil: `wandfarbe in ['blau', 'dunkelblau', 'hellblau', 'graublau']`</sub>

### FA-07 · Grün dezent  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** eine Wand wird grün
- **DANN** sehr dezent (Grau mit Grünstich); Holz lieber über Pflanzen zeigen
- <sub>Räume: alle Räume · Profil: `wandfarbe == grün`</sub>

## 5 Styling – Kunst und Objekte

### KS-01 · Nur Geliebtes  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** Bilder werden zum 'Füllen' der Wand gekauft
- **DANN** nur Kunst, die dich berührt; keine Massenware zum Füllen
- **Warum:** Du siehst sie jeden Tag – sie prägt dich.
- <sub>Räume: alle Räume · Profil: `kunst_als_fueller`</sub>

### KS-02 · Uhren  (mittel, 🟢 Grundriss (automatisch))
- **WENN** eine Uhr wird aufgehängt
- **DANN** nur wo Eile und Präzision passen – nicht in Ess- oder Schlafzimmer
- <sub>Räume: alle Räume · Prüfung: `grundriss:E06`, `foto:F10`</sub>

### KS-03 · Familienfotos  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** Familienfotos hängen hoch an der Wand oder über dem Kamin
- **DANN** gerahmt auf Beistelltische nahe bei dir; nie über ein Feuer
- **Warum:** Hoch aufgehängte Porträts wirken wie eine Ausstellung (eher für Verstorbene).
- <sub>Räume: alle Räume · Profil: `familienfotos_hoch`</sub>

### KS-04 · Zettel und Postkarten  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** Zettel, Postkarten und Haftnotizen kleben an der Wand
- **DANN** alles in EINE Pinnwand
- **Warum:** Sie sind Unordnung und stören den Gedankenfluss.
- <sub>Räume: alle Räume · Profil: `notizzettel_an_wand`</sub>

### KS-05 · Motiv der Kunst  (klein, ⚪ Tipp)
- **WENN** Kunst wird platziert
- **DANN** Landschaften wirken wie Fenster, Menschen wie Spiegel, Grafiken wie Architektur; Porträts ziehen den Blick an; Worte an der Wand sorgfältig wählen
- <sub>Räume: alle Räume</sub>

### KS-06 · Vasen  (klein, ⚪ Tipp)
- **WENN** Vasen stehen leer
- **DANN** Vasen mit Blumen oder Obst füllen
- **Warum:** Nur so erfüllen sie ihren Zweck.
- <sub>Räume: alle Räume</sub>

### KS-07 · Bagua-Spiegel  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** ein Bagua-Spiegel hängt in der Wohnung
- **DANN** nie innen; der Autor rät ganz ab (unfreundliche Geste)
- <sub>Räume: alle Räume · Profil: `bagua_spiegel_innen`</sub>

### KS-08 · Drachen  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Drachenmotive werden aufgestellt
- **DANN** ins Wohnzimmer – nicht ins Schlafzimmer oder Bad
- **Warum:** Drachen haben sehr viel Energie.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C06`</sub>

### KS-09 · Geldfrosch  (klein, ⚪ Tipp)
- **WENN** ein Geldfrosch wird aufgestellt
- **DANN** nie direkt an den Eingang
- **Warum:** Dort ist zu viel Chi.
- <sub>Räume: alle Räume</sub>

### KS-10 · Fu-Hunde  (klein, ⚪ Tipp)
- **WENN** Fu-Hunde bewachen den Eingang
- **DANN** immer als Paar; von innen nach außen gesehen: Weibchen rechts, Männchen links
- <sub>Räume: flur</sub>

### KS-11 · Glückssymbole  (klein, ⚪ Tipp)
- **WENN** Glückssymbole werden genutzt
- **DANN** Mandarinenten als Paar, wo Liebe wachsen soll; Segelschiff zeigt ins Haus; Schildkröte nach hinten; Kalebasse gegen schlechte Energie
- **Warum:** Es sind Symbole – keine Wunder; entscheidend ist dein Gefühl.
- <sub>Räume: alle Räume</sub>

### KS-12 · Geräte am richtigen Ort  (mittel, ⚪ Tipp)
- **WENN** Küchengeräte stehen im Schlafzimmer
- **DANN** Geräte dort, wo sie hingehören (Essen in der Küche)
- **Warum:** Klare Funktionen verbessern das Wohlbefinden.
- <sub>Räume: alle Räume</sub>

### KS-13 · Religiöse Objekte  (mittel, 🟢 Grundriss (automatisch))
- **WENN** religiöse Objekte stehen im Schlafzimmer, auf dem Boden oder in Linie mit dem Bett
- **DANN** im wichtigsten Raum (Wohnzimmer); nicht im Schlafzimmer, nicht auf dem Boden, nicht in Linie mit dem Bett
- **Warum:** Sie haben eine ganz andere Energie als das Schlafzimmer.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C11` · Profil: `religioese_objekte`</sub>

### KS-14 · Papier und Kartons  (mittel, 🔵 Foto (automatisch))
- **WENN** Papiere und Kartons liegen herum
- **DANN** methodisch außer Sicht lagern; Unbenutztes wegwerfen
- **Warum:** Sie werden zu Unordnung.
- <sub>Räume: alle Räume · Prüfung: `foto:F09`</sub>

### KS-15 · Bewegte Objekte  (klein, ⚪ Tipp)
- **WENN** ein bewegtes Objekt wird aufgestellt
- **DANN** Mobiles bringen sanfte Ruhe; was sich nachts unkontrolliert bewegt, gehört nicht ins Schlafzimmer
- <sub>Räume: alle Räume</sub>

### KS-16 · Windspiel  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Windspiel wird aufgehängt
- **DANN** wo zu viele Fenster sind oder in Durchgängen (z. B. Treppe vor der Haustür); nie über Bett oder Schreibtisch; hohle sind am besten
- **Warum:** Windspiele nehmen Chi auf und bremsen es.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C10` · Profil: `windspiel_ueber_bett`</sub>

### KS-17 · Kleine Dinge gruppieren  (klein, ⚪ Tipp)
- **WENN** kleine Objekte stehen verstreut
- **DANN** in Gruppen oder einer Vitrine zusammenfassen, mit freiem Raum drumherum; große Stücke allein stellen
- **Warum:** Verstreutes wirkt zufällig.
- <sub>Räume: alle Räume</sub>

### KS-18 · Bilder aufhängen  (klein, 🟢 Grundriss (automatisch))
- **WENN** Bilder werden aufgehängt
- **DANN** kleine Bilder über Möbel oder als Gruppe mit einem Hauptbild; Augenhöhe; große Bilder mittig über niedrige Möbel; über zu hohe Möbel nichts hängen
- <sub>Räume: alle Räume · Prüfung: `grundriss:H07`</sub>

### KS-19 · Größe und Form  (klein, ⚪ Tipp)
- **WENN** ein Raum soll größer, höher oder breiter wirken
- **DANN** größere Kunst = mehr Weite; hochformatige Bilder = höhere Decke; querformatige = breiterer Raum; runde Objekte symmetrisch zentrieren
- <sub>Räume: alle Räume</sub>

### KS-20 · Farbe über Objekte  (klein, ⚪ Tipp)
- **WENN** du traust dich nicht an farbige Wände
- **DANN** Farbe über Kunst, Skulpturen, Decken – mit Zurückhaltung und Kontrast
- <sub>Räume: alle Räume</sub>

## 5 Styling – Spiegel und Kristalle

### SP-01 · Spiegel wie Türen  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel wird aufgehängt
- **DANN** nicht dorthin, wo keine Bewegung sein soll (vor allem ums Bett, nie ans Fußende)
- **Warum:** Spiegel sind keine Bilder, sie verhalten sich wie Fenster und Türen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C02`</sub>

### SP-02 · Nur Gutes verdoppeln  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel zeigt etwas Unschönes (Herd, WC, Tür, TV)
- **DANN** Spiegel so ausrichten, dass sie Schönes zeigen
- **Warum:** Spiegel verdoppeln alles, was sie zeigen.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C09`, `grundriss:KU4`, `grundriss:BA5`</sub>

### SP-03 · Fehlende Ecke  (klein, ⚪ Tipp)
- **WENN** dem Raum fehlt eine Ecke (L-Form)
- **DANN** Spiegel ergänzt die Raumform (nicht im Schlafzimmer)
- <sub>Räume: wohnzimmer, esszimmer, buero, flur</sub>

### SP-04 · Bildschirme wie Spiegel  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein schwarzer Bildschirm spiegelt
- **DANN** wie einen Spiegel behandeln
- <sub>Räume: alle Räume · Prüfung: `grundriss:C04`</sub>

### SP-05 · Wo Spiegel gut sind  (klein, ⚪ Tipp)
- **WENN** du suchst einen Platz für einen Spiegel
- **DANN** Wohnzimmer, Esszimmer (gedeckter Tisch), ungeschützter Arbeitsplatz (Tür sehen), abgestandene Räume
- <sub>Räume: alle Räume</sub>

### SP-06 · Wo Spiegel schlecht sind  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel hängt im Schlafzimmer, außen, im langen Flur (frontal) oder in der Küche
- **DANN** dort vermeiden
- <sub>Räume: alle Räume · Prüfung: `grundriss:C02`, `grundriss:KU4`</sub>

### SP-07 · Qualität  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** der Spiegel ist geteilt (Spiegelfliesen), gesprungen oder verzerrt
- **DANN** regelmäßige Form, ganze Person ohne Lücken, sauber, unverzerrt, nicht geteilt
- <sub>Räume: alle Räume · Profil: `spiegel_mangelhaft`</sub>

### SP-08 · Höhe  (klein, ⚪ Tipp)
- **WENN** der Spiegel hängt zu hoch oder zu tief
- **DANN** Gesicht muss gut sichtbar sein
- **Warum:** Zu hoch macht haltlos, zu tief lässt dich bücken.
- <sub>Räume: alle Räume</sub>

### SP-09 · Nicht hinter dir  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Spiegel hängt hinter deinem Sitzplatz
- **DANN** nicht hinter dich
- **Warum:** Man fühlt sich beobachtet.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C02`</sub>

### SP-10 · Kristalle  (klein, ⚪ Tipp)
- **WENN** ein Ort hat zu viel oder zu wenig Chi
- **DANN** klare, saubere Kristalle bei zu viel Chi (Tür auf Treppe/Bett) oder in stagnierenden Räumen; Jade für Holz
- **Warum:** Kristalle brechen Licht; ihre Kraft liegt in deiner Wahrnehmung.
- <sub>Räume: alle Räume</sub>

## 5 Styling – Wasser

### WA-01 · Bewegtes Wasser  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** Wasser steht still
- **DANN** Wasser immer bewegt und sauber halten
- **Warum:** Stehendes Wasser steht für Verfall (Schimmel, Mücken).
- <sub>Räume: alle Räume · Profil: `wasser_stehend`</sub>

### WA-02 · Kein Wasser über dir  (klein, ⚪ Tipp)
- **WENN** Wasser befindet sich über dir
- **DANN** Wasser nicht 'über' dir
- **Warum:** Wasser oben bedeutet Lecks und Überschwemmung.
- <sub>Räume: alle Räume</sub>

### WA-03 · Wasser im Büro, nicht im Schlafzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** ein Wasserobjekt wird aufgestellt
- **DANN** gut fürs Arbeiten (Wohlstand); nie ins Schlafzimmer
- **Warum:** Im Schlafzimmer bringt Wasser zu viel Energie.
- <sub>Räume: alle Räume · Prüfung: `grundriss:C06`, `foto:F11`</sub>

### WA-04 · Aquarium pflegen  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** ein Aquarium wird gehalten
- **DANN** gesund und sauber halten
- <sub>Räume: alle Räume · Profil: `aquarium_ungepflegt`</sub>

### WA-05 · Ersatz für Wasser  (klein, ⚪ Tipp)
- **WENN** es gibt kein Wasser im Raum
- **DANN** Pflanzen, glänzend-blaue Keramik oder ruhige Wasserbilder (keine stürmische See)
- <sub>Räume: alle Räume</sub>

## 5 Styling – Pflanzen

### PF-01 · Pflege  (wichtig, 🟣 Profil (aus deinen Angaben))
- **WENN** Pflanzen werden nicht gepflegt
- **DANN** lieber keine Pflanze als eine tote
- **Warum:** Tote Pflanzen stehen für Verfall.
- <sub>Räume: alle Räume · Profil: `tote_pflanzen`</sub>

### PF-02 · Wofür Pflanzen  (klein, ⚪ Tipp)
- **WENN** der Raum hat spitze Wandecken, grelles Licht, dunkle Bereiche oder lange Flure
- **DANN** Pflanzen verdecken Ecken, mildern Fenster, beleben Yin-Bereiche und lange Flure
- <sub>Räume: alle Räume</sub>

### PF-03 · Pflanzen im Schlafzimmer  (mittel, 🟢 Grundriss (automatisch))
- **WENN** Pflanzen stehen im Schlafzimmer
- **DANN** möglichst keine; wenn doch, als Gruppe direkt ans Fenster, das Bett weit weg
- **Warum:** Pflanzen bringen Energie und konkurrieren nachts um Sauerstoff.
- <sub>Räume: schlafzimmer, kinderzimmer, gaestezimmer, studio · Prüfung: `grundriss:C03`, `foto:F08`</sub>

### PF-04 · Pflanzen gruppieren  (klein, 🟢 Grundriss (automatisch))
- **WENN** Pflanzen sind im Raum verstreut
- **DANN** in Gruppen nahe den Fenstern
- <sub>Räume: wohnzimmer, esszimmer, studio · Prüfung: `grundriss:C03`</sub>

### PF-05 · Pflanzen in der Küche  (klein, ⚪ Tipp)
- **WENN** eine Pflanze steht neben dem Herd
- **DANN** nicht direkt an den Herd
- **Warum:** Holz nährt Feuer.
- <sub>Räume: kueche, studio</sub>

### PF-06 · Pflanzen im Bad  (klein, ⚪ Tipp)
- **WENN** ein Bad ohne Fenster hat Pflanzen
- **DANN** Pflanzen nur in Bädern mit Fenster
- <sub>Räume: bad</sub>

### PF-07 · Beste Pflanzen  (klein, ⚪ Tipp)
- **WENN** Pflanzen werden ausgesucht
- **DANN** große, weiche, runde Blätter (Monstera, Geldbaum, Peperomia), Farne, rundblättrige Sukkulenten; die vier Edlen (Orchidee, Bambus, Chrysantheme, Pflaumenblüte)
- <sub>Räume: alle Räume</sub>

### PF-08 · Kakteen  (mittel, 🔵 Foto (automatisch))
- **WENN** ein Kaktus steht in der Wohnung
- **DANN** Kakteen nach draußen
- **Warum:** Stacheln wirken aggressiv und stehen für unwirtliches Klima.
- <sub>Räume: alle Räume · Prüfung: `foto:F08` · Profil: `pflanzenarten enthaelt kaktus`</sub>

### PF-09 · Spitze Pflanzen  (klein, 🟣 Profil (aus deinen Angaben))
- **WENN** Pflanzen mit spitzen Blättern (Bogenhanf, Aloe, aufrechte Palmen) stehen in ruhigen Räumen
- **DANN** als Feuer behandeln: nur in energiereiche Räume
- <sub>Räume: alle Räume · Profil: `pflanzenarten enthaelt_eines ['bogenhanf', 'aloe vera', 'palme', 'dracaena']`</sub>

### PF-10 · Keine Kunstpflanzen  (mittel, 🟣 Profil (aus deinen Angaben))
- **WENN** Kunstpflanzen stehen im Raum
- **DANN** vermeiden; lieber Mobile, Skulpturleuchte oder volle Obstschale
- **Warum:** Sie erneuern sich nicht und sammeln Staub.
- <sub>Räume: alle Räume · Profil: `kunstpflanzen`</sub>

### PF-11 · Nicht grün streichen als Ersatz  (klein, ⚪ Tipp)
- **WENN** etwas wird grün gestrichen, um Pflanzen zu ersetzen
- **DANN** lieber lebendige Alternativen
- **Warum:** Wirkt künstlich.
- <sub>Räume: alle Räume</sub>

## 5 Styling – Garten und Balkon

### GB-01 · Garten als Raum  (klein, ⚪ Tipp)
- **WENN** ein Garten wird gestaltet
- **DANN** Mittelpunkt (Brunnen, Bank, Lichtung), Wege drumherum, Sitzplätze in Kommandoposition, hohe Pflanzen hinten
- <sub>Räume: garten</sub>

### GB-02 · Wasser vorne  (klein, ⚪ Tipp)
- **WENN** ein Wasserobjekt kommt in den Garten
- **DANN** vor das Haus, nicht dahinter
- <sub>Räume: garten</sub>

### GB-03 · Gebogene Wege  (klein, ⚪ Tipp)
- **WENN** ein Weg führt gerade auf die Tür zu
- **DANN** sanft gebogene Wege; vor langer Einfahrt ein Kreisel/Pflanzkübel
- **Warum:** Gerade Wege lassen aggressives Chi hereinrauschen.
- <sub>Räume: garten</sub>

### GB-04 · Balkon nutzen  (wichtig, 🟢 Grundriss (automatisch))
- **WENN** der Balkon ist kahl oder der Zugang zugestellt
- **DANN** Balkon begrünen und nutzen; Zugang nie verstellen; um die Möbel herumgehen können
- **Warum:** Den Zugang zu verschließen macht die Raumwirkung nur schlimmer.
- <sub>Räume: balkon, wohnzimmer, schlafzimmer · Prüfung: `grundriss:S03`</sub>

### GB-05 · Aussicht  (klein, 🟢 Grundriss (automatisch))
- **WENN** die Aussicht ist schön bzw. unschön
- **DANN** schöne Aussicht nicht verdecken (niedrige Pflanzen, hohe seitlich); unschöne mit üppigen Pflanzen weicher machen, aber nicht zubauen
- **Warum:** Man braucht das Licht.
- <sub>Räume: alle Räume · Prüfung: `grundriss:S03`</sub>

### GB-06 · Ohne Außenbereich  (klein, ⚪ Tipp)
- **WENN** die Wohnung hat keinen Balkon
- **DANN** Bank oder Liege ans Fenster; Pflanzen auf Fensterbänke oder nahe ans Fenster
- **Warum:** So entsteht Naturverbindung.
- <sub>Räume: alle Räume</sub>

## Anhang: Automatische Prüfungen im Code

| ID | Kategorie | Gewicht | Prüfung | Buchregeln |
|---|---|---|---|---|
| H01 | hart | 10.0 | **Keine Überlappung** | OR-04 |
| H02 | hart | 10.0 | **Alles im Raum** | OR-04 |
| H03 | hart | 8.0 | **Türen gehen frei auf** | EI-17, OR-04 |
| H04 | hart | 6.0 | **Laufwege frei (≥ 60 cm)** | EI-17, BU-15, BA-14, OR-04 |
| H05 | hart | 6.0 | **Platz für den Schreibtischstuhl** | BU-15 |
| H06 | hart | 4.0 | **Schränke zugänglich** | OR-06 |
| H07 | hart | 6.0 | **Wandobjekte nicht auf Türen/Fenstern** | KS-18 |
| K01 | kommando | 3.0 | **Schildkröte: feste Wand im Rücken** | GL-14, AN-01, AN-04, WZ-06, WZ-10, BU-04, SZ-19, SZ-58 |
| K02 | kommando | 2.5 | **Kein Fenster im Rücken** | AN-02, WZ-24, BU-14, SZ-20 |
| K03 | kommando | 3.0 | **Tür im Blick** | AN-01, AN-03, AN-04, WZ-06, BU-04, BU-22, BU-24, SZ-23, SZ-56, SZ-58 |
| K04 | kommando | 3.0 | **Füße nicht zur Tür (Sargposition)** | SZ-28, SZ-30 |
| K05 | chi | 1.0 | **Füße nicht zum großen Fenster** | SZ-29 |
| K06 | chi | 2.0 | **Abstand zur Tür** | AN-04, BU-13, SZ-31, GR-06 |
| K07 | kommando | 1.5 | **Bett nicht an der Türwand** | SZ-24 |
| K08 | chi | 2.5 | **Keine Balken / Schweres über dir** | GL-08, AN-05, WZ-06, BU-12, SZ-33 |
| K09 | chi | 2.0 | **Dachschräge: Kopf auf der hohen Seite** | WZ-11, SZ-34 |
| K10 | kommando | 1.5 | **Bett von beiden Seiten zugänglich** | SZ-25, SZ-27 |
| K11 | kommando | 1.0 | **Kinderbett mit Längsseite an der Wand** | SZ-55 |
| K12 | kommando | 1.5 | **Vogel: Freiraum vor dir** | GL-15, AN-01, BU-23, SZ-22 |
| K13 | kommando | 1.0 | **Schreibtisch: Fenster seitlich** | BU-14 |
| K14 | chi | 1.5 | **Keine spitzen Ecken auf dich gerichtet** | GL-08, AN-06, EI-18, SZ-05, SZ-45 |
| K15 | chi | 1.0 | **Langer Raum: Möbel quer stellen** | GL-09, WZ-22, SZ-60, SZ-48 |
| K16 | stil | 0.6 | **Bett zentral & symmetrisch** | SZ-02 |
| C01 | chi | 2.0 | **Nicht in der Chi-Bahn Tür ↔ Fenster** | GL-09, GL-11, AN-06, WZ-06, WZ-24, BU-24, SZ-50 |
| C02 | chi | 2.0 | **Spiegel richtig platzieren** | EI-13, SZ-32, SZ-44, SP-01, SP-06, SP-09 |
| C03 | stil | 1.0 | **Pflanzen: Licht ja, Bett nein** | SZ-12, PF-03, PF-04 |
| C04 | zonen | 1.5 | **Keine Bildschirme im Schlafzimmer** | SZ-03, SZ-10, SP-04 |
| C05 | zonen | 1.5 | **Zonen: Arbeiten vorn, Schlafen hinten** | BU-02, SZ-03, SZ-43, GR-01, GR-02, GR-07 |
| C06 | zonen | 1.0 | **Kein Wasser/Aquarium/Drache im Schlafzimmer** | SZ-12, KS-08, WA-03 |
| C07 | chi | 0.6 | **Altbau: Bett nicht an die Außenwand** | SZ-39 |
| S01 | stil | 2.0 | **Nichts Schweres über dem Kopfteil** | BU-16, SZ-36, SZ-37 |
| S02 | stil | 0.8 | **Untere-Drittel-Regel** | BU-18, SZ-57, EI5-03 |
| S03 | chi | 1.5 | **Fenster & Ausblick nicht verstellen** | GB-04, GB-05 |
| S04 | kommando | 2.0 | **Esstisch frei in der Raummitte** | EZ-03 |
| S05 | stil | 1.0 | **Fernseher nicht als Mittelpunkt** | WZ-16 |
| S06 | stil | 1.2 | **Sitzkreis statt einsamer Stuhl** | WZ-02, WZ-13 |
| S07 | stil | 0.8 | **Fernseher vom Sofa sichtbar, aber dezent** | WZ-16 |
| L01 | chi | 1.5 | **Keine Hängeleuchte über Bett oder Sitzplatz** | AN-05, WZ-20, BU-12, SZ-35 |
| L02 | stil | 1.0 | **Pendelleuchte über dem Tisch** | WZ-20, EZ-05, EZ-23, GR-03, LI-08 |
| L03 | stil | 0.8 | **Drei von vier Ecken beleuchten** | WZ-19, LI-04, LI-05 |
| E01 | stil | 0.6 | **Esstisch: rund ist am besten** | EZ-12 |
| E02 | stil | 0.8 | **Gerade Anzahl gleicher Stühle** | EZ-15, EZ-16, EZ-18 |
| E03 | stil | 0.6 | **Nur Tisch und Stühle in der Mitte** | EZ-19 |
| E04 | chi | 1.2 | **Esstisch nicht im Eingang** | EI-23, EZ-10 |
| E05 | stil | 0.6 | **Spiegel spiegelt den Esstisch** | EZ-06 |
| E06 | stil | 0.6 | **Keine Uhr im Ess- und Schlafzimmer** | EZ-09, KS-02 |
| G01 | zonen | 1.5 | **Geteiltes Zimmer: gleiche Betten mit Abstand** | SZ-51, SZ-53 |
| G02 | zonen | 1.2 | **Nicht die Füße zum Kopf des anderen** | SZ-51 |
| G03 | stil | 0.5 | **Kein Etagenbett** | SZ-52 |
| ST1 | zonen | 2.0 | **Studio: Schichten von ruhig nach aktiv** | KU-04, GR-02, GR-08 |
| KU1 | kommando | 2.0 | **Herd in der Kommandoposition** | EI-22, EI-25, KU-02, KU-15 |
| KU2 | chi | 1.5 | **Feuer und Wasser trennen** | KU-07, KU-08, KU-19 |
| KU3 | chi | 1.0 | **Herd nicht unter dem Fenster** | KU-17 |
| KU4 | chi | 1.0 | **Keine Spiegel in der Küche** | KU-05, KU-13, SP-02, SP-06 |
| BA1 | kommando | 2.0 | **WC nicht in Sicht- und Türlinie** | EI-25, BA-05, BA-09 |
| BA2 | zonen | 1.2 | **WC weg von der Badewanne** | BA-10 |
| BA3 | kommando | 1.0 | **Badewanne: Blickfang, Füße nicht zur Tür** | BA-12 |
| BA4 | kommando | 0.8 | **Waschbecken: Rücken nicht zur Tür** | BA-13 |
| BA5 | stil | 0.8 | **Kein Spiegel auf das WC** | BA-04, SP-02 |
| C08 | chi | 2.0 | **Tür und Fenster auf verschiedenen Wänden** | GL-10, EZ-22, KU-06, KU-23, BU-03, SZ-07 |
| C09 | chi | 1.2 | **Spiegel spiegelt keine Tür und keinen Fernseher** | WZ-05, EZ-06, SP-02 |
| C10 | chi | 1.0 | **Kein Windspiel oder Mobile über Bett und Schreibtisch** | KS-16 |
| C11 | zonen | 0.8 | **Religiöse Objekte am richtigen Ort** | KS-13 |
| K17 | kommando | 0.8 | **Nachttische als ausgewogenes Paar** | GL-16, SZ-26, SZ-45 |
| W01 | stil | 1.0 | **Zwei Sofas gegenüber brauchen einen Tisch** | WZ-08 |
| W02 | stil | 0.8 | **Couchtisch als Anker** | WZ-14 |
| W03 | stil | 0.5 | **Sofa nicht allein** | WZ-12 |
| B01 | stil | 0.5 | **Bücher in Reichweite des Arbeitsplatzes** | BU-19 |
| B02 | zonen | 0.8 | **Geteiltes Büro: gleich große Tische** | BU-25 |
| B03 | kommando | 0.6 | **Tagesbett im Büro nicht zur Tür** | BU-21 |
| KU5 | chi | 1.0 | **Ofen nicht auf Sitzplätze richten** | KU-16 |
| E07 | stil | 0.5 | **Keine lange Bank am Esstisch** | EZ-21 |
| S08 | stil | 0.6 | **Erster Eindruck: Hauptmöbel verankert den Blick** | EI5-01 |
| S09 | stil | 1.0 | **Kein Fernseher über dem Kamin** | WZ-17 |
| T01 | zonen | 0.8 | **Tierkäfige an den richtigen Ort** | GR-09 |
| T02 | kommando | 0.5 | **Haustiere sehen die Tür** | GR-10 |
| T03 | zonen | 0.5 | **Futter und Katzenklo getrennt** | GR-11 |
