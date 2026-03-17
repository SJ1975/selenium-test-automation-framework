# pages/base_page.py
"""
Base Page
=========
Every Page Object inherits from BasePage so common Selenium helpers
(waiting, clicking, typing) are written exactly once.

DRY principle: Don't Repeat Yourself.
If the wait strategy ever changes, update it here — not in 10 files.
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.config import Config


class BasePage:
    """Shared helpers inherited by every Page Object class."""

    def __init__(self, driver):
        self.driver = driver
        self.wait   = WebDriverWait(driver, Config.EXPLICIT_WAIT)

    # ── Waiting helpers ───────────────────────────────────────────────

    def wait_for_element(self, locator):
        """Wait until element is visible, then return it."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator):
        """Wait until element is visible AND enabled (safe to click)."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def is_element_visible(self, locator, timeout: int = 5) -> bool:
        """Return True if element becomes visible within timeout seconds."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ── Interaction helpers ───────────────────────────────────────────

    def click(self, locator):
        """Wait for element to be clickable, then click it."""
        self.wait_for_clickable(locator).click()

    def type_text(self, locator, text: str):
        """
        Wait for an input field, clear it, then type text.

        Why clear() first?
        Some fields have pre-filled placeholder values or retain text
        from a previous action.  Always clearing ensures a clean state.
        """
        element = self.wait_for_clickable(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator) -> str:
        """Return the visible text of an element."""
        return self.wait_for_element(locator).text

    # ── Navigation helpers ────────────────────────────────────────────

    def navigate_to(self, url: str):
        self.driver.get(url)

    def get_current_url(self) -> str:
        return self.driver.current_url
