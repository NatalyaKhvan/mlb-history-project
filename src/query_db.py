import sqlite3
import pandas as pd

# Connect to the database
db_path = "data/db/mlb_history.db"
conn = sqlite3.connect(db_path)

# Get all table names
all_tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)[
    "name"
].tolist()

# Extract available years and summarize as a range
years_set = {int(t.split("_")[0]) for t in all_tables if t[0].isdigit()}
min_year, max_year = min(years_set), max(years_set)
print(f"Available years: {min_year}–{max_year}")

# Prompt user for year
year_input = input("Enter year: ").strip()
if not year_input.isdigit() or int(year_input) not in years_set:
    print(f"Year {year_input} not available.")
    conn.close()
    exit()

year = int(year_input)

# Get tables for the selected year
year_tables = [t for t in all_tables if t.startswith(f"{year}_")]
print("\nTables for this year:")
for i, t in enumerate(year_tables, start=1):
    print(f"  {i}. {t}")

# Allow user to choose by number or name
table_input = input("\nEnter table name or number: ").strip()
if table_input.isdigit():
    table_index = int(table_input) - 1
    if table_index < 0 or table_index >= len(year_tables):
        print(f"Invalid table number {table_input}.")
        conn.close()
        exit()
    table = year_tables[table_index]
else:
    if table_input not in year_tables:
        print(f"Table {table_input} not found for year {year}.")
        conn.close()
        exit()
    table = table_input

quoted_table = f'"{table}"'

# Get column names
cols = pd.read_sql(f"PRAGMA table_info({quoted_table})", conn)["name"].tolist()
print("\nAvailable columns/statistics:")
for i, c in enumerate(cols, start=1):
    print(f"  {i}. {c}")

# Ask user whether to apply a filter
filter_col = input("\nEnter a column to filter by (or leave blank for none): ").strip()
filter_value = None
if filter_col:
    if filter_col not in cols:
        print(f"Column '{filter_col}' does not exist in table '{table}'.")
        conn.close()
        exit()

    # Show unique values for that column (up to 20)
    unique_vals = pd.read_sql(
        f"SELECT DISTINCT {filter_col} FROM {quoted_table}", conn
    )[filter_col].tolist()
    print(f"\nAvailable values for '{filter_col}' (showing up to 20):")
    print(unique_vals[:20])

    filter_value = input(f"\nEnter value to filter '{filter_col}' by: ").strip()

# Build and execute query
sql = f"SELECT * FROM {quoted_table}"
params = None
if filter_col and filter_value:
    sql += f" WHERE {filter_col} = ?"
    params = (filter_value,)

try:
    df = pd.read_sql(sql, conn, params=params)
    if df.empty:
        print("\nNo results found.")
    else:
        print("\nQuery results (first 20 rows):")
        print(df.head(20))
        print(f"\nTotal rows: {len(df)}")
except Exception as e:
    print(f"Error executing query: {e}")

conn.close()
