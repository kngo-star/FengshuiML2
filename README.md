# FengshuiML2 – Feng-Shui-Zimmerplaner

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kngo-star/FengshuiML2/blob/main/fengshui_colab.ipynb)

Regelbasis + Optimierer + Machine Learning + YOLO-Fotoanalyse

Python-Projekt für PyCharm, das dein Zimmer automatisch nach den Feng-Shui-Regeln aus dem Buch
einrichtet (Form-Schule: Kommandoposition, Chi-Fluss, fünf Elemente).

## ▶ Am einfachsten: nur ein Foto reinlegen (`start.py`)

1. In PyCharm: Rechtsklick auf **`start.py`** → **Run 'start'** (einmal starten, läuft dann weiter).
2. Der Ordner **`fotos_rein`** öffnet sich – Foto(s) deines Zimmers hineinziehen (`.jpg`, `.png`, iPhone-`.heic`).
3. Fertig: In **`fotos_raus`** erscheinen pro Foto `…_korrigiert.jpg`, `…_aenderungen.jpg`,
   `…_vorher_nachher.png` (öffnet sich automatisch) und `…_bericht.txt`.

Der Raumtyp (Schlafzimmer, Wohnzimmer, Büro, Küche, Bad …) wird **automatisch erkannt**.
Fotos bleiben auf deinem Computer – `fotos_rein/` und `fotos_raus/` werden nicht zu GitHub hochgeladen.

## In Google Colab nutzen (ohne Installation)

Oben auf **Open in Colab** klicken und die Zellen von oben nach unten ausführen.
Das Notebook holt den Code automatisch aus diesem Repo (`QUELLE = "github"`).

## Installation in PyCharm

1. Ordner `fengshui_zimmer` entpacken → in PyCharm **File → Open** → Ordner wählen.
2. Python-Interpreter einrichten (Python ≥ 3.10): **Settings → Project → Python Interpreter**.
3. Im PyCharm-Terminal: `pip install -r requirements.txt` (matplotlib + numpy).

## Benutzung

| Schritt | Datei | Was passiert |
|---|---|---|
| 1 | `mein_zimmer.py` | Maße, Türen, Fenster, Balken, Dachschräge, Möbel und dein Profil eintragen |
| 2 | `main.py` → Run | Optimierer sucht die besten Anordnungen, druckt Bewertung und Hinweise, speichert Grundrisse in `ausgabe/` |
| 3 | `lernen.py` → Run | **Machine Learning:** du bewertest Vorschläge mit 0–10, das Modell lernt, welche Regeln dir wichtig sind |
| 4 | `main.py` erneut | nutzt jetzt automatisch deine gelernten Gewichte (`meine_bewertungen.json`) |
| 🪄 | `foto_korrigieren.py` → Run | **Foto rein → dasselbe Foto mit korrigierten Möbeln raus** (nur Problem-Möbel werden minimal verschoben) |
| ✨ | `zimmer_aus_foto.py` → Run | **Zimmer aus einem Foto vermessen** – keine Meter eintippen: Raummaße, Tür/Fenster, Möbelpositionen → Bewertung + Optimierung |
| 📷 | `foto_empfehlung.py` → Run | **Foto deines Zimmers** → YOLO erkennt Möbel → Feng-Shui-Empfehlungen + Möbelliste für den Optimierer |
| ⬆ | `push.py` → Run | Änderungen mit GitHub synchronisieren: holt erst die Änderungen deines Teams, dann Commit + Push |
| – | `regeln_exportieren.py` | schreibt die gesamte Regelbasis als `regelbasis.md` / `regelbasis.json` |

Deine **aktuelle** Einrichtung bewerten: in `mein_zimmer.py` bei den Möbeln `x`, `y`, `rot` angeben –
`main.py` bewertet sie dann zuerst. Möbel, die nicht bewegt werden dürfen: `fest=True`.

## Koordinaten

```
(0,tiefe) ┌──── oben ────┐
          links        rechts      rot = Blickrichtung / Vorderseite:
(0,0)     └──── unten ───┘ (breite,0)   0=oben  90=rechts  180=unten  270=links
```
Bett: Vorderseite = Fußende, `tiefe` = Bettlänge. Schreibtisch: Richtung, in die du beim Sitzen schaust.
Nachttische/Couchtisch/Bank hängen mit `gehoert_zu` + `seite` am Hauptmöbel und wandern mit.

## Aufbau

```
fengshui/
  modell.py        Raum, Oeffnung, Balken, Schraege, Moebel, Bewohner, Layout
  geometrie.py     Abstände, Sichtwinkel, Türflucht, Chi-Bahnen, Laufweg-Suche (Raster + BFS)
  regeln.py        REGELBASIS: 37 prüfbare Regeln (hart / kommando / chi / zonen / stil)
  wissen.py        Wissensbasis: 5 Elemente + Zyklen, Himmelsrichtungen, Raumprofile, Licht (Kelvin),
                   Pflanzen, Spiegel, Stauraum, Symbol-Objekte, Möbelformen
  ausstattung.py   Check für Farben, Licht, Bett, Pflanzen, Ordnung (aus dem PROFIL-Dict)
  bewertung.py     Score 0–100 + Bericht
  optimierer.py    Simulated Annealing + Hill-Climbing, mehrere Neustarts, verschiedene Varianten
  ml.py            Personalisierung: nicht-negative Ridge-Regression lernt Regelgewichte aus deinen Noten;
                   exportiere_datensatz() erzeugt CSV-Trainingsdaten für eigene Modelle
  visualisierung.py Grundriss mit Türaufschlag, Chi-Bahnen (orange), Balken, Personenpunkt (grün)
```

## Wie die Regelbasis rechnet

Jede Regel liefert Strafen 0…1. Harte Regeln (Überlappung, Tür geht auf, 60-cm-Laufwege, Stuhlplatz …)
müssen erfüllt sein. Weiche Regeln werden gewichtet: `Score = 100 / (1 + Σ Gewicht·Strafe / 5)`.
Eine eigene Regel ergänzt du so:

```python
@regel("X01", "Mein Titel", "Beschreibung", "Quelle", "stil", 1.0, raumtypen={"schlafzimmer"})
def _x01(layout):
    return [Befund(0.5, "Text", "Möbelname")]  # leere Liste = Regel erfüllt
```

## Wichtigste Regeln (Auszug)

- **Kommandoposition:** feste Wand im Rücken, Tür im Blick, nicht in Linie mit der Tür, kein Fenster im Rücken
- **Bett:** Füße nie zur Tür, nicht an der Türwand, nicht unter Balken/Schräge, beidseitig zugänglich (Paare),
  keine Spiegel/Regale/schweren Bilder in Bettnähe, quer im langen Raum, weg von Pflanzen
- **Schreibtisch:** Fenster seitlich, Rücken nie zur Tür, nicht direkt an der Tür, im Zimmer näher zur Tür als das Bett
- **Chi:** Bett/Sofa/Schreibtisch nicht in der Bahn Tür↔Fenster; keine spitzen Möbelecken auf dich gerichtet
- **Stil:** untere Drittel = Stauraum, keine hohen offenen Regale, Fenster nicht zustellen, Sitzkreis im Wohnzimmer

Das Buch betont selbst: Fühlt sich eine Regel falsch an, folge deinem Gefühl – genau dafür ist `lernen.py` da.

## Foto-Analyse mit YOLO (`foto_empfehlung.py`)

1. Foto als `mein_zimmer.jpg` in den Projektordner legen (oder Pfad oben in `FOTO` eintragen), `RAUMTYP` setzen.
2. Run. Beim ersten Start lädt ultralytics das Modell (YOLOE, ~30 MB + Text-Encoder) automatisch.
3. Ergebnis: Hinweise in der Konsole, `ausgabe/foto_erkennung.jpg` (Boxen), `ausgabe/erkennungen.json`
   und eine fertige `Moebel(...)`-Liste zum Kopieren in `mein_zimmer.py`.
4. Mit `OPTIMIEREN = True` (bzw. `--optimieren`) wird die erkannte Möbelliste direkt mit den Raummaßen aus
   `mein_zimmer.py` optimiert.

Modell: Standard ist **YOLOE** mit Text-Prompts (erkennt auch Schrank, Spiegel, Fenster, Tür, Nachttisch, Wandregal).
Alternativen: `yolov8s-world.pt` (YOLO-World) oder `yolo11n.pt` (nur 80 COCO-Klassen – kein Schrank/Spiegel/Fenster).
Eigene Begriffe ergänzt du in `fengshui/foto.py` → `WORLD_KLASSEN`.

Foto-Regeln F01–F19: Elektronik im Schlafzimmer, Spiegel am Bett, Regal/Bild/Leuchte über dem Bett,
Fenster hinter dem Bett, Tür in Bettlinie, Pflanzen (Bett/Licht/Kaktus), Unordnung & untere-Drittel-Regel,
Uhr, Aquarium, Schreibtisch vor dem Fenster, Nachttisch-Paar, hohe offene Regale, Anzahl Lampen,
mehrere Schränke, Sitzkreis/Couchtisch/TV im Wohnzimmer, gerade Stuhlanzahl.

**Grenzen:** Ein Foto ist 2D – Abstände, Blickwinkel zur Tür und die Chi-Bahn lassen sich nur schätzen.
Die Hinweise sind deshalb als „bitte prüfen" formuliert; die genaue Prüfung macht der Grundriss-Teil.
Tipp: Aus der Tür heraus mit Weitwinkel fotografieren, Raum hell. Mehrere Fotos (je eine Wand) liefern mehr.

## ✨ Zimmer aus einem Foto vermessen (`zimmer_aus_foto.py`, Colab-Schritt 3A)

Keine Meter-Eingabe nötig: **YOLOE** findet Möbel, Türen und Fenster (mit Umrissmasken),
**Depth Anything V2 – Metric Indoor** schätzt für jedes Pixel die Entfernung in Metern.
`fengshui/foto3d.py` macht daraus:

1. 3D-Punktwolke (Brennweite aus den EXIF-Daten des Fotos)
2. Boden per RANSAC → Kamerahöhe und Höhen aller Punkte
3. Wände: Ausrichtung + Wandlinien → **Raumbreite und -tiefe**
4. Möbel: Grundfläche, Höhe, Wand im Rücken; Türen/Fenster mit Position, Breite, Brüstung
5. Maßstab-Check über die Türhöhe (2,0 m); optional eine bekannte Länge angeben (`--breite 3.6`)
6. Ergebnis wird als `mein_zimmer.py` geschrieben → `main.py` bewertet deine **jetzige** Einrichtung und optimiert

**Foto-Tipps:** aus einer Zimmerecke diagonal in die gegenüberliegende Ecke, Weitwinkel (0,5×),
Brusthöhe, Handy gerade, Raum hell, Boden + mindestens zwei Wände sichtbar.

**Genauigkeit:** im Test an einem gerenderten Zimmer (3,60 × 4,20 m) lagen Raummaße und Möbel
bei ±5–10 cm; mit echten Fotos ist ±10–20 cm realistisch. Wände hinter der Kamera werden geschätzt,
verdeckte Möbelrückseiten mit Standardmaßen ergänzt – Ergebnis kurz prüfen und bei Bedarf korrigieren.

## 🪄 Dasselbe Foto mit korrigierten Möbeln (`foto_korrigieren.py`, Colab-Schritt 3B)

1. Foto vermessen (siehe oben) → Raum, Möbel, Masken, Kamera
2. **Minimal-Korrektur** (`optimierer.korrigiere`): Start bei deiner jetzigen Einrichtung; jedes Möbel wird
   systematisch an jeder Wand/Position getestet, dann Feinschliff per Simulated Annealing. Verschieben kostet
   Punkte pro Meter, Drehen kostet extra → nur Möbel mit echten Problemen werden bewegt.
3. **Foto bearbeiten** (`fengshui/foto_korrektur.py`): Möbel ausschneiden, Lücke mit **LaMa** füllen,
   Ausschnitt perspektivisch skaliert an die neue Bodenposition setzen, Verdeckungen nachbilden.
4. Ausgabe: `foto_korrigiert.jpg`, `foto_aenderungen.jpg` (rot = jetzt, grün = neu, Pfeile, Nummern),
   `foto_vorher_nachher.png` mit Begründung je Änderung.

**Grenzen:** Das verschobene Möbel behält die Ansicht aus dem Originalfoto (bei großen Wegen sieht man die
Perspektive). Gedrehte Möbel werden nur als 3D-Umriss gezeigt. Vom Bildrand abgeschnittene Möbel bleiben stehen.

## Neue Regeln (Version 2)
Licht (L01–L03), Esszimmer (E01–E06), geteiltes Schlafzimmer (G01–G03), Studio-Schichten (ST1),
**Küche** (KU1–KU4, Raumtyp `kueche`) und **Bad** (BA1–BA5, Raumtyp `bad`) – insgesamt jetzt 59 Regeln.
Neue Möbeltypen: `stuhl` (mit `gehoert_zu="Esstisch"` automatisch um den Tisch verteilt), `stehleuchte`,
`tischleuchte`, `pendelleuchte`, `herd`, `spuele`, `kuehlschrank`, `wc`, `badewanne`, `dusche`,
`waschbecken`, `etagenbett`.

## Ausführliche Analyse mit Begründung (Version 3)
Jedes Ergebnis enthält jetzt (`…_bericht.txt` und Vorher/Nachher-Grafik):
- **Was nicht gut ist – und warum**: jede Regel mit der Begründung aus dem Buch (Kommandoposition, Chi,
  Sha-Chi durch spitze Ecken, Spiegel wie Türen …) und **Abhilfe**, falls du nicht umstellen kannst
  (`fengshui/erklaerungen.py`).
- **Was schon gut ist** und **was sich nicht prüfen ließ** (z. B. keine Tür im Foto).
- **Grundriss von oben**: alt (rot gestrichelt) → neu, mit Kamerastandort.
- Neue Positionen nur im **sichtbaren** Teil des Raums (hinter der Kamera könnten Möbel oder Türen sein).
- Gedrehte Möbel: alte Stelle wird entfernt, neue Stelle als grüne 3D-Box „hierhin (gedreht)“.
- Runde Tische werden an ihrer Form erkannt (keine falschen „spitzen Ecken“).

## 📖 Regelbasis aus dem Buch (Version 4) – `fengshui/buchregeln.py`

Das ganze Buch ist jetzt als **Wissensbasis aus WENN-DANN-Regeln** erfasst (322 Regeln, alle Kapitel:
Grundlagen, Anwendung, Wohnung wählen, Eingang, Wohnzimmer, Esszimmer, Küche, Büro, Schlafzimmer, Bad,
gemeinsame Räume, Eindruck, Ordnung, Licht, Farben, Kunst & Objekte, Spiegel & Kristalle, Wasser, Pflanzen,
Garten & Balkon). Jede Regel hat:

| Feld | Bedeutung |
|---|---|
| `wenn` / `dann` | Situation → Empfehlung |
| `warum` / `abhilfe` | Begründung aus dem Buch / was tun, wenn man nicht umstellen kann |
| `prio` | 1 wichtig · 2 mittel · 3 klein |
| `raeume`, `objekte` | wofür die Regel gilt |
| `pruefung` | automatische Prüfung: `grundriss:K04` (Geometrie, 77 Prüfungen in `regeln.py`), `foto:F02` (YOLO) |
| `profil` | deklarative Bedingungen auf deinen Angaben, z. B. `("leuchtmittel", "==", "klar")` |

**219 Regeln werden automatisch geprüft** (Grundriss, Foto oder Profil), die übrigen erscheinen als Tipp-Checkliste
im Bericht. Der Bericht zeigt zu jedem Problem die Buchregel (WENN → DANN, Warum, Abhilfe, „Siehe auch“),
was schon gut ist, was sich nicht prüfen ließ und die passenden Tipps für den Raum.

`python regeln_exportieren.py` erzeugt **`regelbasis.md`** (lesbarer Katalog) und **`regelbasis.json`**
(maschinenlesbar – z. B. für ein Sprachmodell oder eigene ML-Experimente).
Neue Regel ergänzen: einen `R(...)`-Eintrag in `buchregeln.py` hinzufügen – fertig.

## ✅ Tests & Evaluation (Version 5)

| Datei | Run in PyCharm | Wofür |
|---|---|---|
| `tests_ausfuehren.py` | Run | **24 Tests**: Für die wichtigsten Regeln je ein Testzimmer, das laut Buch klar falsch ist, und eines, das klar richtig ist (Bett frei im Raum, Füße zur Tür, Rücken zur Tür, Fenster im Rücken, Spiegel aufs Bett …). Dazu: alle Regeln stürzen nie ab und liefern Strafen 0…1, alle Verweise der Buch-Regelbasis zeigen auf echte Prüfungen, der Optimierer schlägt den Zufall, die Korrektur macht keine Mini-Verschiebungen. |
| `auswertung.py` | Run (2–4 min) | Zahlen und Grafiken für den Bericht im Ordner `auswertung/`: Optimierer vs. Zufall, Minimal-Korrektur vorher/nachher, Simulationsstudie zum Präferenzlernen (virtuelle Testpersonen), Kreuzvalidierung eurer echten Bewertungen. |

**Keine „Gimmick“-Änderungen mehr:** Die Foto-Korrektur (`korrigiere()` in `optimierer.py`) verlangt jetzt
einen Grundpreis pro angefasstem Möbel, nimmt Verschiebungen unter 30 cm zurück (außer sie sind für eine harte Regel
nötig) und behält nur Änderungen, die für sich mindestens 3 Punkte bringen. Jede Änderung nennt die Regel, die sie löst.
Zusätzlich werden komplett neue gute Anordnungen geprüft und davon nur so viel übernommen, wie sich lohnt.
Behoben: Ein Fehler ließ die Korrektur manchmal eine höhere Punktzahl melden, obwohl nichts umgestellt wurde.

**Bewerten (`lernen.py`):** Es kommen nur noch Vorschläge, bei denen mindestens ein großes Möbel ≥ 1 m woanders
steht oder anders gedreht ist – halb gründlich optimiert, halb nur kurz (plausibel, aber mit Schwächen).

## 🗣️ Nutzer-Feedback → neue Regeln (Version 6)

Beim ersten Bewertungsbogen (Runde 1) hat Kevin 7 Vorschläge bewertet und kommentiert. Die Kommentare zeigten
Mängel, die die Regelbasis noch nicht kannte – daraus wurden neue Regeln in `fengshui/regeln.py`:

| Regel | Art | Kommentar aus Runde 1 |
|---|---|---|
| H08 Schränke stehen an der Wand | hart | „Kleiderschrank ist nicht an der Wand“ |
| H09 Spiegel und Bilder nicht verdecken | hart | „Kleiderschrank deckt den Spiegel“ |
| H10 Kein hohes Möbel vor dem Fenster | hart (verschärft S03) | „Kleiderschrank deckt Fenster“ |
| H11 Arbeitsplatz frei benutzbar | hart | „Schrank / Monstera blockiert den Schreibtisch“ |
| P01 Schreibtisch an einer Wand | weich, lernbar | „Schreibtisch ist nicht an der Wand“ (das Buch sieht das anders → das Modell lernt, wie wichtig es dir ist) |

Die Noten aus Runde 1 werden **nicht** fürs Training benutzt (`daten/runde1_antworten.json`), weil die Vorschläge
diese Mängel hatten. `lernen.py` erzeugt jetzt nur noch Vorschläge, die alle harten Regeln erfüllen: die Hälfte
optimal nach dem aktuellen Modell, die andere Hälfte optimal für einen zufällig veränderten „Geschmack“.
Ein Test (`test_runde1_feedback_wird_erkannt`) prüft, dass jeder kommentierte Mangel jetzt eine Regel verletzt.
