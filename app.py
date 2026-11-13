"""
🌿 WEB-OBERFLÄCHE – alles per Mausklick im Browser.

In PyCharm: Rechtsklick auf app.py → Run 'app'. Der Browser öffnet sich von selbst
(sonst die Adresse aus der Konsole öffnen, meist http://127.0.0.1:7860).
Beenden: in PyCharm auf das rote Quadrat ■ klicken.

Zwei Bereiche:
  🛋 Leeres Zimmer einrichten   – Foto eines leeren Raums → Möbel + Deko im Foto, Grundriss, Einkaufsliste
  🪄 Zimmer verbessern          – Foto eines eingerichteten Raums → Score, was nicht gut ist, korrigiertes Foto

Fotos bleiben auf deinem Computer. Ausnahme: Wenn du unten TEILEN = True setzt, bekommst du einen
öffentlichen Link (72 Stunden gültig), über den andere die Seite benutzen können – ihre Fotos werden
dann auf DEINEM Computer gerechnet.

Benötigt:  pip install "gradio>=6"   (steht auch in requirements.txt)
"""
import os
import time
import traceback

import gradio as gr

HIER = os.path.dirname(os.path.abspath(__file__))
os.chdir(HIER)                                   # damit produkte.json, affiliate.json usw. gefunden werden
AUSGANG = os.path.join(HIER, "ausgabe", "app")
TEILEN = False                                   # True = öffentlicher Link für Freunde/Lehrperson (72 h)

from fengshui.einrichten import RAUMTYPEN, richte_foto_ein, zimmer_einrichten  # noqa: E402
from fengshui.ml import Personalisierung  # noqa: E402
from fengshui.modell import Bewohner  # noqa: E402

RAUM_NAMEN = {"schlafzimmer": "Schlafzimmer", "gaestezimmer": "Gästezimmer", "kinderzimmer": "Kinderzimmer",
              "wohnzimmer": "Wohnzimmer", "esszimmer": "Esszimmer", "buero": "Büro / Arbeitszimmer",
              "studio": "Studio (Schlafen + Wohnen)"}
RAUM_AUSWAHL = [(RAUM_NAMEN[r], r) for r in RAUMTYPEN]
STIL_AUSWAHL = [("Natur – Eiche, Beige", "natur"), ("Hell – Birke, Hellgrau", "hell"),
                ("Dunkel – Nussbaum, Anthrazit", "dunkel")]
BUDGET_AUSWAHL = [("günstig", "guenstig"), ("mittel", "mittel"), ("gehoben", "gehoben")]


def _ordner() -> str:
    o = os.path.join(AUSGANG, time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(o, exist_ok=True)
    return o


def _fehler(fehler: Exception) -> gr.Error:
    traceback.print_exc()                         # ganze Meldung steht in der PyCharm-Konsole
    text = str(fehler) or fehler.__class__.__name__
    if "Keine Möbel" in text:
        text += " → Für ein leeres Zimmer den Bereich „Leeres Zimmer einrichten“ benutzen."
    return gr.Error(f"Das hat nicht geklappt: {text}", duration=None)


# ====================================================================== 🛋 Leeres Zimmer einrichten
def einrichten_ui(foto, raumtyp, stil, budget, paar, pflanzen, breite, demo=False,
                  fortschritt=gr.Progress()):
    if not demo and not foto:
        raise gr.Error("Bitte zuerst ein Foto hochladen – oder „Demo-Zimmer ausprobieren“ klicken.")
    bewohner = Bewohner(paar=bool(paar), pflanzen_sind_freunde=bool(pflanzen))
    gewichte = Personalisierung().gewichte
    ordner = _ordner()
    try:
        if demo:
            from fengshui.demo_zimmer import demo_vermessung
            fortschritt(0.1, desc="Baue das Demo-Zimmer …")
            rgb, v, _ = demo_vermessung(raumtyp)
            fortschritt(0.3, desc="Wähle und stelle die Möbel nach der Regelbasis …")
            r = richte_foto_ein(rgb, v, raumtyp, stil, budget, bewohner, gewichte, ordner, f"demo_{raumtyp}",
                                ausgabe=False)
        else:
            fortschritt(0.05, desc="Vermesse das Zimmer (beim ersten Mal werden die KI-Modelle geladen) …")
            r = zimmer_einrichten(foto, raumtyp, stil, budget, ausgabe_ordner=ordner, bewohner=bewohner,
                                  gewichte=gewichte, bekannte_breite=breite or None, ausgabe=False)
    except gr.Error:
        raise
    except Exception as fehler:
        raise _fehler(fehler)

    e = r["einrichtung"]
    raum = e.layout.raum
    d = r["dateien"]
    kopf = (f"### {RAUM_NAMEN.get(raum.raumtyp, raum.raumtyp)} – Feng-Shui-Score **{e.ergebnis.score:.0f}/100**\n"
            f"Raum ca. {raum.breite:.1f} × {raum.tiefe:.1f} m · {len(e.positionen)} Produkte · "
            f"Richtpreis gesamt ca. **CHF {e.summe():,.0f}**".replace(",", "’"))
    if e.weggelassen:
        kopf += f"\n\nAus Platzgründen weggelassen: {', '.join(e.weggelassen)}."
    downloads = [d["einkaufsliste.html"], d["uebersicht.png"], d["eingerichtet.jpg"], d["grundriss.png"],
                 d["einkaufsliste.json"]]
    return (r["foto"], r["bild_nummern"], d["grundriss.png"], kopf, r["liste_html"], downloads)


def demo_ui(raumtyp, stil, budget, paar, pflanzen, fortschritt=gr.Progress()):
    return einrichten_ui(None, raumtyp, stil, budget, paar, pflanzen, None, demo=True, fortschritt=fortschritt)


# ====================================================================== 🪄 Zimmer verbessern
def verbessern_ui(foto, raumtyp, paar, breite, fortschritt=gr.Progress()):
    if not foto:
        raise gr.Error("Bitte zuerst ein Foto hochladen.")
    from fengshui.foto_korrektur import foto_korrigieren
    ordner = _ordner()
    try:
        fortschritt(0.05, desc="Erkenne Möbel und vermesse das Zimmer (beim ersten Mal: Modelle laden) …")
        r = foto_korrigieren(foto, raumtyp, ausgabe_ordner=ordner, bewohner=Bewohner(paar=bool(paar)),
                             gewichte=Personalisierung().gewichte, bekannte_breite=breite or None, zeigen=False)
    except Exception as fehler:
        raise _fehler(fehler)
    vorher, nachher = r["vorher"].score, r["nachher"].score
    kopf = (f"### {RAUM_NAMEN.get(r['raumtyp'], r['raumtyp'])} – Score **{vorher:.0f}** → **{nachher:.0f}**/100\n"
            + ("\n".join(f"- {z}" for z in r["legende"]) if r["legende"]
               else "Keine Änderung nötig – dein Zimmer passt schon gut."))
    d = r["dateien"]
    return (r["korrigiert"], r["erklaerung"], d["vorher_nachher"], kopf, r["analyse"].text(),
            [d["korrigiert"], d["aenderungen"], d["vorher_nachher"]])


# ====================================================================== Seite
CSS = """
.gradio-container {max-width: 1250px !important; margin: 0 auto;}
#kopf h1 {margin-bottom: 0;}
#kopf p {opacity: .8;}
.fsl {border-radius: 14px; overflow: hidden;}
.fsl a.knopf, .fsl a.knopf:visited {color: #fff !important; text-decoration: none !important;}
.fsl .mehr a {margin: 0 2px;}
#knopf-los {font-size: 17px;}
"""


THEMA = gr.themes.Soft(primary_hue="emerald", neutral_hue="stone",
                       font=["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Helvetica", "Arial", "sans-serif"])


def seite() -> gr.Blocks:
    with gr.Blocks(title="Feng-Shui-Zimmerplaner") as app:
        gr.Markdown("# 🌿 Feng-Shui-Zimmerplaner\nFoto hochladen, Raum wählen, klicken. Die Möbel werden nach "
                    "den Regeln der Form-Schule gestellt – jedes Produkt mit Begründung.", elem_id="kopf")

        with gr.Tab("🛋 Leeres Zimmer einrichten"):
            with gr.Row():
                with gr.Column(scale=1, min_width=320):
                    foto = gr.Image(type="filepath", label="Foto des leeren Zimmers", height=300,
                                    sources=["upload", "clipboard"])
                    raum = gr.Dropdown(RAUM_AUSWAHL, value="schlafzimmer", label="Was soll es werden?")
                    stil = gr.Radio(STIL_AUSWAHL, value="natur", label="Stil")
                    budget = gr.Radio(BUDGET_AUSWAHL, value="mittel", label="Budget")
                    with gr.Accordion("Mehr Einstellungen", open=False):
                        paar = gr.Checkbox(label="Zwei Personen im Bett (breiteres Bett)")
                        pflanzen = gr.Checkbox(label="Pflanzen im Schlafzimmer geben mir Ruhe")
                        breite = gr.Number(label="Raumbreite in m, falls bekannt (0 = unbekannt) – macht die Maße genauer",
                                           value=0, minimum=0, maximum=12)
                    los = gr.Button("✨ Zimmer einrichten", variant="primary", elem_id="knopf-los")
                    demo = gr.Button("Kein Foto? Demo-Zimmer ausprobieren")
                    gr.Markdown("**Tipp fürs Foto:** aus einer Ecke diagonal fotografieren, Weitwinkel 0,5×, "
                                "Brusthöhe. Boden und zwei Wände sollten zu sehen sein, am besten auch die Tür.")
                with gr.Column(scale=2):
                    kopf = gr.Markdown("Hier erscheint das Ergebnis.")
                    with gr.Row():
                        vorher_bild = gr.Image(label="Vorher", interactive=False, height=330)
                        nachher_bild = gr.Image(label="Nachher – Nummern = Einkaufsliste", interactive=False,
                                                height=330)
                    grundriss = gr.Image(label="Grundriss", interactive=False, height=420)
            liste = gr.HTML()
            dateien = gr.File(label="Herunterladen (die HTML-Datei kann man auch verschicken)",
                              file_count="multiple")
            aus = [vorher_bild, nachher_bild, grundriss, kopf, liste, dateien]
            los.click(einrichten_ui, [foto, raum, stil, budget, paar, pflanzen, breite], aus)
            demo.click(demo_ui, [raum, stil, budget, paar, pflanzen], aus)

        with gr.Tab("🪄 Zimmer verbessern"):
            with gr.Row():
                with gr.Column(scale=1, min_width=320):
                    foto2 = gr.Image(type="filepath", label="Foto deines eingerichteten Zimmers", height=300,
                                     sources=["upload", "clipboard"])
                    raum2 = gr.Dropdown([("automatisch erkennen", "auto")] + RAUM_AUSWAHL, value="auto",
                                        label="Raumtyp")
                    paar2 = gr.Checkbox(label="Zwei Personen im Bett")
                    breite2 = gr.Number(label="Raumbreite in m, falls bekannt (0 = unbekannt)", value=0, minimum=0,
                                        maximum=12)
                    los2 = gr.Button("🔍 Analysieren und verbessern", variant="primary")
                with gr.Column(scale=2):
                    kopf2 = gr.Markdown("Hier erscheint das Ergebnis.")
                    with gr.Row():
                        korrigiert = gr.Image(label="Korrigiert: Möbel an der neuen Stelle", interactive=False,
                                              height=330)
                        aenderungen = gr.Image(label="Änderungen: rot = jetzt, grün = neu", interactive=False,
                                               height=330)
            vergleich = gr.Image(label="Vorher / Nachher mit Begründungen", interactive=False)
            analyse = gr.Textbox(label="Ausführliche Analyse (laut Buch)", lines=18, interactive=False)
            dateien2 = gr.File(label="Herunterladen", file_count="multiple")
            los2.click(verbessern_ui, [foto2, raum2, paar2, breite2],
                       [korrigiert, aenderungen, vergleich, kopf2, analyse, dateien2])

        gr.Markdown("<small>Feng Shui ist ein Gestaltungs-Regelwerk, keine wissenschaftlich belegte Wirkung. "
                    "Maße aus Fotos sind auf etwa ±10–20 cm genau – vor dem Kauf nachmessen. "
                    "Preise sind grobe Richtpreise.</small>")
    return app


if __name__ == "__main__":
    os.makedirs(AUSGANG, exist_ok=True)
    seite().queue().launch(inbrowser=True, share=TEILEN, allowed_paths=[AUSGANG],
                           theme=THEMA, css=CSS)
