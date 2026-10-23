# FengshuiML2 – Feng-Shui-Zimmerplaner

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kngo-star/FengshuiML2/blob/main/fengshui_colab.ipynb)

Regelbasis + Optimierer + Machine Learning + YOLO-Fotoanalyse

Python-Projekt für PyCharm, das dein Zimmer automatisch nach den Feng-Shui-Regeln aus dem Buch
einrichtet (Form-Schule: Kommandoposition, Chi-Fluss, fünf Elemente).

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
| ✨ | `zimmer_aus_foto.py` → Run | **Zimmer aus einem Foto vermessen** – keine Meter eintippen: Raummaße, Tür/Fenster, Möbelpositionen → Bewertung + Optimierung |
| 📷 | `foto_empfehlung.py` → Run | **Foto deines Zimmers** → YOLO erkennt Möbel → Feng-Shui-Empfehlungen + Möbelliste für den Optimierer |
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
