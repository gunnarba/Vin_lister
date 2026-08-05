import csv
import os

INPUT_FILE = "300_pluss_roa_poeng.csv"
OUTPUT_FILE = "300_pluss_roa_sortert.csv"


def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: '{INPUT_FILE}' finnes ikke i {os.getcwd()}. "
              f"Kjør hent_poeng_vinliste.py først.")
        return

    with open(INPUT_FILE, encoding="utf-8") as infile:
        reader = csv.DictReader(infile, delimiter=";")
        rows = list(reader)
        fieldnames = reader.fieldnames  # bruk eksakt samme kolonner

    # Konverter og beregn poeng per pris
    for row in rows:
        row["pris"] = to_float(row["pris"])
        row["poengsum"] = to_float(row["poengsum"])
        if row["pris"] and row["poengsum"]:
            row["poeng_per_pris"] = round(row["poengsum"] / row["pris"], 2)
        else:
            row["poeng_per_pris"] = ""

    # Sortering: beste kjøp øverst
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            r["poeng_per_pris"] == "",      # tomme nederst
            -to_float(r["poeng_per_pris"] or 0),
            -(r["poengsum"] or 0)
        )
    )

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows_sorted)

    print(f"Ferdig. {len(rows_sorted)} rader sortert.")
    print("Output:", os.path.abspath(OUTPUT_FILE))


if __name__ == "__main__":
    main()
