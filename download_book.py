import os
import sys
import subprocess
import shutil
import requests
import logging
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from tg_sender import send_to_telegram
from opf import book_info_to_xml
from common_arguments import create_common_args, parse_args
from pydub import AudioSegment


logger = logging.getLogger(__name__)

from seleniumwire import webdriver
from selenium.webdriver.firefox.service import Service as firefox_service
from webdriver_manager.firefox import GeckoDriverManager
import time


def get_firefox_driver():
    executable_path = GeckoDriverManager().install()
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    service = firefox_service(executable_path=executable_path)
    return webdriver.Firefox(service=service, options=options)


def get_m3u_url(book_url):
    current_webdriver = get_firefox_driver()
    with current_webdriver as driver:
        driver.implicitly_wait(40)
        driver.get(book_url)
        time.sleep(15)
        book_requests = driver.requests

        m3u8_file_requests = [r for r in book_requests if "m3u8" in r.url]
        m3u8url = None
        if len(m3u8_file_requests) == 1:
            m3u8url = m3u8_file_requests[0].url

        return m3u8url


# Возвращает заготовку заголовков для запросов
def get_headers():
    ua = UserAgent()
    agent = ua.firefox
    return {
        "User-Agent": agent,
    }


# Путь к файлу с обложкой
def get_cover_filename(dir_path):
    return dir_path / "cover.jpg"


# Путь к файлу с полной неразделенной на главы
# книгой
def full_book_filename(dir_path):
    return dir_path / "full_book.mp3"


# Возвращает строку с общими параметрами ffmpeg, которые используются
# во всех командах
def ffmpeg_common_command():
    ffmpeg_log_level = "fatal"
    if logger.level == logging.DEBUG:
        ffmpeg_log_level = "debug"
    elif logger.level == logging.INFO:
        ffmpeg_log_level = "info"
    elif logger.level == logging.WARNING:
        # ffmpeg_log_level = "warning"
        ffmpeg_log_level = "info"
    elif logger.level == logging.ERROR:
        ffmpeg_log_level = "error"
    return ["ffmpeg", "-y", "-hide_banner", "-loglevel", ffmpeg_log_level]


# Загрузка обложки.
# После загрузки по файлу нужно пройтись ffmpeg и сконвертировать
# в jpeg, так как исходный формат может быть очень разным
def download_cover(book_info, tmp_folder):
    logger.debug(f"Начало загрузки файла обложки с url: {book_info["cover"]}")
    cover_filename = get_cover_filename(tmp_folder)
    res = requests.get(book_info["cover"], stream=True, headers=get_headers())
    if res.ok:
        res.raw.decode_content = True
        with open(cover_filename, "wb") as f:
            shutil.copyfileobj(res.raw, f)
    else:
        msg = (
            f"Ошибка {res.status_code} при загрузке файла обложки {book_info['cover']}."
        )
        logger.error(msg)
    logger.debug(f"Обложка сохранена в файл: {cover_filename}")
    return cover_filename


# После загрузки книги, нужно разделить файл на главы
# и снабдить метаданными
def post_processing(book_folder, book_info):
    logger.info(f"Разбивка на главы книги: {book_info['title']}")
    full_book_fname = str(full_book_filename(book_folder))

    cover_path = get_cover_filename(book_folder)
    if os.path.isfile(cover_path):
        cover_path = str(cover_path)
    else:
        cover_path = None

    next_idx = 0
    chapters_count = len(book_info["chapters"])
    for chapter in book_info["chapters"]:

        next_idx += 1
        output_file = book_folder / sanitize_filename(f'{chapter["title"]}.mp3')
        tags = {
            "title": chapter["title"],
            "album": book_info["title"],
            "artist": book_info["author"],
            "composer": book_info["author"],
            "album_artist": book_info["narrator"],
            "comments": "",
            "TOPE": book_info["narrator"],
            "track": "{0:0>3}/{1:0>3}".format(chapter["number"], chapters_count),
            "encoded_by": "",
        }

        logger.info(f"Начало обработки главы {next_idx} из {chapters_count}")
        start_time = int(chapter["start_time"])
        duration = None
        if next_idx < chapters_count:
            end_time = int(book_info["chapters"][next_idx]["start_time"])
            duration = end_time - start_time

        AudioSegment.from_file(
            full_book_fname,
            start_second=start_time,
            duration=duration,
        ).export(output_file, format="mp3", tags=tags, cover=cover_path)

        logger.info(f"Окончание обработки главы {next_idx} из {chapters_count}")


# Загрузка книги по плэйлисту с помощью программы ffmpeg
# на выходе получаем один большой файл в неизвестном
# (необязательно mp3) формате
def download_book_by_m3u8_with_ffmpeg(m3u8_url, book_folder, book_info):
    logger.info(f"Начало загрузки книги по плейлисту: {m3u8_url}")
    ffmpeg_command = ffmpeg_common_command() + [
        "-i",
        m3u8_url,
        full_book_filename(book_folder),
    ]
    subprocess.run(ffmpeg_command)
    logger.info(f"Окончание загрузки книги по плейлисту: {m3u8_url}")
    post_processing(book_folder, book_info)


# Создаем рабочие директории
def create_work_dirs(output_folder, book_info):
    logger.debug("Создание каталога загрузки")
    book_and_reader = book_info["title"]
    if book_info["narrator"] != "":
        book_and_reader = f'{book_and_reader} - читает {book_info["narrator"]}'
    book_folder = (
        Path(output_folder)
        / sanitize_filename(book_info["author"])
        / sanitize_filename(book_and_reader)
    )
    Path(book_folder).mkdir(exist_ok=True, parents=True)
    logger.debug(f"Установлен каталог для загрузки: {book_folder}")

    return book_folder


def get_book_info(book_url, tg_key, tg_chat):
    book_info = {
        "url": book_url,
        "id": "",
        "title": "_",
        "author": "_",
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
    res = requests.get(book_url, headers=get_headers())
    if not res.ok:
        msg = f"Ошибка {res.status_code} при загрузке страницы книги {book_url}."
        send_to_telegram(msg, tg_key, tg_chat)
        logger.error(msg)
        exit(0)

    book_html = res.text
    bs_book = BeautifulSoup(book_html, "html.parser")

    m3u8_url = ""
    server = ""
    bs_server = bs_book.find("div", {"class": "preconnect"})
    if not bs_server is None:
        server = bs_server.find("link", {"rel": "preconnect"})["href"]
    book_id = bs_book.find("article")["data-bid"]

    if server != "":
        # m3u8_url = f"{server}b/{book_id}/pl.m3u8?res=2"
        m3u8_url = get_m3u_url(book_url)
    else:
        msg = (
            f"На странице книги {book_url} не обнаружен тэг <link> c атрибутом rel='preconnect'."
            " Возможно книга недоступна для свободного прослушивания."
        )
        send_to_telegram(msg, tg_key, tg_chat)
        logger.error(msg)
        exit(0)

    # book_info["id"] = book_id
    book_info["title"] = (
        bs_book.find("div", {"class": "book--header"})
        .find("div", {"itemprop": "name"})
        .get_text()
    )

    description = bs_book.find("div", {"itemprop": "description"}).get_text()
    description = description.replace("Описание", "").replace("<br>", "\n").strip()
    book_info["description"] = description

    bs_authors = bs_book.find_all("span", {"itemprop": "author"})
    if not bs_authors is None:
        for bs_author in bs_authors:
            book_info["authors"].append(bs_author.get_text().strip())
        book_info["author"] = book_info["authors"][0]
    else:
        logger.warning(f"Не найден автор {book_url}")

    bs_narrators = bs_book.find_all("a", {"rel": "performer"})
    if not bs_narrators is None:
        for bs_narrator in bs_narrators:
            book_info["narrators"].append(bs_narrator.get_text().strip())
        book_info["narrator"] = book_info["narrators"][0]
    else:
        logger.warning(f"Не найден исполнитель {book_url}")

    bs_series = bs_book.find("a", {"class": "link__series"})
    if not bs_series is None:
        series_list = bs_series.get_text().split("(")
        book_info["series"] = series_list[0].strip()
        if len(series_list) > 1:
            book_info["series_num"] = series_list[1].replace(")", "").strip()

    bs_cover = bs_book.find("div", {"class": "book--cover"})
    if not bs_cover is None:
        bs_cover = bs_cover.find("img")
        if not bs_cover is None:
            book_info["cover"] = bs_cover["src"]

    if bs_cover is None:
        logger.warning(f"Не найдена обложка {book_url}")

    bs_genres = bs_book.find_all("a", {"class": "section__title"})
    if not bs_genres is None:
        for bs_genre in bs_genres:
            book_info["genres"].append(bs_genre.get_text().strip().lower())

    if bs_genres is None:
        logger.warning(f"Не найдены жанры {book_url}")

    bs_tags = bs_book.find("div", {"class": "classifiers__article-main"})
    if not bs_tags is None:
        bs_tags = bs_tags.find_all("div")
        if not bs_tags is None:
            for bs_tag in bs_tags:
                tag_name = bs_tag.contents[0].replace("\n", "").strip().lower()
                for bs_tag_value in bs_tag.find_all("a"):
                    tag_value = bs_tag_value.get_text().strip().lower()
                    tag_value = " ".join(tag_value.split())
                    book_info["tags"].append(f"{tag_name} {tag_value}")

    if bs_tags is None:
        logger.warning(f"Не найдены тэги {book_url}")

    bs_tmps = bs_book.find_all("div", {"class": "caption__article--about-block"})
    if not bs_tmps is None:
        for bs_tmp in bs_tmps:
            year_str = bs_tmp.get_text().lower()
            if "год" in year_str:
                year_str = year_str.replace("год", "").strip()
                book_info["publishedYear"] = year_str

    chapters = []
    bs_chapters = bs_book.find(
        "div", {"class": "player--chapters", "data-bid": book_id}
    )
    if not bs_chapters is None:
        bs_chapters = bs_chapters.find_all("div", {"class": "chapter__default"})
        if not bs_chapters is None:
            for bs_chapter in bs_chapters:
                title = (
                    bs_chapter.find("div", {"class": "chapter__default--title"})
                    .get_text()
                    .strip()
                )
                chapters.append(
                    {
                        "number": bs_chapter["data-id"],
                        "title": title,
                        "start_time": bs_chapter["data-pos"],
                    }
                )

    if bs_chapters is None:
        msg = f"Не найден список глав {book_url}"
        send_to_telegram(msg, tg_key, tg_chat)
        logger.error(msg)
        exit(0)

    book_info["chapters"] = chapters

    return book_info, m3u8_url


# Загрузка книги
def download_book(
    book_url, output_folder, tg_key, tg_chat, load_cover, create_metadata
):

    msg = f"Начало загрузки книги с url: {book_url}"
    logger.warning(msg)
    send_to_telegram(msg, tg_key, tg_chat)
    book_info, m3u8_url = get_book_info(book_url, tg_key, tg_chat)
    book_folder = create_work_dirs(output_folder, book_info)

    # Загружаем обложку в любом случае, так как она понадобится для установки
    # метаданных в mp3 файлы
    download_cover(book_info, book_folder)

    # Создание файла метаданных
    if create_metadata:
        filename = Path(book_folder) / "metadata.opf"
        logger.debug(f"Начало создания файла {filename} с метаданными книги")
        xml = book_info_to_xml(book_info)
        Path(filename).write_text(xml)
        logger.debug(f"Создан файл {filename} с метаданными книги")
    else:
        logger.debug("Создание файла метаданных не требуется")

    download_book_by_m3u8_with_ffmpeg(m3u8_url, book_folder, book_info)

    msg = (
        f"Окончание загрузки книги:\n{book_info['title']}\nавтор: {book_info['author']}"
    )
    logger.warning(msg)
    send_to_telegram(msg, tg_key, tg_chat)

    # Удаляем ненужные файлы
    book_fname = full_book_filename(book_folder)
    if os.path.isfile(book_fname):
        os.remove(book_fname)
    cover_fname = get_cover_filename(book_folder)
    if not load_cover and os.path.isfile(cover_fname):
        os.remove(cover_fname)
    # Устанавливаем права на каталог. Всем полный доступ
    if sys.platform != "win32":
        subprocess.Popen(f"chmod -R ugo+wrX '{str(book_folder)}'", shell=True)

    return book_folder


# Обработка серии и последовательный запуск книг из серии
def parse_series(
    series_url, output_folder, tg_key, tg_chat, load_cover, create_metadata
):
    msg = "Начата загрузка серии"
    logger.warning(msg)
    send_to_telegram(msg, tg_key, tg_chat)
    res = requests.get(series_url, headers=get_headers())
    if res.ok:
        series_soup = BeautifulSoup(res.text, "html.parser")
        bs_links_soup = series_soup.find(
            "div", {"class": "content__main__articles"}
        ).findAll("a", {"class": "content__article-main-link tap-link"})
        for bs_link_soup in bs_links_soup:
            download_book(
                bs_link_soup["href"],
                output_folder,
                tg_key,
                tg_chat,
                load_cover,
                create_metadata,
            )
    else:
        logger.error(
            f"Получен код ошибки: {res.status_code} при загрузке с url: {series_url}"
        )


# Точка входа в программу
if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    # Создаем общие аргументы для всех качалок
    parser = create_common_args(f"Загрузчик книг с сайта akniga.org")
    args = parse_args(parser, logger)
    logger.info(args)

    if "/series/" in args.url:
        parse_series(
            args.url,
            args.output,
            args.telegram_api,
            args.telegram_chatid,
            args.cover,
            args.metadata,
        )
    else:
        download_book(
            args.url,
            args.output,
            args.telegram_api,
            args.telegram_chatid,
            args.cover,
            args.metadata,
        )
