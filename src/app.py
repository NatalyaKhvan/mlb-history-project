import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

# Page Config
st.set_page_config(page_title="MLB Pitching Stats Dashboard", layout="wide")

st.title("MLB Historical Pitching Stats Dashboard")
st.write(
    "Explore player and team pitching statistics across years. Use the filters to dynamically adjust the view."
)

# Connect to DB
db_path = "data/db/mlb_history.db"
conn = sqlite3.connect(db_path)

# Get available years and tables
all_tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)[
    "name"
].tolist()
years_set = sorted({int(t.split("_")[0]) for t in all_tables})
min_year, max_year = min(years_set), max(years_set)

st.sidebar.header("Filters")

# Year selection
year = st.sidebar.selectbox("Select Year", years_set, index=len(years_set) - 1)

# Tables for selected year
year_tables = [t for t in all_tables if t.startswith(f"{year}_")]
table_name = st.sidebar.selectbox("Select Pitching Table", year_tables)

# Load table
df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

# Column/Statistic filter
columns_to_filter = [c for c in df.columns if c not in ["year", "category", "value"]]
stat_filter_col = st.sidebar.selectbox(
    "Filter by (Player/Team)", [""] + columns_to_filter
)

if stat_filter_col:
    unique_vals = df[stat_filter_col].dropna().unique()
    selected_val = st.sidebar.selectbox(f"Select {stat_filter_col}", unique_vals)
    df = df[df[stat_filter_col] == selected_val]

# --- Value Slider ---
if "value" in df.columns:
    min_val, max_val = df["value"].min(), df["value"].max()
    selected_range = st.sidebar.slider(
        "Filter by Pitching Stat Value",
        float(min_val),
        float(max_val),
        (float(min_val), float(max_val)),
    )
    df = df[(df["value"] >= selected_range[0]) & (df["value"] <= selected_range[1])]

st.subheader(f"Pitching Data Preview ({len(df)} rows)")
st.dataframe(df.head(20))

# Visualization 1: Top 10 Pitchers/Teams by Stat Value
if "player" in df.columns or "team" in df.columns:
    group_col = "player" if "player" in df.columns else "team"
    top_df = (
        df.groupby(group_col)["value"]
        .sum()
        .reset_index()
        .sort_values(by="value", ascending=False)
        .head(10)
    )
    bar_chart = (
        alt.Chart(top_df)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title="Stat Value"),
            y=alt.Y(f"{group_col}:N", sort="-x", title=group_col.capitalize()),
            tooltip=[group_col, "value"],
        )
        .properties(title=f"Top 10 {group_col.capitalize()} by Pitching Value")
    )
    st.altair_chart(bar_chart, use_container_width=True)

# Visualization 2: Histogram of Pitching Stat Values
if "value" in df.columns:
    hist = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X("value:Q", bin=alt.Bin(maxbins=30), title="Pitching Stat Value"),
            y="count():Q",
            tooltip=["count()"],
        )
        .properties(title="Distribution of Pitching Stat Values")
    )
    st.altair_chart(hist, use_container_width=True)

# Visualization 3: Table of Top 5 Pitching Stats
st.subheader("Top 5 Pitching Statistics")
if "statistic" in df.columns:
    top_stats = df.sort_values(by="value", ascending=False).head(5)
    st.table(top_stats)

conn.close()
