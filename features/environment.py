"""
Environment for Behave Testing
"""

import os
import shutil
import requests
from behave import given  # noqa: F401
from selenium import webdriver

WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "60"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
DRIVER = os.getenv("DRIVER", "chrome").lower()


def before_all(context):
    """Executed once before all tests"""
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS

    if DRIVER == "firefox":
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()

    context.driver.implicitly_wait(context.wait_seconds)


def after_all(context):
    """Executed after all tests"""
    context.driver.quit()


######################################################################
# Utility functions to create web drivers
######################################################################
def get_chrome():
    """Creates a headless Chrome browser"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,1300")
    # Find Chromium binary (works across Debian, Ubuntu, Alpine, etc.)
    for binary in ["chromium", "chromium-browser", "google-chrome"]:
        path = shutil.which(binary)
        if path:
            options.binary_location = path
            break
    return webdriver.Chrome(options=options)


def get_firefox():
    """Creates a headless Firefox browser"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)
