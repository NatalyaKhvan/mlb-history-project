import csv
import os

# Paths
raw_folder = "data/year_details/raw"
processed_folder = "data/year_details/processed"
os.makedirs(processed_folder, exist_ok=True)

# Process all raw CSV files
for filename in os.listdir(raw_folder):
    if not filename.endswith(".csv"):
        continue

    input_csv = os.path.join(raw_folder, filename)
    year = filename.split("_")[0]  # assumes filename starts with year

    with open(input_csv, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    # Group rows by category (table)
    tables = {}
    for row in rows:
        cat = row["category"]
        if cat not in tables:
            tables[cat] = []
        # Skip repeated header rows inside table
        if row["text"].startswith("Statistic"):
            continue
        tables[cat].append(row)

    # Write each table to a separate clean CSV
    for cat, cat_rows in tables.items():
        if not cat_rows:
            continue  # skip empty tables

        # Find max number of columns
        max_cols = max(len(r["text"].split(" | ")) for r in cat_rows)
        headers = ["category"] + [f"col{i+1}" for i in range(max_cols)]

        # Output file
        output_csv = os.path.join(processed_folder, f"{year}_{cat}_clean.csv")

        with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=headers)
            writer.writeheader()
            for r in cat_rows:
                cols = r["text"].split(" | ")
                row_dict = {"category": r["category"]}
                for i in range(max_cols):
                    row_dict[f"col{i+1}"] = cols[i] if i < len(cols) else ""
                writer.writerow(row_dict)

        print(f"Saved {output_csv}")
