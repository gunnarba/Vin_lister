"""
Hovedscript for vinliste-pipelinen.

Kjører de to stegene i riktig rekkefølge:
  1. hent_poeng_vinliste.py   -> henter poengsum fra aperitif.no
  2. vinmonopolet_sortert_liste.py -> sorterer på poeng per krone

Kjør denne filen for å gjøre alt i én operasjon:
    python run.py
"""

import hent_poeng_vinliste
import vinmonopolet_sortert_liste


def main():
    print("=== Steg 1: Henter poengsum ===")
    hent_poeng_vinliste.main()

    print()
    print("=== Steg 2: Sorterer liste ===")
    vinmonopolet_sortert_liste.main()


if __name__ == "__main__":
    main()
