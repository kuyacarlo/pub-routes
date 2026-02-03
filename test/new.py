import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()
url = "https://ltfrb.gov.ph/routes-with-consolidated-entities"

resp = scraper.get(url)
soup = BeautifulSoup(resp.text, "html.parser")
print(soup)
