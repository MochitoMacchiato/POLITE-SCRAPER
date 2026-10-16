import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
import json

CACHE_DIR = Path("cache")
USER_AGENT = "FlyRankInternship-A9/1.0 (https://github.com/MochitoMacchiato/POLITE-SCRAPER.git)"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 3
DELAY_SECONDS = 0.5


def fetch_page(url, cache_name):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / cache_name

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(f"CACHE HIT size={len(html)}")
        return html, False

    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=10
    )

    response.encoding = "UTF-8"

    if response.status_code != 200:
        print(f"FETCH FAILED status={response.status_code}")
        return None, True

    html = response.text
    cache_file.write_text(html, encoding="utf-8")
    print(f"FETCH size={len(html)}")
    return html, True


def parse_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")

    book_urls = []
    for tag in soup.select("article.product_pod h3 a"):
        book_urls.append(urljoin(page_url, tag["href"]))

    next_url = None
    next_tag = soup.select_one("li.next a")
    if next_tag is not None:
        next_url = urljoin(page_url, next_tag["href"])

    return book_urls, next_url


def discover_books(max_pages):
    current_url = START_URL
    pages_visited = 0
    discovered = 0
    books = {}

    while current_url is not None and pages_visited < max_pages:
        cache_name = f"catalogue-page-{pages_visited + 1}.html"
        html, was_fetched = fetch_page(current_url, cache_name)

        if html is None:
            break

        if was_fetched:
            time.sleep(DELAY_SECONDS)

        links, next_url = parse_page(html, current_url)
        discovered += len(links)

        for link in links:
            if link not in books:
                books[link] = current_url

        pages_visited += 1
        current_url = next_url

    return books, pages_visited, discovered


def cache_name_for_book(book_url):
    parts = book_url.split("/")
    folder = parts[-2]
    return f"book-{folder}.html"


def extract_book(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one("div.col-sm-6.product_main")

    title = product.select_one("h1").get_text(strip=True)
    price = product.select_one("p.price_color").get_text(strip=True)
    availability = product.select_one("p.instock.availability").get_text(strip=True)

    rating_tag = product.select_one("p.star-rating")
    classes = rating_tag["class"]

    rating = None
    for c in classes:
        if c != "star-rating":
            rating = c

    desc_tag = soup.select_one("div#product_description + p")

    if desc_tag is not None:
        desc = desc_tag.get_text(strip=True, separator=" ")
    else:
        desc = None

    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price,
        "availability_text": availability,
        "rating_text": rating,
        "description": desc,
        "source_page": source_page,
        "fetched_at": fetched_at
        }

def scrape_details(books):
    records = []
    detail_pages = 0

    for book_url, source_page in books.items():
        cache_name = cache_name_for_book(book_url)
        html, was_fetched = fetch_page(book_url, cache_name)

        if html is None:
            continue

        if was_fetched:
            time.sleep(DELAY_SECONDS)

        record = extract_book(html, book_url, source_page)
        records.append(record)
        detail_pages += 1

    return records, detail_pages

if __name__ == "__main__":
    books, pages_visited, discovered = discover_books(MAX_PAGES)
    print(
        f"catalogue_pages={pages_visited} "
        f"discovered={discovered} "
        f"unique_urls={len(books)}"
    )

    records, detail_pages = scrape_details(books)
    print(json.dumps(records[0], indent=2, ensure_ascii=False))
    print(f"detail_pages={detail_pages}")
