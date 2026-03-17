# pages/cart_page.py
"""
Cart Page Object
================
Represents https://www.saucedemo.com/cart.html

IMPORTANT LOCATOR NOTE
======================
get_cart_item_count() counts <div class="cart_item"> rows —
the actual line-item rows rendered on this page.

It does NOT read shopping_cart_badge (the red number on the header icon).
Those are two different things:
  - cart_item     → how many products are listed on /cart.html
  - cart_badge    → the counter on the icon (lives in the header, not the table)
Using the badge here would return 0 or throw TimeoutException because
the badge is not a reliable indicator of cart-page row count.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class CartPage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────
    PAGE_TITLE        = (By.CLASS_NAME, "title")

    # cart_item is the wrapper div for every product row on /cart.html
    CART_ITEMS        = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAMES   = (By.CLASS_NAME, "inventory_item_name")

    REMOVE_BACKPACK   = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-backpack']")
    REMOVE_BIKE_LIGHT = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-bike-light']")

    CONTINUE_BTN      = (By.ID, "continue-shopping")
    CHECKOUT_BTN      = (By.ID, "checkout")

    # ── Verification ──────────────────────────────────────────────────

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def get_cart_item_count(self) -> int:
        """
        Return the number of product rows on the cart page.

        Uses presence_of_element_located (not visibility) because a row
        can be in the DOM and valid even if partially off-screen.
        Returns 0 safely if the cart is empty or the page hasn't loaded.
        """
        try:
            self.wait.until(EC.presence_of_element_located(self.CART_ITEMS))
            return len(self.driver.find_elements(*self.CART_ITEMS))
        except TimeoutException:
            return 0

    def get_cart_item_names(self) -> list:
        """Return a list of product-name strings currently in the cart."""
        try:
            self.wait.until(EC.presence_of_element_located(self.CART_ITEM_NAMES))
            elements = self.driver.find_elements(*self.CART_ITEM_NAMES)
            return [el.text for el in elements]
        except TimeoutException:
            return []

    def is_item_in_cart(self, product_name: str) -> bool:
        return product_name in self.get_cart_item_names()

    def is_cart_empty(self) -> bool:
        return self.get_cart_item_count() == 0

    # ── Actions ───────────────────────────────────────────────────────

    def remove_backpack(self):
        self.click(self.REMOVE_BACKPACK)

    def remove_bike_light(self):
        self.click(self.REMOVE_BIKE_LIGHT)

    def proceed_to_checkout(self):
        """Click the Checkout button to begin the checkout flow."""
        self.click(self.CHECKOUT_BTN)

    def continue_shopping(self):
        """Click Continue Shopping to go back to /inventory.html."""
        self.click(self.CONTINUE_BTN)
