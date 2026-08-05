# Vinpoeng-scraper

Pipeline som henter poengsum fra aperitif.no for hver vin i en Vinmonopolet-liste,
og sorterer listen etter beste poeng per krone.

## Mappestruktur

```
Vin_lister/
├── run.py
├── hent_poeng_vinliste.py
├── vinmonopolet_sortert_liste.py
├── README.md
└── data_input/
    ├── input/
    │   └── input_300_pluss_roa.csv
    └── output/
        ├── 300_pluss_roa_poeng.csv
        └── 300_pluss_roa_sortert.csv
```

Scriptene kjøres fra repo-roten (der `run.py` ligger) — de bruker relative stier til
`data_input/input/` og `data_input/output/`, uavhengig av hvor du kjører fra i PyCharm.

## Kjør alt med `run.py`

```
python run.py
```

Dette gjør to ting etter hverandre:

1. **`hent_poeng_vinliste.py`** — leser `data_input/input/input_300_pluss_roa.csv`,
   henter poengsum fra aperitif.no, skriver til `data_input/output/300_pluss_roa_poeng.csv`
2. **`vinmonopolet_sortert_liste.py`** — leser output fra steg 1, sorterer og skriver til
   `data_input/output/300_pluss_roa_sortert.csv`

Du trenger normalt ikke kjøre de to under-scriptene hver for seg — bruk `run.py`.

## Krav

- Python 3.9 eller nyere
- Følgende pakker (installeres med pip):

```
pip install requests beautifulsoup4
```

## Filformat

**Input:** `data_input/input/input_300_pluss_roa.csv`
Semikolon-separert (`;`), kodet i `cp1252` (Windows-1252/ANSI, standard fra Excel/Vinmonopolet-eksport).

Må inneholde minst disse kolonnene:

| Kolonne     | Beskrivelse                     |
|-------------|----------------------------------|
| varenummer  | Vinmonopolets varenummer         |
| navn        | Navn på vinen                    |
| pris        | Pris, format `Kr 329,00`         |

**Mellomresultat:** `data_input/output/300_pluss_roa_poeng.csv`
Semikolon-separert, UTF-8:

| Kolonne         | Beskrivelse                                  |
|-----------------|-----------------------------------------------|
| varenummer      | Varenummer                                   |
| navn            | Navn på vinen                                |
| pris            | Pris som tall (f.eks. `329.0`)               |
| poengsum        | Poengsum fra aperitif.no (tom hvis ikke funnet) |
| poeng_per_pris  | poengsum / pris, avrundet til 4 desimaler     |

**Sluttresultat:** `data_input/output/300_pluss_roa_sortert.csv`
Samme kolonner som over, men sortert med beste poeng per krone øverst
(tomme `poeng_per_pris`-rader havner nederst).

## Bruk

1. Legg input-filen i `data_input/input/input_300_pluss_roa.csv`
2. Kjør fra repo-roten:

```
python run.py
```

3. Følg med i konsollen — Steg 1 skriver ut fremdrift per vin:

```
=== Steg 1: Henter poengsum ===
[12] 5077101 - Jean-Paul Brun L'Ancien Beaujolais 2024
```

4. Når begge stegene er ferdige, ligger sluttresultatet i `data_input/output/300_pluss_roa_sortert.csv`.

### Kjøre ett steg om gangen

```
python hent_poeng_vinliste.py
python vinmonopolet_sortert_liste.py
```

## Viktig å vite

- **Steg 1 tar tid.** Det ligger inn en pause på 1,5 sekund mellom hvert oppslag for
  ikke å overbelaste aperitif.no. Med 85 rader tar dette fort 3–5 minutter. Konsollen
  skriver ut fremdrift underveis.
- **Manglende poengsum er normalt.** Ikke alle viner ligger i pollisten på
  aperitif.no. Rader uten treff får tom `poengsum` og `poeng_per_pris`, og havner
  nederst etter sortering i Steg 2.
- **Ved nettverksfeil** hopper Steg 1 over den aktuelle raden i stedet for å stoppe
  hele kjøringen, og skriver en varsel-linje i konsollen (`[!] ...`).
- **Output-mappen opprettes automatisk** hvis den ikke finnes fra før.

## Feilsøking

| Symptom | Mulig årsak |
|---|---|
| `FileNotFoundError` i Steg 1 | `data_input/input/input_300_pluss_roa.csv` mangler, eller du kjører scriptet fra feil mappe (ikke repo-roten) |
| `FileNotFoundError` i Steg 2 | Steg 1 har ikke kjørt ennå — kjør `run.py` fra start |
| `UnicodeDecodeError` ved lesing | Input-filen er ikke faktisk kodet i `cp1252` — sjekk hvordan den ble eksportert |
| Alle rader får tom `poengsum` | Siden blokkerer trolig automatiserte oppslag (bot-beskyttelse), eller CSS-strukturen på aperitif.no er endret |
| Scriptet ser ut til å henge | Følg med på fremdriftsutskriften — det er ofte bare treigt, ikke fastlåst |
