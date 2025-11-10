# scraper.py
# -*- coding: utf-8 -*-
"""
Учебный парсер Books to Scrape.

Функции:
- get_book_data(book_url) -> dict
- scrape_books(catalog_page1_url, is_save=False, return_json=False, page_count=0, verbose=True)

Совместимо с автотестами:
- ключи в get_book_data в lower-case;
- присутствует product_info (словарь с таблицей характеристик);
- rating — строка '1'..'5';
- каждая сохранённая строка — валидный JSON-объект, содержит "_source_url".
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ==========================
# Настройки HTTP
# ==========================
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 15


# ==========================
# Вспомогательные функции
# ==========================
def _to_float_money(s: Optional[str]) -> Optional[float]:
    """Извлечь число из денежной строки (убираем валюту, пробелы и запятые)."""
    if not s:
        return None
    s = re.sub(r"[^\d.\-]", "", s)  # оставим только цифры/точки/минус
    try:
        return float(s)
    except ValueError:
        return None


def _rating_from_class(tag) -> Optional[str]:
    """Преобразуем CSS-класс star-rating (One..Five) в строку '1'..'5'."""
    if not tag or not tag.get("class"):
        return None
    classes = tag["class"]
    scale = {"One": "1", "Two": "2", "Three": "3", "Four": "4", "Five": "5"}
    for cls in classes:
        if cls in scale:
            return scale[cls]
    return None


def _ensure_artifacts_file() -> Path:
    """Создаём (при необходимости) папку artifacts и возвращаем путь к файлу."""
    root = Path.cwd()
    out_dir = root / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "books_data.txt"


def _mk_page_url(catalog_page1_url: str, n: int) -> str:
    """catalogue/page-1.html -> catalogue/page-{n}.html"""
    return re.sub(r"page-\d+\.html", f"page-{n}.html", catalog_page1_url)


# ==========================
# Основные функции
# ==========================
def get_book_data(book_url: str) -> dict:
    """
    Забрать данные со страницы книги (Books to Scrape).

    Формат возвращаемого словаря (как ожидают тесты):
    {
      'title': str,
      'price': float | None,          # из price_text
      'price_text': str,              # исходная строка с валютой
      'rating': '1'..'5' | '',
      'availability': str,
      'description': str,
      'product_info': dict[str, str], # таблица Product Information
      '_source_url': str              # абсолютный URL страницы
    }
    """
    # нормализуем URL
    if not urlparse(book_url).scheme:
        book_url = urljoin("http://books.toscrape.com/", book_url)

    resp = requests.get(book_url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.select_one(".product_main h1")
    rating_tag = soup.select_one(".product_main p.star-rating")
    desc_tag = soup.select_one("#product_description ~ p")

    # таблица характеристик в dict
    product_info: Dict[str, str] = {}
    for row in soup.select("table.table.table-striped tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            product_info[th.get_text(strip=True)] = td.get_text(strip=True)

    # берём price_text из "Price (incl. tax)" (если нет — из "Price (excl. tax)")
    price_text = (
        product_info.get("Price (incl. tax)")
        or product_info.get("Price (excl. tax)")
        or ""
    )
    price_num = _to_float_money(price_text)

    data = {
        "title": title_tag.get_text(strip=True) if title_tag else "",
        "price": price_num,
        "price_text": price_text,
        "rating": _rating_from_class(rating_tag) or "",
        "availability": product_info.get("Availability", ""),
        "description": desc_tag.get_text(strip=True) if desc_tag else "",
        "product_info": product_info,
        "_source_url": book_url,
    }
    return data


def scrape_books(
    catalog_page1_url: str,
    is_save: bool = False,
    return_json: bool = False,
    page_count: int = 0,
    verbose: bool = True,
) -> List[dict] | str:
    """
    Обходит страницы каталога Books to Scrape, собирает ссылки на книги,
    парсит каждую книгу через get_book_data и возвращает:
      - list[dict], если return_json=False;
      - JSON-строку, если return_json=True.

    Параметры:
      catalog_page1_url : str   URL вида 'http://books.toscrape.com/catalogue/page-1.html'
      is_save           : bool  сохранять ли результат в artifacts/books_data.txt (NDJSON)
      return_json       : bool  вернуть JSON-строку вместо списка словарей
      page_count        : int   сколько страниц обойти (<=0 — обойти до 404/конца каталога)
      verbose           : bool  печатать прогресс
    """
    # --- Сбор ссылок на книги ---
    urls: List[str] = []
    max_pages = page_count if page_count and page_count > 0 else 50

    t0 = time.time()
    for page in range(1, max_pages + 1):
        page_url = _mk_page_url(catalog_page1_url, page)
        r = requests.get(page_url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 404:
            if verbose:
                print(f"Страница {page} вернула 404 — остановка.")
            break
        r.raise_for_status()
        if verbose:
            print(f"Обработаны ссылки со страницы №{page}")

        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("article.product_pod h3 a"):
            href = a.get("href", "")
            urls.append(urljoin(page_url, href))

    if verbose:
        print(f"Время обработки ссылок: {time.time() - t0:.2f} сек.")
        print(f"Всего найдено URL книг для парсинга: {len(urls)}")
        print("Начинаю парсинг")

    # --- Парсинг книг ---
    books: List[dict] = []
    t1 = time.time()
    for u in urls:
        try:
            books.append(get_book_data(u))
        except Exception:
            # не валимся на одной неудачной книге
            continue

    if verbose and (time.time() - t1) > 0:
        dt = time.time() - t1
        speed = len(books) / dt if dt > 0 else 0
        print(f"Время парсинга книг: {dt:.2f} сек.")
        print(f"Средняя скорость: {speed:.2f} книг/сек")

    # --- Сохранение ---
    if is_save:
        out_path = _ensure_artifacts_file()
        if return_json:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(books, ensure_ascii=False, indent=2))
        else:
            # NDJSON: одна книга = одна строка JSON
            with open(out_path, "w", encoding="utf-8") as f:
                for obj in books:
                    if "_source_url" not in obj:
                        obj["_source_url"] = ""
                    f.write(json.dumps(obj, ensure_ascii=False))
                    f.write("\n")

    # --- Возврат результата ---
    if return_json:
        return json.dumps(books, ensure_ascii=False)
    return books
