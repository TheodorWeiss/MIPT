# tests/test_scraper.py
import json
from pathlib import Path
import pytest


# Импортируем функции из твоего модуля (замени имя на реальное, если нужно)
# Например, если всё в notebook, а ты экспортировал в scraper.py:
from scraper import get_book_data, scrape_books
# from __main__ import get_book_data, scrape_books  # если тесты гоняются прямо из ноутбука


BOOK_PAGE = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
CATALOG_PAGE1 = "http://books.toscrape.com/catalogue/page-1.html"


def test_get_book_data_structure_and_title():
    data = get_book_data(BOOK_PAGE)
    # базовая структура
    assert isinstance(data, dict)
    for k in ["title", "price", "price_text", "rating", "availability", "description", "product_info"]:
        assert k in data
    # известный заголовок на этой странице
    assert data["title"] == "A Light in the Attic"


@pytest.mark.parametrize("pages,expected", [(1, 20), (2, 40)])
def test_scrape_books_count_by_pages(pages, expected):
    res = scrape_books(CATALOG_PAGE1, is_save=False, return_json=False, page_count=pages, verbose=False)
    assert isinstance(res, list)
    assert len(res) == expected


def test_scrape_books_saves_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Работаем в чистой папке и проверяем сохранение
    monkeypatch.chdir(tmp_path)

    res = scrape_books(CATALOG_PAGE1, is_save=True, return_json=False, page_count=1, verbose=False)
    assert isinstance(res, list)
    assert len(res) == 20

    out_dir = Path.cwd() / "artifacts"
    out_file = out_dir / "books_data.txt"
    assert out_file.exists(), "Файл выгрузки не создан"

    # В файле JSON Lines: по строке на книгу
    lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 20
    # Проверим, что каждая строка — валидный JSON-объект
    for line in lines:
        obj = json.loads(line)
        assert isinstance(obj, dict)
        assert "_source_url" in obj
