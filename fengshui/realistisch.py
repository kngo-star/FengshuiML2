"""
OPTIONAL und EXPERIMENTELL: die 3D-Skizze mit generativer KI fotorealistischer machen.

Idee: Stable Diffusion (Bild-zu-Bild) malt die gezeichneten Möbel „schöner“, ein ControlNet mit der
Tiefenkarte der eingerichteten Szene hält dabei Form und Position fest. Außerhalb der Möbel bleibt
das Originalfoto unverändert.

WICHTIG – bitte ehrlich im Bericht erwähnen:
  • Dieser Teil ist nicht automatisch getestet (er braucht eine Grafikkarte und lädt ~5 GB Modelle).
    Am besten in Google Colab mit „Laufzeit → T4-GPU“ ausprobieren:  !pip install diffusers accelerate
  • Generative KI kann Details erfinden. Die Möbel sehen danach evtl. etwas anders aus als die Produkte
    in der Einkaufsliste. Verbindlich bleiben Grundriss, Maße und Einkaufsliste – nicht das KI-Bild.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

SD_MODELL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
CONTROLNET = "lllyasviel/control_v11f1p_sd15_depth"

RAUM_EN = {"schlafzimmer": "bedroom", "gaestezimmer": "guest bedroom", "kinderzimmer": "kids bedroom",
           "wohnzimmer": "living room", "esszimmer": "dining room", "buero": "home office", "studio": "studio apartment"}
STIL_EN = {"natur": "natural oak wood, beige and sage fabrics, calm earthy tones",
           "hell": "light birch wood, white and light grey fabrics, scandinavian",
           "dunkel": "dark walnut wood, taupe and anthracite fabrics"}


def tiefenbild(tiefe_raum: np.ndarray, tiefe_moebel: np.ndarray) -> np.ndarray:
    """Steuerbild fürs ControlNet: nahe = hell, fern = dunkel (aus Raum-Tiefe + gezeichneten Möbeln)."""
    t = np.minimum(tiefe_raum, np.where(np.isfinite(tiefe_moebel), tiefe_moebel, np.inf))
    t = np.clip(t, 0.2, None)
    inv = 1.0 / t
    inv = (inv - inv.min()) / max(1e-6, inv.max() - inv.min())
    g = (inv * 255).astype(np.uint8)
    return np.stack([g, g, g], -1)


def verschoenere(bild: np.ndarray, foto: np.ndarray, maske: np.ndarray, tiefe_moebel: np.ndarray,
                 tiefe_raum: np.ndarray, raumtyp: str = "schlafzimmer", stil: str = "natur",
                 staerke: float = 0.5, schritte: int = 30, seed: int = 0, lange_seite: int = 768,
                 prompt: Optional[str] = None) -> np.ndarray:
    """Gibt das fotorealistischere Bild zurück (gleiche Größe wie `bild`).

    staerke: 0.3 = nah an der Skizze … 0.7 = freier (schöner, aber weiter weg von den echten Produkten).
    """
    import torch
    from PIL import Image, ImageFilter
    try:
        from diffusers import ControlNetModel, StableDiffusionControlNetImg2ImgPipeline, UniPCMultistepScheduler
    except ImportError as fehler:
        raise ImportError("Für das KI-Bild fehlt ein Paket:  pip install diffusers accelerate") from fehler

    geraet = "cuda" if torch.cuda.is_available() else "cpu"
    typ = torch.float16 if geraet == "cuda" else torch.float32
    if geraet == "cpu":
        print("  Hinweis: ohne Grafikkarte dauert das KI-Bild mehrere Minuten.")
    cn = ControlNetModel.from_pretrained(CONTROLNET, torch_dtype=typ)
    pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(SD_MODELL, controlnet=cn, torch_dtype=typ,
                                                                    safety_checker=None)
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to(geraet)

    H, W = bild.shape[:2]
    s = lange_seite / max(H, W)
    w, h = int(round(W * s / 8)) * 8, int(round(H * s / 8)) * 8
    start = Image.fromarray(bild).resize((w, h), Image.LANCZOS)
    steuer = Image.fromarray(tiefenbild(tiefe_raum, tiefe_moebel)).resize((w, h), Image.BILINEAR)
    text = prompt or (f"interior design photo of a furnished {RAUM_EN.get(raumtyp, 'room')}, "
                      f"{STIL_EN.get(stil, STIL_EN['natur'])}, soft natural daylight, realistic materials, "
                      "photorealistic, high detail")
    gen = torch.Generator(device=geraet).manual_seed(seed)
    aus = pipe(text, image=start, control_image=steuer, strength=staerke, num_inference_steps=schritte,
               guidance_scale=7.0, controlnet_conditioning_scale=1.0, generator=gen,
               negative_prompt="cartoon, 3d render, lowres, blurry, distorted, people, text, watermark").images[0]
    aus = np.asarray(aus.resize((W, H), Image.LANCZOS)).astype(np.float32)

    # nur dort übernehmen, wo Möbel sind (weicher Rand) – der Raum selbst bleibt das Originalfoto
    m = Image.fromarray((np.clip(maske, 0, 1) * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(8))
    a = (np.asarray(m, np.float32) / 255)[..., None]
    return np.clip(aus * a + foto.astype(np.float32) * (1 - a), 0, 255).astype(np.uint8)
