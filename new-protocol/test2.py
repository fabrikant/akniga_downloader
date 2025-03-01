
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



print(get_m3u_url("https://akniga.org/glubina-pogruzhenie-62-e"))