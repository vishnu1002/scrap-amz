import time
import csv
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import re

# Configuration constants
CHROME_DRIVER_PATH = r"C:\Windows\chromedriver-win64\chromedriver.exe"
SEARCH_QUERY = "smartphone"
BASE_URL = f"https://www.amazon.in/s?k={SEARCH_QUERY}"
NUM_PRODUCTS = 100
MAX_THREADS = 50
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
]
CSV_FILE = "amazon_scraped_data.csv"

def log(message):
    print(f"[LOG] {message}")

def setup_selenium():
    """Sets up and returns a Selenium WebDriver instance."""
    log("Initializing Selenium WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    service = Service(executable_path=CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=chrome_options)

def get_product_links(driver, base_url, num_products):
    """Extracts product links from Amazon search pages."""
    product_links = set()
    page = 1
    while len(product_links) < num_products:
        url = f"{base_url}&page={page}"
        log(f"Opening page {page}: {url}")
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.a-link-normal.s-no-outline"))
            )
        except:
            log(f"⚠️ Skipping page {page} due to loading issues.")
            break
        soup = BeautifulSoup(driver.page_source, "lxml")
        for a in soup.select("a.a-link-normal.s-no-outline"):
            href = a.get("href")
            if href and "/dp/" in href:
                asin_match = re.search(r"/dp/([A-Z0-9]{10})", href)
                if asin_match:
                    asin = asin_match.group(1)
                    actual_product_url = f"https://www.amazon.in/dp/{asin}"
                    product_links.add(actual_product_url)
        log(f"✅ Found {len(product_links)} total products so far.")
        if len(product_links) >= num_products:
            break
        page += 1
        time.sleep(random.uniform(1, 3))
    return list(product_links)[:num_products]

def scrape_product(url, session):
    """Scrapes product data from a given URL."""
    log(f"Scraping: {url}")
    for attempt in range(3):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            prod_soup = BeautifulSoup(response.text, "lxml")

            title = prod_soup.find("span", {"id": "productTitle"}).get_text(strip=True) if prod_soup.find("span", {"id": "productTitle"}) else "N/A"
            price_whole = prod_soup.select_one("span.a-price-whole").get_text(strip=True) if prod_soup.select_one("span.a-price-whole") else "N/A"
            price_fraction = prod_soup.select_one("span.a-price-fraction").get_text(strip=True) if prod_soup.select_one("span.a-price-fraction") else ""
            price = f"{price_whole}.{price_fraction}" if price_whole != "N/A" else "N/A"
            rating = prod_soup.find("span", {"class": "a-icon-alt"}).get_text(strip=True) if prod_soup.find("span", {"class": "a-icon-alt"}) else "N/A"
            reviews = prod_soup.select_one("#acrCustomerReviewText").get_text(strip=True) if prod_soup.select_one("#acrCustomerReviewText") else "0 reviews"
            availability = prod_soup.select_one("#availability span").get_text(strip=True) if prod_soup.select_one("#availability span") else "N/A"

            log(f"✓ Scraped: {title[:50]}... (Price: {price}, Rating: {rating}, Reviews: {reviews})")
            return {
                "Title": title,
                "URL": url,
                "Price": price,
                "Rating": rating,
                "Reviews": reviews,
                "Availability": availability
            }
        except requests.exceptions.RequestException as e:
            log(f"❌ Error fetching {url}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def main():
    log("Starting the scraping process...")
    driver = setup_selenium()
    product_links = get_product_links(driver, BASE_URL, NUM_PRODUCTS)
    driver.quit()
    session = requests.Session()
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = list(executor.map(lambda url: scrape_product(url, session), product_links))
    scraped_data = [data for data in results if data]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "URL", "Price", "Rating", "Reviews", "Availability"])
        writer.writeheader()
        writer.writerows(scraped_data)
    log(f"✅ Scraping complete! Data saved to {CSV_FILE}.")

if __name__ == "__main__":
    main()