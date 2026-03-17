# pages/checkout_page.py
"""
Checkout Page Object
====================
Handles all three steps of the checkout flow:

  Step 1 → /checkout-step-one.html    Personal information form
  Step 2 → /checkout-step-two.html    Order overview / summary
  Step 3 → /checkout-complete.html    Order confirmation

One class for all three steps is fine here because each step is
simple.  In a larger app you would split these into three classes.

fill_shipping_info() lives HERE — not in CartPage.
Methods belong to the page they interact with.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CheckoutPage(BasePage):

    # ── Step 1 locators ───────────────────────────────────────────────
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT  = (By.ID, "last-name")
    ZIP_INPUT        = (By.ID, "postal-code")
    CONTINUE_BTN     = (By.ID, "continue")
    ERROR_MESSAGE    = (By.CSS_SELECTOR, "[data-test='error']")

    # ── Step 2 locators ───────────────────────────────────────────────
    FINISH_BTN       = (By.ID, "finish")
    TOTAL_LABEL      = (By.CLASS_NAME, "summary_total_label")
    ITEM_TOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    CANCEL_BTN       = (By.ID, "cancel")

    # ── Step 3 locators ───────────────────────────────────────────────
    CONFIRM_HEADER   = (By.CLASS_NAME, "complete-header")
    CONFIRM_TEXT     = (By.CLASS_NAME, "complete-text")
    BACK_HOME_BTN    = (By.ID, "back-to-products")

    # ── Shared ────────────────────────────────────────────────────────
    PAGE_TITLE       = (By.CLASS_NAME, "title")

    # ── Step 1 — personal information ────────────────────────────────

    def fill_shipping_info(self, first: str, last: str, zip_code: str):
        """
        Fill in the checkout information form and click Continue.

        Passing an empty string for any field simulates a missing-field
        submission (used in validation error tests).

        Args:
            first    : first name  — pass "" to leave blank
            last     : last name   — pass "" to leave blank
            zip_code : postal code — pass "" to leave blank
        """
        if first:
            self.type_text(self.FIRST_NAME_INPUT, first)
        if last:
            self.type_text(self.LAST_NAME_INPUT, last)
        if zip_code:
            self.type_text(self.ZIP_INPUT, zip_code)

        # Always click Continue — this triggers server-side validation
        self.click(self.CONTINUE_BTN)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self.is_element_visible(self.ERROR_MESSAGE)

    # ── Step 2 — order overview ───────────────────────────────────────

    def get_total_price(self) -> str:
        """Return the total-price string e.g. 'Total: $32.39'."""
        return self.get_text(self.TOTAL_LABEL)

    def click_finish(self):
        """Submit the order (Step 2 → Step 3)."""
        self.click(self.FINISH_BTN)

    def click_cancel(self):
        self.click(self.CANCEL_BTN)

    # ── Step 3 — confirmation ─────────────────────────────────────────

    def get_confirmation_header(self) -> str:
        """Return the 'Thank you for your order!' header text."""
        return self.get_text(self.CONFIRM_HEADER)

    def is_order_confirmed(self) -> bool:
        """Return True when the thank-you confirmation is visible."""
        try:
            el = self.wait_for_element(self.CONFIRM_HEADER)
            return "Thank you for your order" in el.text
        except Exception:
            return False

    def click_back_home(self):
        self.click(self.BACK_HOME_BTN)

    # ── Shared ────────────────────────────────────────────────────────

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)
