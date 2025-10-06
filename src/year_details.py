import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
wait = WebDriverWait(driver, 10)

# Paths
current_dir = os.path.dirname(__file__)
data_folder = os.path.join(current_dir, "..", "data")
os.makedirs(data_folder, exist_ok=True)

raw_folder = os.path.join(data_folder, "year_details", "raw")
os.makedirs(raw_folder, exist_ok=True)

# Read years.csv
years_csv_path = os.path.join(data_folder, "years.csv")
years = []
with open(years_csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        years.append(row)

# Scrape each year
for entry in years:
    year = entry["year"]
    league = entry["league"]
    url = entry["url"]

    print(f"Scraping {year} {league} -> {url}")
    driver.get(url)

    # Wait for main content
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except:
        print(f"⚠️ Could not load {url}")
        continue

    pitching_sections = []

    # Only scrape tables that contain pitching info
    tables = driver.find_elements(By.TAG_NAME, "table")
    for idx, table in enumerate(tables, start=1):
        # Check if table contains pitching keywords
        caption_text = table.get_attribute("textContent").lower()
        if "pitching" not in caption_text:
            continue

        # Extract table rows
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            col_texts = [c.text.strip() for c in cols if c.text.strip()]
            if len(col_texts) >= 3:  # Keep rows with meaningful data
                pitching_sections.append(
                    {"category": f"table_{idx}", "text": " | ".join(col_texts)}
                )

    if not pitching_sections:
        print(f"⚠️ No pitching tables found for {year}")
        continue

    # Save to CSV
    safe_league = league.replace(" ", "_")
    csv_filename = f"{year}_{safe_league}_pitching.csv"
    csv_path = os.path.join(raw_folder, csv_filename)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "text"])
        writer.writeheader()
        writer.writerows(pitching_sections)

    print(f"Saved {len(pitching_sections)} pitching rows to {csv_path}")

driver.quit()
