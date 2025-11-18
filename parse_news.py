from pathlib import Path
from typing import Dict, List
import json

from bs4 import BeautifulSoup


INPUT_FILE = "news.html"


def load_html(path: str) -> str:
    """
    Загружает HTML из файла.

    path: имя файла (по умолчанию news.html в папке проекта).
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            "Файл 'news.html' не найден. "
            "Сначала скачайте страницу из WebArchive и сохраните её как news.html "
            "в папку проекта news_parser."
        )
    return file_path.read_text(encoding="utf-8")


def parse_news(html: str) -> Dict[str, List[dict]]:
    """
    Парсит HTML страницы новостей iz.ru и группирует новости по рубрикам.

    Возвращает словарь вида:
    {
        "Общество": [
            {"title": "...", "description": "...", "url": "...", "datetime": "...", "time_text": "..."},
            ...
        ],
        "Армия": [ ... ],
        ...
    }
    """
    soup = BeautifulSoup(html, "lxml")

    result: Dict[str, List[dict]] = {}

    # Каждый блок новости выглядит как div.node__cart__item.show_views_and_comments
    for item in soup.select("div.node__cart__item.show_views_and_comments"):
        # ----- Рубрика (Общество, Армия, Здоровье и т.п.) -----
        rubric_link = item.select_one(
            "div.node__cart__item__category_news div a"
        )
        if rubric_link is None:
            continue
        category = rubric_link.get_text(strip=True)

        # ----- Ссылка на новость -----
        link_tag = item.select_one("a.node__cart__item__inside")
        if link_tag is None:
            continue
        url = link_tag.get("href", "").strip()

        # Внутренний блок с текстом
        info = link_tag.select_one("div.node__cart__item__inside__info")
        if info is None:
            continue

        # ----- Заголовок -----
        title_span = info.select_one(
            "div.node__cart__item__inside__info__title span"
        )
        title = title_span.get_text(strip=True) if title_span else ""

        # ----- Краткое описание (может быть пустым) -----
        desc_div = info.select_one(
            "div.node__cart__item__inside__info__description"
        )
        description = desc_div.get_text(strip=True) if desc_div else ""

        # ----- Время -----
        time_tag = info.select_one("time")
        datetime_iso = (
            time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else ""
        )
        time_text = time_tag.get_text(strip=True) if time_tag else ""

        news_item = {
            "title": title,
            "description": description,
            "url": url,
            "datetime": datetime_iso,
            "time_text": time_text,
        }

        # Добавляем новость в нужную рубрику
        if category not in result:
            result[category] = []
        result[category].append(news_item)

    return result


def main() -> None:
    # 1. Читаем HTML
    html = load_html(INPUT_FILE)

    # 2. Парсим новости
    grouped_news = parse_news(html)

    # 3. Краткая сводка по рубрикам
    print("Найдено новостей по рубрикам:")
    for category, items in grouped_news.items():
        print(f"- {category}: {len(items)}")

    # 4. Красиво печатаем структуру (как JSON)
    print("\nСтруктура данных:")
    print(json.dumps(grouped_news, ensure_ascii=False, indent=2))

    # 5. Сохраняем в файл
    output_path = Path("news_parsed.json")
    output_path.write_text(
        json.dumps(grouped_news, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nРезультат сохранён в {output_path.resolve()}")


if __name__ == "__main__":
    main()