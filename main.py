import requests
from pathlib import Path

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"
URL = "https://books.toscrape.com/catalogue/page-1.html"
USER_AGENT = "FlyRankInternship-A9/1.0 (https://github.com/MochitoMacchiato/POLITE-SCRAPER.git)"


def fetch_page():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists():
        html = CACHE_FILE.read_text(encoding="utf-8")
        print(f"CACHE HIT size={len(html)}")
        return html

    response = requests.get(
        URL,
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )

    if response.status_code != 200:
        print(f"FETCH FAILED status={response.status_code}")
        return None

    html = response.text
    CACHE_FILE.write_text(html, encoding="utf-8")
    print(f"FETCH size={len(html)}")
    return html


if __name__ == "__main__":
    fetch_page()