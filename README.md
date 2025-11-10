# 📚 Books Scraper

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Requests](https://img.shields.io/badge/Requests-HTTP%20client-brightgreen)
![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-HTML%20parser-orange)
![Pytest](https://img.shields.io/badge/tests-pytest-success)

Учебный проект по парсингу каталога **[Books to Scrape](http://books.toscrape.com/)**.  
Скрипт собирает по каждой книге: название, рейтинг, описание, цены и характеристики из блока **Product Information**.  
Есть сохранение результата в файл и автотесты.

## 🚀 Возможности

- Парсинг всех страниц каталога или заданного количества страниц;
- Возврат результата в виде **списка словарей** или **JSON-строки**;
- Сохранение выгрузки в `artifacts/books_data.txt` (по одной JSON-строке на книгу);
- Подробный лог прогресса (страницы, время, скорость);
- Регулярный запуск по расписанию через `schedule`.

## 🗂 Структура репозитория

```text
.
├─ artifacts/
│  └─ books_data.txt          # пример выгрузки (может отсутствовать до первого запуска)
├─ notebooks/
│  └─ HW_03_python_ds_2025.ipynb
├─ tests/
│  └─ test_scraper.py         # автотесты (pytest)
├─ .gitignore
├─ README.md
├─ requirements.txt
└─ scraper.py                 # основной скрипт


```

> Основная ветка репозитория: **main**. Рабочие изменения вносились в **hw-books-parser** и затем сливались PR в `main`.

---

## ⚙️ Установка

1) Клонирование репозитория:
```bash
git clone https://github.com/<your_user>/hw-books-parser.git
cd hw-books-parser
````

2. (Рекомендация) Создать и активировать виртуальное окружение:

```bash
python -m venv .venv
# Windows (Git Bash/CMD):
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
```

3. Установить зависимости:

```bash
pip install -r requirements.txt
```

---

## 🔧 Использование

### Вариант 1: быстрый пример

```python
from scraper import scrape_books

catalog_url = "http://books.toscrape.com/catalogue/page-1.html"

# Вернуть JSON-строку по двум страницам и сохранить копию в artifacts/books_data.txt
data_json = scrape_books(
    catalog_page1_url=catalog_url,
    page_count=2,
    return_json=True,
    is_save=True,
    verbose=True,
)

print(data_json[:600], "...")
```

**Аргументы `scrape_books`:**

* `catalog_page1_url: str` — URL 1-й страницы каталога
* `page_count: int = 0` — сколько страниц парсить (`0` = до последней)
* `return_json: bool = False` — вернуть JSON-строку вместо списка
* `is_save: bool = False` — сохранять результат в `artifacts/books_data.txt`
* `verbose: bool = True` — печатать ход выполнения

---

## ⏰ Регулярный запуск (schedule)

Ежедневно в **19:00**:

```python
import schedule
import time
from scraper import scrape_books

catalog_url = "http://books.toscrape.com/catalogue/page-1.html"

schedule.every().day.at("19:00").do(
    scrape_books,
    catalog_page1_url=catalog_url,
    page_count=5,
    is_save=True,
    return_json=True,
    verbose=True,
)

while True:
    schedule.run_pending()
    time.sleep(1)
```

> Для локальной проверки можно заменить на `schedule.every(1).minutes.do(...)`.

---

## 🧪 Тесты

Запуск из корня репозитория:

**Windows (Git Bash / CMD):**

```bash
set PYTHONPATH=. && python -m pytest -v tests/test_scraper.py
```

**macOS / Linux:**

```bash
PYTHONPATH=. python -m pytest -v tests/test_scraper.py
```

Ожидаемо: `4 passed`.

---

## 📦 Формат выгрузки

Файл `artifacts/books_data.txt` содержит **по одной валидной JSON-строке на книгу**.
Ключевые поля:
`Name`, `Rating` (`"1"`…`"5"`), `Description`, `UPC`, `Product Type`,
`Price (excl. tax)`, `Price (incl. tax)`, `Tax`, `Availability`, `Number of reviews`, `_source_url`.

---

## 📄 Лицензия

Проект создан в учебных целях. Использование **Books to Scrape** разрешено для практики парсинга.

---

