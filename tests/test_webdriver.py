import os
from selenium import webdriver

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__)[:-6])
DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/chromedriver")

def test_webdriver():
    browser = webdriver.Chrome(executable_path = DRIVER_BIN)
    browser.get('http://www.google.com/')