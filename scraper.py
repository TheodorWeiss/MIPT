import os
import sys
import time
import argparse
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://books.toscrape.com/"
OUTPUT_DIR = "artifacts"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "books_data.txt")


def fetch_html(url: str, session: requests.Session) -> str:
    """Скачать HTML страницы, вернуть текст."""
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_page(html: str, base_url: str) -> list[dict]:
    """Разобрать страницу и вернуть список книг со всеми полями."""
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for card in soup.select("article.product_pod"):
        title = card.h3.a.get("title", "").strip()
        price = card.select_one("p.price_color").get_text(strip=True).replace("£", "")
        rating_tag = card.select_one("p.star-rating")
        # во втором классе лежит словесный рейтинг (One, Two, Three, Four, Five)
        rating = ""
        if rating_tag and rating_tag.get("class"):
            # ['star-rating', 'Three'] -> 'Three'
            classes = rating_tag.get("class")
            rating = next((c for c in classes if c != "star-rating"), "")
        availability = soup.select_one("p.instock.availability")
        if availability:
            availability = availability.get_text(strip=True)
        else:
            availability = ""
        rel_link = card.h3.a.get("href", "")
        url = urljoin(base_url, rel_link)

        books.append(
            {
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability,
                "url": url,
            }
        )
    return books


def find_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    """Вернуть URL следующей страницы или None."""
    next_li = soup.select_one("li.next > a")
    if not next_li:
        return None
    return urljoin(current_url, next_li.get("href"))


def save_tsv(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        # шапка
        f.write("title\tprice\trating\tavailability\turl\n")
        for r in rows:
            line = f"{r['title']}\t{r['price']}\t{r['rating']}\t{r['availability']}\t{r['url']}\n"
            f.write(line)


def scrape_books(start_url: str = DEFAULT_URL, max_pages: int | None = None, delay: float = 0.5) -> int:
    """
    Собрать книги, начиная со стартового URL.
    Возвращает количество собранных записей.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    })

    all_rows: list[dict] = []
    current_url = start_url
    pages_done = 0

    while current_url:
        html = fetch_html(current_url, session)
        soup = BeautifulSoup(html, "html.parser")
        # base для относительных ссылок
        base = current_url if current_url.endswith("/") else current_url.rsplit("/", 1)[0] + "/"

        page_rows = parse_page(html, base)
        all_rows.extend(page_rows)
        pages_done += 1

        if max_pages is not None and pages_done >= max_pages:
            break

        next_url = find_next_page_url(soup, current_url)
        current_url = next_url
        if current_url:
            time.sleep(delay)  # быть вежливыми к сайту

    save_tsv(all_rows, OUTPUT_FILE)
    return len(all_rows)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Books scraper (books.toscrape.com)")
    parser.add_argument("--url", default=DEFAULT_URL, help="Стартовый URL (по умолчанию главная)")
    parser.add_argument("--max-pages", type=int, default=None, help="Ограничение по числу страниц")
    args = parser.parse_args(argv)

    try:
        count = scrape_books(start_url=args.url, max_pages=args.max_pages)
        print(f"Saved {count} rows to {OUTPUT_FILE}")
        return 0
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
