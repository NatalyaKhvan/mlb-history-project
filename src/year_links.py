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

url = "https://www.baseball-almanac.com/yearmenu.shtml"
driver.get(url)

# Find League sections
league_headers = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.header h2"))
)

results = []

# Only include these leagues
target_leagues = ["American League", "National League"]

for header in league_headers:
    league_name = header.text.strip().replace(" Year-by-Year History", "")

    if league_name not in target_leagues:
        continue  # skip other leagues

    print(f"Scraping league: {league_name}")

    # The year links are in following sibling table rows
    league_table = header.find_element(
        By.XPATH, "../../following-sibling::tr[2]//table"
    )
    year_links = league_table.find_elements(By.TAG_NAME, "a")

    for link in year_links:
        year_text = link.text.strip()
        year_url = link.get_attribute("href")

        if year_text.isdigit():  # keep only years like 1901, 1902...
            results.append(
                {
                    "year": year_text,
                    "league": league_name,
                    "url": year_url,
                }
            )

# Ensure data folder exists
data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_folder, exist_ok=True)

csv_path = os.path.join(data_folder, "years.csv")

# Save to CSV
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["year", "league", "url"])
    writer.writeheader()
    writer.writerows(results)

driver.quit()
print(f"Saved {len(results)} year links to {csv_path}")
