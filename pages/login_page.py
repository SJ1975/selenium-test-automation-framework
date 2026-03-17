# pages/login_page.py
"""
Login Page Object
=================
Represents https://www.saucedemo.com (the login screen).

Locators are stored as class-level tuples so they are easy to find
and update when the UI changes — you never have to hunt through
method bodies.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.config import Config


class LoginPage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────
    USERNAME_FIELD = (By.ID, "user-name")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON   = (By.ID, "login-button")
    ERROR_MESSAGE  = (By.CSS_SELECTOR, "[data-test='error']")
    LOGIN_LOGO     = (By.CLASS_NAME, "login_logo")

    # ── Navigation ────────────────────────────────────────────────────

    def open(self):
        """Navigate to the login page."""
        self.navigate_to(Config.BASE_URL)

    # ── Actions ───────────────────────────────────────────────────────

    def enter_username(self, username: str):
        self.type_text(self.USERNAME_FIELD, username)

    def enter_password(self, password: str):
        self.type_text(self.PASSWORD_FIELD, password)

    def click_login(self):
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        """
        High-level composite method: fills both fields and submits.

        Most tests call login() rather than the three individual methods.
        Individual methods exist for tests that need to interact with
        just one field (e.g. empty-password validation test).
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    # ── Queries ───────────────────────────────────────────────────────

    def get_error_message(self) -> str:
        """Return the error banner text shown after a failed login attempt."""
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self.is_element_visible(self.ERROR_MESSAGE)

    def is_on_login_page(self) -> bool:
        return self.is_element_visible(self.LOGIN_LOGO)
