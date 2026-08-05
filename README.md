# Vinpoeng-scraper

Henter poengsum fra aperitif.no for hver vin i en Vinmonopolet-liste, og regner ut poeng per krone.

## Hva scriptet gjør

1. Leser inn en CSV-fil med vinliste (varenummer, navn, pris osv.)
2. Slår opp hvert varenummer på aperitif.no sin pollisten
3. Henter poengsummen hvis den finnes
4. Regner ut `poeng_per_pris` (poengsum delt på pris)
5. Skriver resultatet til en ny CSV-fil

## Krav

- Python 3.9 eller nyere
- Følgende pakker (installeres med pip):

```
pip install requests beautifulsoup4
```

## Filstruktur

Scriptet forventer at input-filen ligger i samme mappe som scriptet, eller at du oppgir full sti.

**Input:** `300_pluss_roa.csv`
Semikolon-separert (`;`), kodet i `cp1252` (Windows-1252/ANSI, standard fra Excel/Vinmonopolet-eksport).

Må inneholde minst disse kolonnene:

| Kolonne     | Beskrivelse                     |
|-------------|----------------------------------|
| varenummer  | Vinmonopolets varenummer         |
| navn        | Navn på vinen                    |
| pris        | Pris, format `Kr 329,00`         |

**Output:** `300_pluss_roa_poeng.csv`
Semikolon-separert, UTF-8, med kolonnene:

| Kolonne         | Beskrivelse                                  |
|-----------------|-----------------------------------------------|
| varenummer      | Varenummer                                   |
| navn            | Navn på vinen                                |
| pris            | Pris som tall (f.eks. `329.0`)               |
| poengsum        | Poengsum fra aperitif.no (tom hvis ikke funnet) |
| poeng_per_pris  | poengsum / pris, avrundet til 4 desimaler     |

## Bruk

1. Legg `300_pluss_roa.csv` i samme mappe som scriptet
2. Kjør scriptet:

```
hent_poeng_vinliste.py
```

3. Følg med i konsollen — scriptet skriver ut fremdrift per vin, f.eks.:

```
[12] 5077101 - Jean-Paul Brun L'Ancien Beaujolais 2024
```

4. Når det er ferdig, ligger resultatet i `300_pluss_roa_poeng.csv` i samme mappe.

## Viktig å vite

- **Scriptet tar tid.** Det ligger inn en pause på 1,5 sekund mellom hvert oppslag for ikke å overbelaste aperitif.no. Med 85 rader tar dette fort 3–5 minutter. Konsollen skriver ut fremdrift underveis — hvis det ser ut som ingenting skjer i lang tid uten noen utskrift i det hele tatt, sjekk at du kjører versjonen med fremdriftsutskrift (ikke en variant uten `print()` i løkken).
- **Manglende poengsum er normalt.** Ikke alle viner ligger i pollisten på aperitif.no, eller siden kan tidvis blokkere/begrense automatiserte oppslag. Rader uten treff får tom `poengsum` og tom `poeng_per_pris` i output, resten av kjøringen fortsetter som normalt.
- **Ved nettverksfeil** (tidsavbrudd, tilkoblingsfeil) hopper scriptet over den aktuelle raden i stedet for å stoppe hele kjøringen, og skriver en varsel-linje i konsollen (`[!] ...`).

## Feilsøking

| Symptom | Mulig årsak |
|---|---|
| `FileNotFoundError` | Input-filen ligger ikke i samme mappe som scriptet, eller feil filnavn |
| `UnicodeDecodeError` ved lesing | Input-filen er ikke faktisk kodet i `cp1252` — sjekk hvordan den ble eksportert |
| Alle rader får tom `poengsum` | Siden blokkerer trolig automatiserte oppslag (bot-beskyttelse), eller CSS-strukturen på aperitif.no er endret |
| Scriptet ser ut til å henge | Sjekk at du kjører versjonen med fremdriftsutskrift per rad — uten den er det ofte bare treigt, ikke fastlåst |
