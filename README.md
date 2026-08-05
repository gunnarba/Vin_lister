# Vinpoeng-scraper

Pipeline som henter poengsum fra aperitif.no for hver vin i en Vinmonopolet-liste,
og sorterer listen etter beste poeng per krone.

## Kjør alt med `run.py`

`run.py` er hovedfilen — den kjører hele pipelinen i riktig rekkefølge:

```
python run.py
```

Dette gjør to ting etter hverandre:

1. **`hent_poeng_vinliste.py`** — henter poengsum fra aperitif.no
2. **`vinmonopolet_sortert_liste.py`** — sorterer resultatet, beste kjøp øverst

Du trenger normalt ikke kjøre de to under-scriptene hver for seg — bruk `run.py`.

## Krav

- Python 3.9 eller nyere
- Følgende pakker (installeres med pip):

```
pip install requests beautifulsoup4
```

## Filstruktur

**Steg 1 – input:** `300_pluss_roa.csv`
Semikolon-separert (`;`), kodet i `cp1252` (Windows-1252/ANSI, standard fra Excel/Vinmonopolet-eksport).

Må inneholde minst disse kolonnene:

| Kolonne     | Beskrivelse                     |
|-------------|----------------------------------|
| varenummer  | Vinmonopolets varenummer         |
| navn        | Navn på vinen                    |
| pris        | Pris, format `Kr 329,00`         |

**Steg 1 – output / Steg 2 – input:** `300_pluss_roa_poeng.csv`
Semikolon-separert, UTF-8:

| Kolonne         | Beskrivelse                                  |
|-----------------|-----------------------------------------------|
| varenummer      | Varenummer                                   |
| navn            | Navn på vinen                                |
| pris            | Pris som tall (f.eks. `329.0`)               |
| poengsum        | Poengsum fra aperitif.no (tom hvis ikke funnet) |
| poeng_per_pris  | poengsum / pris, avrundet til 4 desimaler     |

**Steg 2 – output:** `300_pluss_roa_sortert.csv`
Samme kolonner som over, men sortert med beste poeng per krone øverst
(tomme `poeng_per_pris`-rader havner nederst).

Alle filer forventes å ligge i samme mappe som scriptene, med mindre du endrer
`INPUT_FILE`/`OUTPUT_FILE` øverst i hvert script.

## Bruk

1. Legg `300_pluss_roa.csv` i samme mappe som scriptene
2. Kjør:

```
python run.py
```

3. Følg med i konsollen — Steg 1 skriver ut fremdrift per vin:

```
=== Steg 1: Henter poengsum ===
[12] 5077101 - Jean-Paul Brun L'Ancien Beaujolais 2024
```

4. Når begge stegene er ferdige, ligger sluttresultatet i `300_pluss_roa_sortert.csv`.

### Kjøre ett steg om gangen

Ønsker du å kjøre stegene separat (f.eks. for å teste sortering på gamle data
uten å hente på nytt), kan du fortsatt kjøre dem hver for seg:

```
python hent_poeng_vinliste.py
python vinmonopolet_sortert_liste.py
```

## Viktig å vite

- **Steg 1 tar tid.** Det ligger inn en pause på 1,5 sekund mellom hvert oppslag for
  ikke å overbelaste aperitif.no. Med 85 rader tar dette fort 3–5 minutter. Konsollen
  skriver ut fremdrift underveis — ser det ut som ingenting skjer i lang tid uten
  noen utskrift i det hele tatt, sjekk at du faktisk kjører den oppdaterte versjonen
  (med `print()` i løkken).
- **Manglende poengsum er normalt.** Ikke alle viner ligger i pollisten på
  aperitif.no, eller siden kan tidvis blokkere/begrense automatiserte oppslag. Rader
  uten treff får tom `poengsum` og tom `poeng_per_pris`, og havner nederst etter
  sortering i Steg 2.
- **Ved nettverksfeil** (tidsavbrudd, tilkoblingsfeil) hopper Steg 1 over den
  aktuelle raden i stedet for å stoppe hele kjøringen, og skriver en varsel-linje i
  konsollen (`[!] ...`).

## Feilsøking

| Symptom | Mulig årsak |
|---|---|
| `FileNotFoundError` i Steg 1 | `300_pluss_roa.csv` ligger ikke i samme mappe, eller feil filnavn |
| `FileNotFoundError` i Steg 2 | Steg 1 har ikke kjørt ennå, eller `300_pluss_roa_poeng.csv` mangler — kjør `run.py` fra start |
| `UnicodeDecodeError` ved lesing | Input-filen er ikke faktisk kodet i `cp1252` — sjekk hvordan den ble eksportert |
| Alle rader får tom `poengsum` | Siden blokkerer trolig automatiserte oppslag (bot-beskyttelse), eller CSS-strukturen på aperitif.no er endret |
| Scriptet ser ut til å henge | Sjekk at du kjører den oppdaterte versjonen med fremdriftsutskrift per rad — uten den er det ofte bare treigt, ikke fastlåst |
