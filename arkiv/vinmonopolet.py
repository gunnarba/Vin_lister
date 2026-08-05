import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# ---------------------------------------------------------
# 1. LES CSV-FIL (bruk latin1, Excel lagrer ofte slik)
# ---------------------------------------------------------
try:
    df = pd.read_csv("vinliste.csv", encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv("vinliste.csv", encoding="latin1")

# ---------------------------------------------------------
# 2. FUNKSJON: Sjekk CC Vest med Vinmonopolet sitt API
# ---------------------------------------------------------



def sjekk_cc_vest_med_api(varenummer):
    url = "https://www.vinmonopolet.no/graphql"

    query = """
    query ProductAvailability($productId: String!) {
      productAvailability(productId: $productId) {
        availability {
          store {
            name
            id
          }
          availabilityStatus
          quantity
        }
      }
    }
    """

    variables = { "productId": varenummer }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    r = requests.post(url, headers=headers, json={
        "query": query,
        "variables": variables
    })

    if r.status_code != 200:
        print("GraphQL-feil:", r.status_code, "for varenummer", varenummer)
        return False, 0

    data = r.json()

    try:
        butikker = data["data"]["productAvailability"]["availability"]
    except:
        return False, 0

    for entry in butikker:
        navn = entry["store"]["name"].lower()
        antall = entry.get("quantity", 0)

        if "cc vest" in navn:
            return (antall > 0), antall

    return False, 0

# ---------------------------------------------------------
# 3. FUNKSJON: Finn Aperitif-lenke via Google
# ---------------------------------------------------------
def finn_aperitif_url(vin_navn):
    søk = urllib.parse.quote(vin_navn + " site:aperitif.no")
    url = f"https://www.google.com/search?q={søk}"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.select("a"):
        href = link.get("href")
        if href and "aperitif.no" in href:
            if href.startswith("/url?q="):
                href = href.split("/url?q=")[1].split("&")[0]
            return href

    return None

# ---------------------------------------------------------
# 4. FUNKSJON: Hent poeng fra Aperitif-siden
# ---------------------------------------------------------
def hent_poeng(aperitif_url):
    if aperitif_url is None:
        return None

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(aperitif_url, headers=headers)

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    rating = soup.select_one(".score-value, .Rating__Value, .ProductRating_score__value")
    if rating:
        return rating.get_text(strip=True)

    return "Ingen poeng funnet"

# ---------------------------------------------------------
# 5. HOVEDLOOP: Sjekk alle viner
# ---------------------------------------------------------
resultater = []

for idx, row in df.iterrows():
    varenummer = str(row["varenummer"])
    vin_navn = row["navn"]

    print(f"Sjekker: {vin_navn} (Varenr {varenummer})")

    # 1 - sjekk CC Vest
    finnes, antall = sjekk_cc_vest_med_api(varenummer)

    # Hvis ikke på lager → ingen Google-søk nødvendig
    if not finnes:
        resultater.append([
            vin_navn,
            varenummer,
            "Ikke på lager hos CC Vest",
            antall,
            None,
            None
        ])
        continue

    # 2 - finn Aperitif-lenke og poeng
    aperitif_link = finn_aperitif_url(vin_navn)
    poeng = hent_poeng(aperitif_link)

    resultater.append([
        vin_navn,
        varenummer,
        "På lager hos CC Vest",
        antall,
        aperitif_link,
        poeng
    ])

    time.sleep(1)  # pause for Google

# ---------------------------------------------------------
# 6. Lagre resultatet
# ---------------------------------------------------------
result_df = pd.DataFrame(
    resultater,
    columns=["navn", "varenummer", "status", "antall", "aperitif_url", "poeng"]
)

result_df.to_csv("vin_resultat.csv", index=False, encoding="utf-8")

print("\n✅ Ferdig! Resultat lagret i vin_resultat.csv")

print(sjekk_cc_vest_med_api("4583801"))