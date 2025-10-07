import os
import pandas as pd
import sqlite3
import re

# Paths
processed_folder = "data/year_details/processed"
db_folder = "data/db"
os.makedirs(db_folder, exist_ok=True)
db_path = os.path.join(db_folder, "mlb_history.db")

# Connect to SQLite
conn = sqlite3.connect(db_path)

# Import each CSV as a separate table
for filename in os.listdir(processed_folder):
    if not filename.endswith(".csv"):
        continue

    csv_path = os.path.join(processed_folder, filename)

    try:
        df = pd.read_csv(csv_path)

        # Normalize column names
        df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

        # Extract year and category
        year = str(df["year"].iloc[0]) if "year" in df.columns else "unknown"
        category = (
            df["category"].iloc[0].lower().replace(" ", "_")
            if "category" in df.columns
            else "misc"
        )

        # Safe table name
        table_name = re.sub(r"\W+", "_", f"{year}_{category}")

        # Clean numeric columns (remove commas, convert to numbers)
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.replace(",", "", regex=True)
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # Import to SQLite
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Imported {filename} as table '{table_name}'")

    except Exception as e:
        print(f"Failed to import {filename}: {e}")

# Close connection
conn.close()
print(f"All CSVs from '{processed_folder}' imported into '{db_path}' successfully.")
