import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import logging


logger = logging.getLogger(__name__)


def get_headers():
    ua = UserAgent()
    agent = ua.firefox
    return {
        "User-Agent": agent,
    }


def convert_to_number(number_string):
    res = 0
    try:
        res = int(f'0{number_string.split(" ")[0]}')
    except ValueError as message:
        logger.error(message)
    return res


def convert_to_float(float_string):
    res = 0.0
    try:
        res = float(f'0{float_string.split(" ")[0]}')
    except ValueError as message:
        logger.error(message)
    return res


def find_book_property(book_soup, pattern_string):
    res = None
    field_soup = book_soup.find("div", string=re.compile(pattern_string))
    if not field_soup is None:
        field_soup = field_soup.parent.find("span")
        if not field_soup is None:
            res = field_soup.get_text().replace("\n", "").strip().split(" ")[0]
    return res


def get_book_info(book_url):

    book_info = {
        "url": book_url,
        # "id": "",
        "title": "",
        "author": "",
        "authors": [],
        "narrator": "",
        "narrators": [],
        "series": "",
        # "series_count": 0,
        "series_num": 0,
        "genres": [],
        "cover": "",
        "tags": [],
        "description": "",
        # "isbn": "",
        "publishedYear": "",
        # "publishedDate": "",
        # "uuid": "",
    }

    akniga_url = "https://akniga.org"

    res = requests.get(book_url, headers=get_headers())
    if res.ok:
        book_soup = BeautifulSoup(res.text, "html.parser")

        book_info["cover"] = book_soup.find("link", {"rel": "preload", "as": "image"})[
            "href"
        ]

        # Книга
        title = book_soup.find("div", {"itemprop": "name"})
        if not title is None:
            book_info["title"] = title.get_text().strip()

        description = book_soup.find("div", {"itemprop": "description"})
        if description is None:
            description = ""
        else:
            book_info["description"] = (
                description.get_text().replace("Описание", "").replace("\n", "").strip()
            )

        # Автор
        author_soup = book_soup.find("a", {"rel": "author"})
        if not author_soup is None:
            book_info["author"] = author_soup.get_text().replace("\n", "")
            book_info["authors"].append(book_info["author"])

        # Исполнитель
        performer_soup = book_soup.find("a", {"rel": "performer"})
        if not performer_soup is None:
            book_info["narrator"] = performer_soup.get_text().replace("\n", "")
            book_info["narrators"].append(book_info["narrator"])

        # Серия
        series_soup = book_soup.find("div", {"class": "about--series"})
        if not series_soup is None:
            series_soup = series_soup.find("a")

            series_split = series_soup.get_text().split("(")
            book_info["series"] = series_split[0].replace("\n", "").strip()

            if len(series_split) > 1:
                series_number = (
                    series_split[1].replace(")", "").replace("\n", "").strip()
                )
                book_info["series_num"] = convert_to_float(series_number)

        # Год
        year = find_book_property(book_soup, "Год")
        if not year is None:
            book_info["publishedYear"] = convert_to_number(year)

        # Фильтры/Тэги
        filers_url_prefix = f"{akniga_url}/label/"
        filters_soup = book_soup.find("article", {"itemtype": "http://schema.org/Book"})
        if not filters_soup is None:
            filters_soup = filters_soup.find(
                "div", {"class": "classifiers__article-main"}
            )
        if not filters_soup is None:
            filters_soup = filters_soup.findAll("div")
        if not filters_soup is None:
            for filter_types_soup in filters_soup:
                type_of_filters = (
                    filter_types_soup.next.get_text()
                    .replace("\n", "")
                    .replace(":", "")
                    .strip()
                )
                links_soup = filter_types_soup.findAll("a")
                for link_soup in links_soup:
                    filter_name = link_soup.get_text()
                    # book_info["tags"].append(f"{type_of_filters} {filter_name}")
                    book_info["tags"].append(filter_name)
        # Жанры
        sections_soup = book_soup.findAll("a", {"class": "section__title"})
        if sections_soup is not None:
            for section_soup in sections_soup:
                # section_url = section_soup['href']
                section_name = section_soup.get_text().replace("\n", "").strip()
                book_info["genres"].append(section_name)
        logger.warning(f"Получены метаданные книги - {book_url}")
        return book_info
    else:
        logger.error(f"code: {res.status_code} while get: {book_url}")
        return None
