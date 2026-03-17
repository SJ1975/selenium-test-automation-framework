# pages/cart_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.config import Config


class CartPage(BasePage):

    PAGE_TITLE        = (By.CLASS_NAME, "title")
    CART_ITEMS        = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAMES   = (By.CLASS_NAME, "inventory_item_name")
    REMOVE_BACKPACK   = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-backpack']")
    REMOVE_BIKE_LIGHT = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-bike-light']")
    CONTINUE_BTN      = (By.ID, "continue-shopping")
    CHECKOUT_BTN      = (By.ID, "checkout")

    def _wait_for_cart_page(self):
        """Wait until URL confirms we are on /cart.html."""
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.url_contains("cart")
        )

    def _wait_for_item_text(self):
        """
        Wait until every cart item name element has non-empty text.

        WHY a custom condition beats presence/visibility here:

        The sequence when navigating to the cart page is:
          1. URL changes to /cart.html          <- url_contains fires
          2. cart_item divs added to DOM        <- presence fires
          3. cart_item divs become visible      <- visibility fires
          4. Text content rendered inside them  <- THIS is what we need

        Steps 1-3 all fire BEFORE step 4 on a slow or busy machine.
        Calling .text at step 3 returns "" — so is_item_in_cart()
        returns False even though the item IS there.

        This custom condition polls until .text is non-empty on every
        item name element. It only resolves when the content is
        actually rendered — making it immune to slow rendering.
        """
        def all_items_have_text(driver):
            elements = driver.find_elements(*self.CART_ITEM_NAMES)
            # True when: at least one element exists AND every element
            # has non-empty stripped text
            return bool(elements) and all(
                el.text.strip() != "" for el in elements
            )

        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            all_items_have_text
        )

    # ── Verification ──────────────────────────────────────────────────

    def get_page_title(self) -> str:
        self._wait_for_cart_page()
        return self.get_text(self.PAGE_TITLE)

    def get_cart_item_count(self) -> int:
        """
        Count product rows on /cart.html.
        Waits for rows to have text before counting — prevents
        counting empty/unrendered rows that return 0.
        """
        try:
            self._wait_for_cart_page()
            self._wait_for_item_text()
            return len(self.driver.find_elements(*self.CART_ITEMS))
        except TimeoutException:
            # TimeoutException from _wait_for_item_text = cart is empty
            return 0

    def get_cart_item_names(self) -> list:
        """
        Return product name strings from the cart.
        Guarantees text is loaded before reading .text.
        """
        try:
            self._wait_for_cart_page()
            self._wait_for_item_text()
            elements = self.driver.find_elements(*self.CART_ITEM_NAMES)
            return [el.text for el in elements]
        except TimeoutException:
            return []

    def is_item_in_cart(self, product_name: str) -> bool:
        return product_name in self.get_cart_item_names()

    def is_cart_empty(self) -> bool:
        """
        Returns True if no cart items exist.
        Uses a short wait — if cart is empty there are no items to load.
        """
        self._wait_for_cart_page()
        try:
            # Short wait — if items exist they appear quickly
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.CART_ITEMS)
            )
            return False  # Items found = cart not empty
        except TimeoutException:
            return True   # No items found in 3s = cart is empty

    def remove_backpack(self):
        self.click(self.REMOVE_BACKPACK)

    def remove_bike_light(self):
        self.click(self.REMOVE_BIKE_LIGHT)

    def proceed_to_checkout(self):
        self._wait_for_cart_page()
        self.click(self.CHECKOUT_BTN)
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.url_contains("checkout-step-one")
        )

    def continue_shopping(self):
        self._wait_for_cart_page()
        self.click(self.CONTINUE_BTN)
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.url_contains("inventory")
        )