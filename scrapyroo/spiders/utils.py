from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore

import time

def get_chrome_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    return webdriver.Chrome(chrome_options=options)

def scrape_dynamic(url: str, wait=None, *args, **kwargs) -> str:
    driver = get_chrome_driver(*args, **kwargs)
    try:
        driver.get(url)
        if wait is not None:
            time.sleep(wait)
        return driver.page_source
    finally:
        driver.quit()
