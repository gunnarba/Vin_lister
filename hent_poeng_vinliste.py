import csv
import os
import requests
from bs4 import BeautifulSoup
import html
import time

INPUT_FILE = "300_pluss_roa.csv"
OUTPUT_FILE = "300_pluss_roa_poeng.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def parse_price(price_str):
    price_str = html.unescape(price_str)
    price_str = price_str.replace("Kr", "").strip()
    price_str = price_str.replace(",", ".")
    return float(price_str)


def fetch_score(varenummer, session):
    url = f"https://www.aperitif.no/pollisten?query={varenummer}&ordering=points_desc"

    try:
        r = session.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"  [!] Request failed for {varenummer}: {e}")
        return None

    if r.status_code != 200:
        print(f"  [!] HTTP {r.status_code} for {varenummer}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    score_span = soup.select_one("div.group-2 div.points span.number")
    if score_span:
        try:
            return int(score_span.text.strip())
        except ValueError:
            return None

    return None


def main():
    print("Working directory:", os.getcwd())
    print("Input exists:", os.path.exists(INPUT_FILE))

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: '{INPUT_FILE}' not found i {os.getcwd()}. "
              f"Sjekk filsti og prøv igjen.")
        return

    session = requests.Session()

    with open(INPUT_FILE, encoding="cp1252") as infile, \
         open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile, delimiter=";")
        fieldnames = ["varenummer", "navn", "pris", "poengsum", "poeng_per_pris"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        rows_written = 0
        rows_with_score = 0

        for row in reader:
            varenummer = row["varenummer"]
            navn = html.unescape(row["navn"])

            try:
                pris = parse_price(row["pris"])
            except (ValueError, KeyError) as e:
                print(f"  [!] Hopper over rad {varenummer}, ugyldig pris: {e}")
                continue

            print(f"[{rows_written + 1}] {varenummer} - {navn}")
            poeng = fetch_score(varenummer, session)
            if poeng is not None:
                rows_with_score += 1

            poeng_per_pris = round(poeng / pris, 4) if poeng else ""

            writer.writerow({
                "varenummer": varenummer,
                "navn": navn,
                "pris": pris,
                "poengsum": poeng if poeng else "",
                "poeng_per_pris": poeng_per_pris
            })
            outfile.flush()
            rows_written += 1

            time.sleep(1.5)

    print()
    print(f"Ferdig. {rows_written} rader skrevet, {rows_with_score} med poengsum.")
    print("Output:", os.path.abspath(OUTPUT_FILE))


if __name__ == "__main__":
    main()
