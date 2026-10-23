"""Feng-Shui-Regelbasis zum automatischen Einrichten eines Zimmers.

Quelle der Regeln: Form-Schule-Feng-Shui (Kommandoposition, Chi-Fluss, fünf Elemente),
sinngemäß aus dem Buch zusammengefasst und als prüfbare Python-Regeln umgesetzt.
"""
from .modell import Balken, Bewohner, Layout, Moebel, Oeffnung, Raum, Schraege
from .bewertung import bewerte, bericht
from .optimierer import optimiere
from .regeln import REGELN

__all__ = ["Raum", "Oeffnung", "Balken", "Schraege", "Moebel", "Bewohner", "Layout",
           "bewerte", "bericht", "optimiere", "REGELN"]
