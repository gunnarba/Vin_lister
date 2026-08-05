import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# ---------------------------------------------------------
# 0. KONFIGURASJON
# ---------------------------------------------------------
API_KEY = "fee9018cbe894a2185903ee27b046387"  # <-- sett inn nøkkelen her

PRODUCT_API_URL = "https://apis.vinmonopolet.no/products/v0/details-normal"
#PRODUCT_API_URL = "https://apis.vinmonopolet.no/products/v0/monthly-sales-per-store"

HEADERS_API = {
    "Ocp-Apim-Subscription-Key": API_KEY,
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

HEADERS_WEB = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}

# ---------------------------------------------------------
# 1. LES CSV (Excel = Latin1)
# ---------------------------------------------------------
try:
    df = pd.read_csv("vinliste.csv", encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv("vinliste.csv", encoding="latin1")


# ---------------------------------------------------------
# 2. FUNKSJON: Hent lagerstatus via API (OFFISIELT)
# ---------------------------------------------------------
def sjekk_cc_vest(varenummer):
    params = {
        "productId": varenummer
    }

    r = requests.get(PRODUCT_API_URL, headers=HEADERS_API, params=params)

    if r.status_code != 200:
        print(f"API-feil ({r.status_code}) for varenummer {varenummer}")
        return False, 0

    data = r.json()

    if not data or "basic" not in data[0]:
        return False, 0

    product = data[0]

    # inventory ligger under "stores" → "inventory"
    stores = product.get("stores", [])

    for store in stores:
        name = store.get("name", "").lower()
        stock = store.get("stock", 0)

        if "cc vest" in name:
            return stock > 0, stock

    return False, 0


# ---------------------------------------------------------
# 3. GOOGLE → FINN APERITIF-LENKE
# ---------------------------------------------------------
def finn_aperitif_url(vin_navn):
    søk = urllib.parse.quote(vin_navn + " site:aperitif.no")
    url = f"https://www.google.com/search?q={søk}"

    r = requests.get(url, headers=HEADERS_WEB)
    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.select("a"):
        href = link.get("href")
        if href and "aperitif.no" in href:
            if href.startswith("/url?q="):
                href = href.split("/url?q=")[1].split("&")[0]
            return href

    return None


# ---------------------------------------------------------
# 4. HENT POENG FRA APERITIF-SIDE
# ---------------------------------------------------------
def hent_poeng(aperitif_url):
    if aperitif_url is None:
        return None

    r = requests.get(aperitif_url, headers=HEADERS_WEB)

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    rating = soup.select_one(".score-value, .Rating__Value, .ProductRating_score__value")
    if rating:
        return rating.get_text(strip=True)

    return "Ikke funnet"


# ---------------------------------------------------------
# 5. HOVEDLOOP
# ---------------------------------------------------------
resultater = []

for idx, row in df.iterrows():
    varenummer = str(row["varenummer"])
    vin_navn = row["navn"]

    print(f"Sjekker: {vin_navn} (Varenr {varenummer})")

    # 1. Lagerstatus CC Vest
    finnes, antall = sjekk_cc_vest(varenummer)

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

    # 2. Aperitif
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

    time.sleep(1)  # for å unngå Google-blokkering


# ---------------------------------------------------------
# 6. LAGRE RESULTAT
# ---------------------------------------------------------
result_df = pd.DataFrame(
    resultater,
    columns=["navn", "varenummer", "status", "antall", "aperitif_url", "poeng"]
)

result_df.to_csv("vin_resultat.csv", index=False, encoding="utf-8")

print("\n✅ FERDIG! Resultat lagret i vin_resultat.csv")