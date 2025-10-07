import csv
import os

# Paths
raw_folder = "data/year_details/raw"
processed_folder = "data/year_details/processed"
os.makedirs(processed_folder, exist_ok=True)

# Mapping table IDs to meaningful names
table_labels = {
    "table_2": "Individual Pitching Stats",
    "table_5": "Team Pitching Stats",
    # add more mappings if needed
}

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

        # Map table ID to meaningful label
        table_name = table_labels.get(cat, cat)  # fallback to table ID if not mapped

        # Determine max columns for fallback (generic tables)
        max_cols = max(len(r["text"].split(" | ")) for r in cat_rows)

        # Define headers for CSV
        if table_name == "Individual Pitching Stats":
            headers = ["Year", "Category", "Statistic", "Player", "Team", "Value"]
        elif table_name == "Team Pitching Stats":
            headers = ["Year", "Category", "Statistic", "Team", "Value"]
        else:
            headers = ["Year", "Category"] + [f"Col{i+1}" for i in range(max_cols)]

        # Output file
        output_csv = os.path.join(processed_folder, f"{year}_{cat}_clean.csv")

        with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=headers)
            writer.writeheader()

            for r in cat_rows:
                cols = [c.strip() for c in r["text"].split(" | ")]
                row_dict = {"Year": year, "Category": table_name}

                if table_name == "Individual Pitching Stats":
                    row_dict["Statistic"] = cols[0] if len(cols) > 0 else ""
                    row_dict["Player"] = cols[1] if len(cols) > 1 else ""
                    row_dict["Team"] = cols[2] if len(cols) > 2 else ""
                    row_dict["Value"] = cols[3] if len(cols) > 3 else ""
                elif table_name == "Team Pitching Stats":
                    row_dict["Statistic"] = cols[0] if len(cols) > 0 else ""
                    row_dict["Team"] = cols[1] if len(cols) > 1 else ""
                    row_dict["Value"] = cols[2] if len(cols) > 2 else ""
                else:
                    for i in range(max_cols):
                        row_dict[f"Col{i+1}"] = cols[i] if i < len(cols) else ""

                writer.writerow(row_dict)

        print(f"Saved {output_csv}")
