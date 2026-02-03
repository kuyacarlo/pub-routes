from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

url = "https://ltfrb.gov.ph/routes-with-consolidated-entities"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector("table.tablepress")  # wait until table loads
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")

data = []
for table in soup.select("table.tablepress"):
    table_name = table.select_one("thead th.column-1").text.strip()
    entries = []
    for row in table.select("tbody tr"):
        entries.append({
            "name": row.select_one("td.column-1").text.strip(),
            "url": row.select_one("td.column-2 a")["href"]
        })
    data.append({"name": table_name, "entries": entries})

with open("routes.jsonl", "w") as f:
    for item in data:
        f.write(json.dumps(item) + "\n")

