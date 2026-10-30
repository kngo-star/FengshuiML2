"""
Alle Tests ausführen – prüft, ob die Regeln richtig programmiert sind.

In PyCharm: Rechtsklick auf tests_ausfuehren.py -> Run 'tests_ausfuehren'
(Kein zusätzliches Paket nötig. Wer pytest installiert hat, kann auch `python -m pytest tests` nutzen.)
"""
import time
import traceback

from tests import test_regeln


def main():
    tests = [(n, f) for n, f in vars(test_regeln).items() if n.startswith("test_") and callable(f)]
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
