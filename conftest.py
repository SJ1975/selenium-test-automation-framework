# conftest.py
"""
PyTest Shared Fixtures
======================
conftest.py is automatically loaded by PyTest before any tests run.
Fixtures defined here are available to EVERY test file in the project
without any import statement.

Two fixtures are provided:

  driver           → fresh browser for each test (use in login tests)
  logged_in_driver → already authenticated browser  (use in cart / checkout tests)

The 'yield' keyword splits each fixture into:
  - Everything BEFORE yield  = setup   (runs before the test)
  - Everything AFTER  yield  = teardown (runs after the test, even on failure)
"""

import os
import logging
import pytest
from datetime import datetime
from utils.driver_setup import get_driver, quit_driver
from utils.config import Config

# ── Logging ──────────────────────────────────────────────────────────────────
os.makedirs("reports", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("reports/test_run.log", mode="w"),
    ],
)
logger = logging.getLogger(__name__)


# ── Core driver fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def driver():
    """
    Provide a fresh, unauthenticated browser for each test.

    scope="function" means a new browser is started before every test
    and closed after it.  Tests are fully isolated — one test's actions
    cannot affect another.

    headless mode: set to True when the CI environment variable is present
    so the same code runs locally (visible) and in GitHub Actions (headless).
    """
    is_ci = os.getenv("CI", "false").lower() == "true"
    web_driver = get_driver(headless=is_ci)
    web_driver.get(Config.BASE_URL)
    logger.info("Browser opened → %s", Config.BASE_URL)

    yield web_driver  # ← test runs here

    logger.info("Closing browser")
    quit_driver(web_driver)


# ── Pre-authenticated driver fixture ─────────────────────────────────────────

@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """
    Provide a browser that is already logged in as standard_user.

    Reuses the 'driver' fixture and performs login on top of it.
    Cart and checkout tests start from the inventory page — they should
    not repeat login logic in every test.  Using this fixture keeps
    each test focused on its own module.

    The driver fixture handles browser teardown, so no extra cleanup
    is needed here.
    """
    from pages.login_page import LoginPage

    login = LoginPage(driver)
    login.login(Config.STANDARD_USER, Config.PASSWORD)
    logger.info("Logged in as '%s'", Config.STANDARD_USER)

    yield driver  # ← test runs here (browser is on /inventory.html)


# ── Screenshot on failure hook ────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Automatically capture a screenshot when any test fails.

    pytest hooks let you plug into PyTest's lifecycle.
    hookwrapper=True means we wrap around the normal report creation
    so we can inspect its outcome.

    Screenshots are saved to reports/screenshots/<testname>_<timestamp>.png
    and are attached to the HTML report automatically.
    """
    outcome = yield
    report  = outcome.get_result()

    # Only act on the main test call phase that failed
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
            logger.error("FAILED  %s  →  screenshot: %s", item.name, path)
