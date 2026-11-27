"""
Alle Tests ausführen – prüft, ob die Regeln richtig programmiert sind.

In PyCharm: Rechtsklick auf tests_ausfuehren.py -> Run 'tests_ausfuehren'
(Kein zusätzliches Paket nötig. Wer pytest installiert hat, kann auch `python -m pytest tests` nutzen.)
"""
import os
import sys
import time
import traceback

# Projektordner zum Suchpfad hinzufügen – so laufen die Tests auch, wenn man sie
# aus einem anderen Ordner startet (z. B. `python ../FengshuiML2/tests_ausfuehren.py`).
PROJEKT = os.path.dirname(os.path.abspath(__file__))
if PROJEKT not in sys.path:
    sys.path.insert(0, PROJEKT)
os.chdir(PROJEKT)                                   # Tests lesen Dateien wie produkte.json relativ zum Projekt

from tests import test_einrichten, test_regeln  # noqa: E402


def main():
    tests = [(n, f) for modul in (test_regeln, test_einrichten)
             for n, f in vars(modul).items() if n.startswith("test_") and callable(f)]
    ok, fehler = 0, []
    start = time.time()
    for name, f in tests:
        titel = name[5:].replace("_", " ")
        try:
            f()
            ok += 1
            print(f"  ✓ {titel}")
        except Exception as e:                      # noqa: BLE001 – jeden Fehler melden
            fehler.append((name, e))
            print(f"  ✗ {titel}\n      {type(e).__name__}: {e}")
    print()
    print(f"{ok} von {len(tests)} Tests bestanden ({time.time() - start:.0f} s).")
    if fehler:
        print("\nDetails zum ersten Fehler:")
        traceback.print_exception(fehler[0][1])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
