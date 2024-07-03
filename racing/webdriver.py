from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


def init_driver(url: str) -> WebDriver:
    web = webdriver.Chrome()
    web.get(url)
    return web
