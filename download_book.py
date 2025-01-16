import os
import sys
import subprocess
import json
import shutil
import requests
import logging
from pathlib import Path
from pathvalidate import sanitize_filename
from seleniumwire import webdriver
from selenium.webdriver.firefox.service import Service as firefox_service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import urllib.parse
from Crypto.Cipher import AES
import gzip
from fake_useragent import UserAgent

from book_metadata import get_book_info
from tg_sender import send_to_telegram
from opf import book_info_to_xml
from common_arguments import create_common_args, check_common_args

logger = logging.getLogger(__name__)

REQUEST_BOOK_INFO_PATTERN = "/ajax/b/"
REQUEST_BOOK_M3U8_PATTERN = "m3u8"


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
def full_book_tmp_filename(dir_path):
    return dir_path / "full_book.mp3"


# Возвращает строку с общими параметрами ffmpeg, которые используются
# во всех командах
def ffmpeg_common_command():
    ffmpeg_log_level = "fatal"
    if logger.root.level == logging.DEBUG:
        ffmpeg_log_level = "debug"
    elif logger.root.level == logging.INFO:
        ffmpeg_log_level = "info"
    elif logger.root.level == logging.WARNING:
        # ffmpeg_log_level = "warning"
        ffmpeg_log_level = "info"
    elif logger.root.level == logging.ERROR:
        ffmpeg_log_level = "error"
    return ["ffmpeg", "-y", "-hide_banner", "-loglevel", ffmpeg_log_level]


# Отрезает от большого файла кусок со временем начала и оеончания
# Делит большой файл на главы. Файл создается без метаданных,
# так как ffmpeg не хочет делать это за один проход
def cut_the_chapter(chapter, input_file, output_folder):
    output_file = output_folder / sanitize_filename(f'no_meta_{chapter["title"]}.mp3')
    logger.warning(
        f'нарезка главы {chapter["title"]} файла {input_file} время '
        f'начала {str(chapter["time_from_start"])} время окончания {str(chapter["time_finish"])}'
    )
    command_cut = ffmpeg_common_command() + [
        "-i",
        input_file,
        "-codec",
        "copy",
        "-ss",
        str(chapter["time_from_start"]),
        "-to",
        str(chapter["time_finish"]),
        output_file,
    ]
    subprocess.run(command_cut)
    return output_file


# Добавляются метаданные в mp3 файл
def create_mp3_with_metadata(
    chapter, no_meta_filename, book_folder, tmp_folder, book_json
):
    cover_filename = get_cover_filename(tmp_folder)
    chapter_path = book_folder / sanitize_filename(f'{chapter["title"]}.mp3')
    logger.warning(f"Создание метаданных для главы: {chapter_path}")
    command_metadata = ffmpeg_common_command() + ["-i", no_meta_filename]
    book_performer = ""
    if "sTextPerformer" in book_json.keys():
        book_performer = BeautifulSoup(book_json["sTextPerformer"], "html.parser").find(
            "a"
        )
        if book_performer is None:
            book_performer = ""
        else:
            book_performer = book_performer.find("span")
            if book_performer is None:
                book_performer = ""
            else:
                book_performer = book_performer.get_text()
    if Path(cover_filename).exists():
        command_metadata = command_metadata + [
            "-i",
            cover_filename,
            "-map",
            "0:0",
            "-map",
            "1:0",
        ]
    command_metadata = command_metadata + [
        "-codec",
        "copy",
        "-id3v2_version",
        "3",
        "-metadata",
        f'title={chapter["title"]}',
        "-metadata",
        f'album={book_json["titleonly"]}',
        "-metadata",
        f'artist={book_json["author"]}',
        "-metadata",
        f'composer={book_json["author"]}',
        "-metadata",
        f"album_artist={book_performer}",
        "-metadata",
        "comment=",
        "-metadata",
        "encoded_by=",
        "-metadata",
        f"TOPE={book_performer}",
        "-metadata",
        "track={0:0>3}/{1:0>3}".format(
            chapter["chapter_number"], chapter["number_of_chapters"]
        ),
        chapter_path,
    ]
    subprocess.run(command_metadata)
    # remove no_meta file
    os.remove(no_meta_filename)


# Загрузка обложки. Сначала стараемся загрузить файл побольше,
# ели не находим берем со страницы
# После загрузки по файлу нужно пройтись ffmpeg и сконвертировать
# в jpeg, так как исходный формат может быть очень разным
def download_cover(book_json, book_soup, tmp_folder):
    cover_url = book_json["preview"]
    cover_filename = get_cover_filename(tmp_folder)
    cover_tmp_filename = tmp_folder / "cover_tmp.jpg"
    big_picture_url = book_soup.find("link", {"rel": "preload", "as": "image"})["href"]
    # try to download big picture
    res = requests.get(big_picture_url, stream=True, headers=get_headers())
    if res.ok:
        res.raw.decode_content = True
        with open(cover_tmp_filename, "wb") as f:
            shutil.copyfileobj(res.raw, f)

    else:
        # big picture not found, try to download preview
        res = requests.get(cover_url, stream=True, headers=get_headers())
        if res.ok:
            res.raw.decode_content = True
            with open(cover_tmp_filename, "wb") as f:
                shutil.copyfileobj(res.raw, f)

    command = ffmpeg_common_command() + ["-i", cover_tmp_filename, cover_filename]
    subprocess.run(command)
    os.remove(cover_tmp_filename)
    return cover_filename


# Открываем в браузере страницу с книгой
def get_book_requests(book_url):
    logger.warning("Старт получения данных о книге")

    executable_path = GeckoDriverManager().install()
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    service = firefox_service(executable_path=executable_path)
    current_webdriver = webdriver.Firefox(service=service, options=options)

    with current_webdriver as driver:
        driver.implicitly_wait(30)
        driver.get(book_url)
        driver.wait_for_request(REQUEST_BOOK_INFO_PATTERN, 30)
        driver.wait_for_request(REQUEST_BOOK_M3U8_PATTERN, 30)
        book_requests = driver.requests
        html = driver.page_source
        driver.close()
        return book_requests, html


# akniga предоставляет медиа в разных форматах. Некоторые страницы
# могут содержать список воспроизведения - файл m3u8.
# Но иногда (редко) список mp3 файлов.
# Это второй случай
def download_book_by_mp3_url(
    mp3_url, book_folder, tmp_folder, book_json, tg_key, tg_chat
):
    mp3_filename = mp3_url.split("/")[-1]
    url_pattern_path = "{0}/".format("/".join(mp3_url.split("/")[0:-1]))
    url_pattern_filename = "." + ".".join(mp3_filename.split(".")[1:])
    filename = None
    count = 0
    chapter_count = 0
    chapters = json.loads(book_json["items"])
    for chapter in chapters:
        chapter_count += 1
        chapter["chapter_number"] = chapter_count
        chapter["number_of_chapters"] = len(chapters)
        # download new file
        if count != chapter["file"]:
            count = chapter["file"]
            # calculate filename
            str_count = "{}".format(count)
            if count < 10:
                str_count = "{:0>2}".format(count)
            filename = tmp_folder / (str_count + url_pattern_filename)
            url_string = url_pattern_path + urllib.parse.quote(
                str_count + url_pattern_filename
            )
            logger.warning("Начало загрузки файла: " + url_string)
            res = requests.get(url_string, stream=True, headers=get_headers())
            if res.ok:
                with open(filename, "wb") as f:
                    shutil.copyfileobj(res.raw, f)
                logger.warning(f"Файл загружен и сохранен как: {filename}")
            else:
                msg = (
                    f"Получен код ошибки: {res.status_code} при загрузке с url: {url_string}. "
                    "Загрузка прервана."
                )
                logger.error(msg)
                send_to_telegram(msg, tg_key, tg_chat)
                exit(0)
        no_meta_filename = cut_the_chapter(chapter, filename, tmp_folder)
        create_mp3_with_metadata(
            chapter, no_meta_filename, book_folder, tmp_folder, book_json
        )


# После загрузки книги, нужно разделить файл на главы
# и снабдить метаданными
def post_processing(book_folder, tmp_folder, book_json):
    chapter_count = 0
    # separate audio file into chapters
    items = json.loads(book_json["items"])
    for chapter in items:
        chapter_count += 1
        chapter["chapter_number"] = chapter_count
        chapter["number_of_chapters"] = len(items)
        no_meta_filename = cut_the_chapter(
            chapter, full_book_tmp_filename(tmp_folder), book_folder
        )
        create_mp3_with_metadata(
            chapter, no_meta_filename, book_folder, tmp_folder, book_json
        )


# Загрузка книги по плэйлисту с помощью программы ffmpeg
# на выходе получаем один большой файл в неизвестном
# (необязательно mp3) формате
def download_book_by_m3u8_with_ffmpeg(m3u8_url, book_folder, tmp_folder, book_json):
    ffmpeg_command = ffmpeg_common_command() + [
        "-i",
        m3u8_url,
        full_book_tmp_filename(tmp_folder),
    ]
    subprocess.run(ffmpeg_command)
    post_processing(book_folder, tmp_folder, book_json)


# Создаем рабочие директории
def create_work_dirs(output_folder, book_json, book_soup, book_url):

    book_json["narrator"] = ""
    bs_narrator = book_soup.find("a", {"rel": "performer"})
    if bs_narrator != None:
        bs_narrator = bs_narrator.find("span")
        if bs_narrator != None:
            book_json["narrator"] = sanitize_filename(bs_narrator.get_text())

    if book_json["narrator"] == "":
        book_dir_name = book_json["titleonly"]
    else:
        book_dir_name = f"{book_json["titleonly"]} - читает {book_json["narrator"]}"

    # sanitize (make valid) book title
    book_json["titleonly"] = sanitize_filename(book_json["titleonly"])
    book_json["author"] = sanitize_filename(book_json["author"])
    book_folder = Path(output_folder) / book_json["author"] / book_dir_name

    bs_series = book_soup.findAll(
        "div", {"class": "caption__article--about-block about--series"}
    )
    if len(bs_series) == 1:
        series_name = bs_series[0].find("a").find("span").get_text().split("(")
        if len(series_name) == 2:
            book_json["series_name"] = sanitize_filename(series_name[0].strip(" "))
            book_json["series_number"] = series_name[1].split(")")[0].strip(" ")
            if len(book_json["series_name"]) > 0:
                book_folder = (
                    Path(output_folder)
                    / book_json["author"]
                    / book_json["series_name"]
                    / f"{book_json['series_number']} - {book_dir_name}"
                )

    # create new folder with book title
    Path(book_folder).mkdir(exist_ok=True, parents=True)

    # create tmp folder. It will be removed
    tmp_folder = book_folder / "tmp"
    Path(tmp_folder).mkdir(exist_ok=True)

    return book_folder, tmp_folder


# Пытаемся найти на странице ссылки на mp3 файлы
def find_mp3_url(book_soup):
    url_mp3 = None
    attr_name = "src"
    for audio_tag in book_soup.findAll("audio"):
        if "src" in audio_tag.attrs:
            url_mp3 = audio_tag.attrs[attr_name]
            break
    return url_mp3


def create_metadata_file(book_folder, book_url):
    filename = Path(book_folder) / "metadata.opf"
    logger.warning(f"Создание файла с метаданными книги {filename}")
    book_info = get_book_info(book_url)
    xml = book_info_to_xml(book_info)
    Path(filename).write_text(xml)


# Загрузка книги
def download_book(book_url, output_folder, tg_key, tg_chat):

    msg = f"Начало загрузки книги с url: {book_url}"
    logger.warning(msg)
    send_to_telegram(msg, tg_key, tg_chat)

    book_requests, book_html = get_book_requests(book_url)
    book_json, m3u8_url = analyse_book_requests(book_requests, tg_key, tg_chat)
    book_soup = BeautifulSoup(book_html, "html.parser")
    book_folder, tmp_folder = create_work_dirs(
        output_folder, book_json, book_soup, book_url
    )

    # download cover picture
    download_cover(book_json, book_soup, tmp_folder)
    # Копируем обложку к основным файлам
    shutil.copyfile(get_cover_filename(tmp_folder), get_cover_filename(book_folder))
    # Создание файла метаданных
    create_metadata_file(book_folder, book_url)

    if m3u8_url is None:  # playlist not found.
        # try to parse html
        mp3_url = find_mp3_url(book_soup)
        if mp3_url is None:
            msg = "Не удалось обнаружить ни файл m3u8, ни файл mp3. Загрузка прервана"
            logger.error(msg)
            send_to_telegram(msg, tg_key, tg_chat)
            exit(0)
        else:
            download_book_by_mp3_url(
                mp3_url, book_folder, tmp_folder, book_json, tg_key, tg_chat
            )
    else:  # it's ordinary case
        download_book_by_m3u8_with_ffmpeg(m3u8_url, book_folder, tmp_folder, book_json)

    msg = f"Книга успешна загружена в каталог: {book_folder}"
    logger.warning(msg)
    send_to_telegram(msg, tg_key, tg_chat)

    # Удаляем каталог временных файлов
    shutil.rmtree(tmp_folder, ignore_errors=True)
    # Устанавливаем права на каталог. Всем полный доступ
    if sys.platform != "win32":
        subprocess.Popen(f"chmod -R ugo+wrX '{str(book_folder)}'", shell=True)

    return book_folder


# Обработка данных со страницы с книгой
def analyse_book_requests(book_requests, tg_key, tg_chat):
    try:
        # find request with book json data
        book_json_requests = [
            r
            for r in book_requests
            if r.method == "POST" and r.path.startswith(REQUEST_BOOK_INFO_PATTERN)
        ]
        # assert that we have only 1 request for book data found
        assert len(book_json_requests) == 1, "Error: Book data not found. Exiting."
        logger.warning("Информация о книге получена")

        # book_json = json.loads(brotli.decompress(book_json_requests[0].response.body))
        resp_body = book_json_requests[0].response.body
        book_json = json.loads(gzip.decompress(resp_body).decode("utf-8"))
        # find request with m3u8 file
        m3u8_file_requests = [
            r for r in book_requests if REQUEST_BOOK_M3U8_PATTERN in r.url
        ]
        m3u8url = None
        if len(m3u8_file_requests) == 1:
            logger.warning("Файл m3u8 найден")
            m3u8url = m3u8_file_requests[0].url
        else:
            logger.warning("Файл m3u8 не найден")
        return book_json, m3u8url
    except AssertionError as message:
        logger.error(message)
        send_to_telegram(message, tg_key, tg_chat)
        exit(0)


# Обработка серии и последовательный запуск книг из серии
def parse_series(series_url, output_folder, tg_key, tg_chat):
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
            download_book(bs_link_soup["href"], output_folder, tg_key, tg_chat)
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
    args = check_common_args(parser, logger)
    logger.info(args)

    if "/series/" in args.url:
        parse_series(args.url, args.output, args.telegram_api, args.telegram_chatid)
    else:
        download_book(args.url, args.output, args.telegram_api, args.telegram_chatid)
