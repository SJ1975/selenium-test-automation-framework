# conftest.py

import os
import logging
import pytest
from datetime import datetime
from utils.driver_setup import get_driver, quit_driver
from utils.config import Config

# ── Logging setup ─────────────────────────────────────────────────────────────
# encoding="utf-8" on FileHandler prevents UnicodeEncodeError on Windows.
# The terminal stream uses errors="replace" so unknown chars print as ?
# instead of crashing the entire test run.
os.makedirs("reports", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("reports/test_run.log", mode="w", encoding="utf-8"),
    ],
)

# Force the console stream to replace unencodable chars instead of crashing
for handler in logging.root.handlers:
    if isinstance(handler, logging.StreamHandler) and not isinstance(
        handler, logging.FileHandler
    ):
        handler.stream.reconfigure(errors="replace")

logger = logging.getLogger(__name__)


# ── Core driver fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def driver():
    """
    Fresh unauthenticated browser for each test.
    scope="function" = new browser per test = full isolation.
    """
    is_ci = os.getenv("CI", "false").lower() == "true"
    web_driver = get_driver(headless=is_ci)
    web_driver.get(Config.BASE_URL)
    logger.info("Browser opened -> %s", Config.BASE_URL)

    yield web_driver

    logger.info("Closing browser")
    quit_driver(web_driver)


# ── Pre-authenticated driver fixture ─────────────────────────────────────────

@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """
    Browser already logged in as standard_user.
    Cart and checkout tests use this so they don't repeat login logic.
    """
    from pages.login_page import LoginPage

    login = LoginPage(driver)
    login.login(Config.STANDARD_USER, Config.PASSWORD)
    logger.info("Logged in as '%s'", Config.STANDARD_USER)

    yield driver


# ── Screenshot on failure hook ────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture a screenshot whenever a test fails.
    Saved to reports/screenshots/<testname>_<timestamp>.png
    """
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call" and report.failed:
        web_driver = (
            item.funcargs.get("logged_in_driver")
            or item.funcargs.get("driver")
        )
        if web_driver:
            os.makedirs("reports/screenshots", exist_ok=True)
            ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = item.name.replace("[", "_").replace("]", "")
            path      = f"reports/screenshots/{safe_name}_{ts}.png"
            web_driver.save_screenshot(path)
            # No arrow symbol here - plain ASCII only in log messages
            logger.error("FAILED  %s  -> screenshot: %s", item.name, path)