import csv
import requests
from bs4 import BeautifulSoup
import html
import time

from vinmonopolet_API import varenummer

INPUT_FILE = "300_pluss_roa.csv"
OUTPUT_FILE = "300_pluss_roa_poeng.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (VinlisteBot/1.0)"
}

def parse_price(price_str):
    # Fjern HTML &nbsp; og 'Kr'
    price_str = html.unescape(price_str)
    price_str = price_str.replace("Kr", "").strip()

    # Norsk/Europeisk desimal → Python-desimal
    price_str = price_str.replace(",", ".")

    return float(price_str)


def fetch_score(varenummer):
    url = (
        f"https://www.aperitif.no/pollisten?query={varenummer}&ordering=points_desc"
    )

    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    score_span = soup.select_one("div.group-2 div.points span.number")
    if score_span:
        return int(score_span.text.strip())

    return None


with open(INPUT_FILE, encoding="cp1252") as infile, \
     open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile, delimiter=";")
    fieldnames = ["varenummer", "navn", "pris", "poengsum", "poeng_per_pris"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()
    print(varenummer)
    for row in reader:
        varenummer = row["varenummer"]
        navn = html.unescape(row["navn"])
        pris = parse_price(row["pris"])

        poeng = fetch_score(varenummer)

        poeng_per_pris = round(poeng / pris, 4) if poeng else ""

        writer.writerow({
            "varenummer": varenummer,
            "navn": navn,
            "pris": pris,
            "poengsum": poeng if poeng else "",
            "poeng_per_pris": poeng_per_pris
        })

        time.sleep(1.5)


print("✅ Ferdig: vinliste1_poeng.csv")