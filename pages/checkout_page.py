# pages/checkout_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.config import Config


class CheckoutPage(BasePage):

    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT  = (By.ID, "last-name")
    ZIP_INPUT        = (By.ID, "postal-code")
    CONTINUE_BTN     = (By.ID, "continue")
    ERROR_MESSAGE    = (By.CSS_SELECTOR, "[data-test='error']")

    FINISH_BTN       = (By.ID, "finish")
    TOTAL_LABEL      = (By.CLASS_NAME, "summary_total_label")
    CANCEL_BTN       = (By.ID, "cancel")

    CONFIRM_HEADER   = (By.CLASS_NAME, "complete-header")
    BACK_HOME_BTN    = (By.ID, "back-to-products")
    PAGE_TITLE       = (By.CLASS_NAME, "title")

    def _wait_for_url(self, fragment: str):
        """Wait until the current URL contains the expected fragment."""
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.url_contains(fragment)
        )

    # ── Step 1 ────────────────────────────────────────────────────────

    def fill_shipping_info(self, first: str, last: str, zip_code: str):
        """
        Fill the checkout info form and click Continue.

        _wait_for_url("checkout-step-one") is called first because
        proceed_to_checkout() in CartPage already waits for this URL —
        so in practice this resolves instantly. It is kept here as a
        defensive guard in case fill_shipping_info() is ever called
        directly without going through CartPage.
        """
        self._wait_for_url("checkout-step-one")

        if first:
            self.type_text(self.FIRST_NAME_INPUT, first)
        if last:
            self.type_text(self.LAST_NAME_INPUT, last)
        if zip_code:
            self.type_text(self.ZIP_INPUT, zip_code)

        self.click(self.CONTINUE_BTN)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self.is_element_visible(self.ERROR_MESSAGE)

    # ── Step 2 ────────────────────────────────────────────────────────

    def get_total_price(self) -> str:
        self._wait_for_url("checkout-step-two")
        return self.get_text(self.TOTAL_LABEL)

    def click_finish(self):
        self._wait_for_url("checkout-step-two")
        self.click(self.FINISH_BTN)

    def click_cancel(self):
        self.click(self.CANCEL_BTN)

    # ── Step 3 ────────────────────────────────────────────────────────

    def get_confirmation_header(self) -> str:
        self._wait_for_url("checkout-complete")
        return self.get_text(self.CONFIRM_HEADER)

    def is_order_confirmed(self) -> bool:
        try:
            self._wait_for_url("checkout-complete")
            el = self.wait_for_element(self.CONFIRM_HEADER)
            return "Thank you for your order" in el.text
        except Exception:
            return False

    def click_back_home(self):
        self.click(self.BACK_HOME_BTN)

    def get_page_title(self) -> str:
        """
        Return the current page title.

        Does NOT include a URL wait here — the URL wait is handled
        by the method that navigated TO this step (fill_shipping_info,
        click_finish, etc.) before get_page_title() is called.
        """
        return self.get_text(self.PAGE_TITLE)