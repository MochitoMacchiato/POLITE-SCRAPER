import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
        timeout=10,
    )

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
    all_links = []

    while current_url is not None and pages_visited < max_pages:
        cache_name = f"catalogue-page-{pages_visited + 1}.html"
        html, was_fetched = fetch_page(current_url, cache_name)

        if html is None:
            break

        if was_fetched:
            time.sleep(DELAY_SECONDS)

        links, next_url = parse_page(html, current_url)
        all_links.extend(links)

        pages_visited += 1
        current_url = next_url

    unique_links = list(dict.fromkeys(all_links))
    return unique_links, pages_visited, len(all_links)


if __name__ == "__main__":
    unique_links, pages_visited, discovered = discover_books(MAX_PAGES)
    print(
        f"catalogue_pages={pages_visited} "
        f"discovered={discovered} "
        f"unique_urls={len(unique_links)}"
    )