
# scrap-amz
Amazon Product Scraping

# ChromeDriver Setup
1. Check Chrome version: chrome://settings/help
2. Download ChromeDriver: [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)
	-	Click **Stable**
	-	Copy **URL** of **win64** Platform
	-	Unzip Folder `chromedriver-win64`
	-	Copy `chromedriver-win64` to `C:\Windows\`
	-	Open ***System Environment Variables*** > *System Variable* > *Path* > *New*
	-	Save path as: **C:\Windows\chromedriver-win64\chromedriver.exe**

# Install Requirements

    pip install selenium beautifulsoup4 requests lxml

# Code Config

-   `CHROME_DRIVER_PATH`: Path to your Chrome WebDriver executable.
-   `SEARCH_QUERY`: The search term you want to scrape products for.
-   `BASE_URL`: The base URL for Amazon India search results.
-   `NUM_PRODUCTS`: The number of products you want to scrape.
-   `MAX_THREADS`: The maximum number of threads for parallel processing.
-   `CSV_FILE`: The output CSV file where scraped data will be saved.

example:

```
CHROME_DRIVER_PATH  =  r"C:\Windows\chromedriver-win64\chromedriver.exe"
SEARCH_QUERY  =  "smartphone"
BASE_URL  =  f"https://www.amazon.in/s?k={SEARCH_QUERY}"
NUM_PRODUCTS  =  100
MAX_THREADS  =  50
CSV_FILE  =  "data.csv"
```
