# MLB History Web Scraping & Streamlit App

This project scrapes historical **pitching data** from the Major League Baseball History website, stores it in a SQLite database, and visualizes insights using an interactive Streamlit app.

## Project Structure

- `data/`
  - `raw/` – Raw CSV files of pitching data for each year
  - `processed/` – Cleaned CSV files ready for database import
- `notebooks/` – Exploratory analysis and visualizations
- `src/` – Python scripts for:
  - Web scraping pitching statistics
  - Database import
  - Database query
  - Streamlit app

## Requirements, Dependencies & Usage

Install dependencies using:

```bash
pip install -r requirements.txt
```

Dependencies include:

- numpy
- pandas
- matplotlib
- plotly
- seaborn
- streamlit
- selenium
- gunicorn

Usage:

- Web Scraping: Run the scraping script in `src/` to retrieve data and save as CSV  
  `python src/scrape_mlb_data.py`

- Database Import: Load CSV files into SQLite database  
  `python src/import_to_db.py`

- Database Query: Query the database from the command line  
  `python src/query_db.py`

- Streamlit App: Launch the interactive Streamlit app  
  `streamlit run src/app.py`

## Screenshot

![Streamlit App Screenshot](path/to/screenshot.png)
