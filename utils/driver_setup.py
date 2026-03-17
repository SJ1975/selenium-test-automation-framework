# utils/driver_setup.py
"""
Driver Setup Module
===================
Centralised WebDriver creation with a safety-net fix for the
WinError-193 / wrong-file bug in older webdriver-manager versions.

All tests get their driver via the conftest.py fixture which calls
get_driver() — never call webdriver.Chrome() directly in tests.
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(browser: str = "chrome", headless: bool = False) -> webdriver.Chrome:
    """
    Create and return a configured WebDriver instance.

    Args:
        browser  : Browser name. Currently only 'chrome' is supported.
        headless : Run without a visible window (set True for CI/CD pipelines).

    Returns:
        A ready-to-use Selenium WebDriver.
    """
    if browser.lower() != "chrome":
        raise ValueError(f"Browser '{browser}' is not supported. Use 'chrome'.")

    # ── Chrome options ────────────────────────────────────────────────
    options = Options()

    if headless:
        options.add_argument("--headless=new")   # 'new' headless is stable in Chrome 112+

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")

    # ── Driver path (with WinError-193 safety net) ────────────────────
    driver_path = ChromeDriverManager().install()

    # WinError-193 fix: older WDM versions cache THIRD_PARTY_NOTICES
    # instead of chromedriver.exe on Windows.  If the returned path is
    # not an .exe we walk the folder to find the real binary.
    if os.name == "nt" and not driver_path.endswith(".exe"):
        folder = os.path.dirname(driver_path)
        for fname in os.listdir(folder):
            if fname == "chromedriver.exe":
                driver_path = os.path.join(folder, fname)
                break

    print(f"[INFO] ChromeDriver path: {driver_path}")

    # ── Build driver ──────────────────────────────────────────────────
    service = Service(executable_path=driver_path)
    driver  = webdriver.Chrome(service=service, options=options)

    driver.implicitly_wait(3)        # short fallback; explicit waits are used in pages
    driver.set_page_load_timeout(30)
    driver.maximize_window()

    return driver


def quit_driver(driver: webdriver.Chrome) -> None:
    """
    Safely close all browser windows and kill the WebDriver process.

    driver.quit()  → closes every window AND terminates the driver process
    driver.close() → closes only the current window (process stays alive)
    Always use quit() in teardown to prevent orphaned chromedriver processes.
    """
    if driver:
        driver.quit()
