# tests/test_login.py
"""
Login Test Suite
================
Covers the login module of https://www.saucedemo.com

Test IDs follow the pattern TC_LOGIN_XXX for traceability.
Each test is independent — it opens a fresh browser via the 'driver' fixture.

Positive tests  → verify the happy path works
Negative tests  → verify the system rejects bad input gracefully
"""

import logging
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from utils.config import Config

logger = logging.getLogger(__name__)


class TestLogin:

    # ── Positive tests ────────────────────────────────────────────────

    def test_valid_login(self, driver):
        """
        TC_LOGIN_001  Valid credentials → lands on inventory page.

        Steps:
          1. Enter standard_user / secret_sauce
          2. Click Login
        Expected:
          - Inventory page container is visible
          - Page title reads 'Products'
        """
        login     = LoginPage(driver)
        inventory = InventoryPage(driver)

        login.login(Config.STANDARD_USER, Config.PASSWORD)

        assert inventory.is_loaded(), \
            "Inventory page did not load after valid login"

        title = inventory.get_page_title()
        assert title == "Products", \
            f"Expected title 'Products', got '{title}'"

        logger.info("PASSED  TC_LOGIN_001  valid login → Products page")

    # ── Negative tests ────────────────────────────────────────────────

    def test_invalid_login(self, driver):
        """
        TC_LOGIN_002  Wrong password → error message appears.

        Expected error contains: 'Username and password do not match'
        """
        login = LoginPage(driver)
        login.login(Config.STANDARD_USER, Config.INVALID_PASSWORD)

        assert login.is_error_displayed(), \
            "No error message shown for wrong password"

        msg = login.get_error_message()
        assert "Username and password do not match" in msg, \
            f"Unexpected error text: '{msg}'"

        logger.info("PASSED  TC_LOGIN_002  invalid password → error shown")

    def test_empty_credentials(self, driver):
        """
        TC_LOGIN_003  Submit with no credentials → 'Username is required'.
        """
        login = LoginPage(driver)
        login.click_login()   # click without entering anything

        assert login.is_error_displayed(), \
            "No error shown for empty submission"

        msg = login.get_error_message()
        assert "Username is required" in msg, \
            f"Unexpected error text: '{msg}'"

        logger.info("PASSED  TC_LOGIN_003  empty credentials → error shown")

    def test_empty_password(self, driver):
        """
        TC_LOGIN_004  Username entered but password blank → 'Password is required'.
        """
        login = LoginPage(driver)
        login.enter_username(Config.STANDARD_USER)
        login.click_login()

        assert login.is_error_displayed(), \
            "No error shown for empty password"

        msg = login.get_error_message()
        assert "Password is required" in msg, \
            f"Unexpected error text: '{msg}'"

        logger.info("PASSED  TC_LOGIN_004  empty password → error shown")

    def test_locked_out_user(self, driver):
        """
        TC_LOGIN_005  Locked-out account → specific lock-out error.

        Saucedemo provides locked_out_user to test this scenario.
        Real-world equivalent: account disabled after too many failed attempts.
        """
        login = LoginPage(driver)
        login.login(Config.LOCKED_OUT_USER, Config.PASSWORD)

        assert login.is_error_displayed(), \
            "No error shown for locked-out user"

        msg = login.get_error_message()
        assert "locked out" in msg.lower(), \
            f"Expected lock-out message, got: '{msg}'"

        logger.info("PASSED  TC_LOGIN_005  locked-out user → lock-out error")

    def test_invalid_username(self, driver):
        """
        TC_LOGIN_006  Wrong username → credentials-mismatch error.
        """
        login = LoginPage(driver)
        login.login(Config.INVALID_USER, Config.PASSWORD)

        assert login.is_error_displayed(), \
            "No error shown for invalid username"

        msg = login.get_error_message()
        assert "Username and password do not match" in msg, \
            f"Unexpected error text: '{msg}'"

        logger.info("PASSED  TC_LOGIN_006  invalid username → error shown")
