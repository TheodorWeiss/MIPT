````markdown
# 📚 Books Scraper  

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.x-green?logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-2.x-orange?logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/tests-passed-brightgreen?logo=pytest)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

*A training project for web scraping using Python and BeautifulSoup.*  

---

## 🎯 Цель проекта  
Учебный проект по парсингу данных с сайта [Books to Scrape](http://books.toscrape.com/).  
Скрипт автоматически собирает информацию о книгах — названия, рейтинги, описания, цены и характеристики из таблицы Product Information.

---

## 🧩 Используемые библиотеки  
- `requests`  
- `beautifulsoup4`  
- `schedule`  
- `pytest`  

---

## 🚀 Установка и запуск  

### 1️⃣ Установка зависимостей  
```bash
pip install -r requirements.txt
````

### 2️⃣ Использование

```python
from scraper import scrape_books

# Пример 1: парсинг одной страницы без сохранения
data = scrape_books(
    catalog_page1_url="http://books.toscrape.com/catalogue/page-1.html",
    page_count=1,
    return_json=True
)
print(data[:200])  # часть результата

# Пример 2: парсинг нескольких страниц с сохранением результатов в файл
scrape_books(
    catalog_page1_url="http://books.toscrape.com/catalogue/page-1.html",
    is_save=True,
    page_count=5
)
```

После выполнения результат сохраняется в папке **`artifacts/books_data.txt`**
в формате JSON Lines (по одной книге на строку).

---

## 🕒 Автоматический запуск (планировщик)

Функцию можно настроить на ежедневный запуск с помощью `schedule`:

```python
import schedule
import time
from scraper import scrape_books

catalog_url = "http://books.toscrape.com/catalogue/page-1.html"

schedule.every().day.at("19:00").do(
    scrape_books,
    catalog_url,
    is_save=True,
    return_json=True,
    page_count=5,
)

while True:
    schedule.run_pending()
    time.sleep(5)
```

---

## 🧪 Тестирование

```bash
pytest tests/ -v
```

Все тесты проверяют корректность структуры данных, количество книг и работу сохранения файла.

---

## 🧾 Пример вывода JSON

```json
[
  {
    "Name": "A Light in the Attic",
    "Rating": "3",
    "Description": "It's hard to imagine a world without A Light in the Attic...",
    "UPC": "a897fe39b1053632",
    "Product Type": "Books",
    "Price (excl. tax)": "£51.77",
    "Price (incl. tax)": "£51.77",
    "Tax": "£0.00",
    "Availability": "In stock (22 available)",
    "Number of reviews": "0"
  }
]
```

---

## 🗂️ Структура проекта

```
hw-books-parser/
├─ artifacts/
│  └─ books_data.txt
├─ tests/
│  └─ test_scraper.py
├─ scraper.py
├─ requirements.txt
├─ README.md
└─ notebook.ipynb
```

---

📚 *This project was created for educational purposes as part of the “Programming in Python” course at MIPT (Moscow Institute of Physics and Technology).*

```