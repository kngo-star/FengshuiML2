"""
▶ Änderungen mit GitHub synchronisieren – per Klick in PyCharm.

Rechtsklick auf push.py → Run 'push'. Das Skript
  1. holt zuerst die Änderungen deines Teams (git pull),
  2. zeigt dir, welche Dateien du geändert hast,
  3. speichert sie mit einer Nachricht (git commit),
  4. lädt sie hoch (git push).

Die Nachricht kannst du unten bei NACHRICHT eintragen oder beim Start eingeben.
Fotos, Modelle und deine Bewertungen werden wegen der .gitignore nie hochgeladen.
"""
import subprocess
import sys
from datetime import datetime

NACHRICHT = ""          # leer lassen = beim Start fragen (Enter = automatische Nachricht)


def git(*args, pruefen=True):
    """Führt einen git-Befehl aus und gibt (Erfolg, Ausgabe) zurück."""
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    ausgabe = (r.stdout + r.stderr).rstrip()
    if pruefen and r.returncode != 0:
        print(f"✗ git {' '.join(args)} ist fehlgeschlagen:\n{ausgabe}")
    return r.returncode == 0, ausgabe


def main():
    ok, _ = git("rev-parse", "--is-inside-work-tree", pruefen=False)
    if not ok:
        sys.exit("✗ Dieser Ordner ist nicht mit GitHub verbunden. Projekt über "
                 "File → New → Project from Version Control neu klonen.")

    # 1. Erst die Änderungen der anderen holen
    print("⬇  Hole Änderungen von GitHub …")
    ok, out = git("pull", "--rebase", "--autostash", pruefen=False)
    if not ok:
        print(out)
        if "CONFLICT" in out or "conflict" in out:
            sys.exit("✗ Konflikt: Du und dein Teammitglied habt dieselbe Stelle geändert.\n"
                     "  In PyCharm: Git → Resolve Conflicts … öffnen, Konflikt lösen, dann push.py erneut starten.")
        sys.exit("✗ Pull fehlgeschlagen (siehe oben). Internetverbindung prüfen.")
    print("   " + (out.strip().splitlines()[-1] if out.strip() else "aktuell"))

    # 2. Was hat sich geändert?
    _, status = git("status", "--porcelain")
    if not status:
        _, voraus = git("rev-list", "--count", "@{u}..HEAD", pruefen=False)
        if voraus.strip() in ("", "0"):
            print("✓ Nichts zu pushen – alles ist schon auf GitHub.")
            return
    else:
        print("\n📝 Geänderte Dateien:")
        for zeile in status.splitlines():
            zeichen = {"M": "geändert", "A": "neu", "D": "gelöscht", "??": "neu", "R": "umbenannt"}
            code = zeile[:2].strip()
            print(f"   {zeichen.get(code, code):9} {zeile[3:]}")

        nachricht = NACHRICHT.strip()
        if not nachricht:
            try:
                nachricht = input("\nKurze Beschreibung (Enter = automatisch): ").strip()
            except EOFError:
                nachricht = ""
        if not nachricht:
            nachricht = f"Änderungen vom {datetime.now():%d.%m.%Y %H:%M}"

        # 3. Speichern (commit)
        git("add", "-A")
        ok, out = git("commit", "-m", nachricht, pruefen=False)
        if not ok:
            if "user.email" in out or "Please tell me who you are" in out:
                sys.exit("✗ Git kennt deinen Namen noch nicht. Einmal im Terminal ausführen:\n"
                         '  git config --global user.name "Dein Name"\n'
                         '  git config --global user.email "deine@email.com"')
            sys.exit(f"✗ Commit fehlgeschlagen:\n{out}")
        print(f"\n💾 Gespeichert: {nachricht}")

    # 4. Hochladen (push)
    print("⬆  Lade auf GitHub hoch …")
    ok, ziel = git("rev-parse", "--abbrev-ref", "@{u}", pruefen=False)      # z. B. "origin/main"
    if ok and "/" in ziel:
        remote, zweig = ziel.strip().split("/", 1)
        ok, out = git("push", remote, f"HEAD:{zweig}", pruefen=False)
    else:
        ok, out = git("push", "-u", "origin", "HEAD", pruefen=False)
    if not ok:
        print(out)
        if "Authentication" in out or "403" in out or "could not read Username" in out:
            sys.exit("✗ GitHub-Anmeldung fehlt. In PyCharm: Settings → Version Control → GitHub → + → "
                     "Log In via GitHub, dann push.py erneut starten.")
        sys.exit("✗ Push fehlgeschlagen (siehe oben).")
    _, stand = git("log", "--oneline", "-1")
    print(f"✓ Fertig! Auf GitHub ist jetzt: {stand.strip()}")


if __name__ == "__main__":
    main()
