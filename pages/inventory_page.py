# pages/inventory_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.config import Config


class InventoryPage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────
    INVENTORY_CONTAINER    = (By.ID, "inventory_container")
    PAGE_TITLE             = (By.CLASS_NAME, "title")
    INVENTORY_ITEMS        = (By.CLASS_NAME, "inventory_item")

    CART_ICON              = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE             = (By.CLASS_NAME, "shopping_cart_badge")

    ADD_TO_CART_BACKPACK   = (By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-backpack']")
    REMOVE_BACKPACK        = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-backpack']")

    ADD_TO_CART_BIKE_LIGHT = (By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-bike-light']")
    REMOVE_BIKE_LIGHT      = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-bike-light']")

    MENU_BUTTON            = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK            = (By.ID, "logout_sidebar_link")

    # ── Verification ──────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self.is_element_visible(self.INVENTORY_CONTAINER)

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def get_product_count(self) -> int:
        return len(self.driver.find_elements(*self.INVENTORY_ITEMS))

    # ── Cart badge ────────────────────────────────────────────────────

    def get_cart_count(self) -> int:
        """
        Return the number on the cart badge, or 0 if badge is absent.

        Uses the full EXPLICIT_WAIT (10s) so slow network/page responses
        don't cause false 0 readings.
        Badge absent = cart is empty = 0.
        """
        try:
            badge = WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
                EC.visibility_of_element_located(self.CART_BADGE)
            )
            return int(badge.text)
        except TimeoutException:
            return 0

    # ── Cart actions ──────────────────────────────────────────────────

    def add_backpack_to_cart(self):
        """
        Click 'Add to cart' for Backpack and WAIT for the button to
        change to 'Remove' before returning.

        WHY the wait matters:
        Saucedemo updates the cart via JavaScript. The click fires
        instantly, but the DOM swap (Add -> Remove) and the badge
        update happen a few milliseconds later.
        If we read get_cart_count() before the JS finishes, we get
        the OLD value (0). Waiting for the Remove button to appear
        proves the JS has completed — the badge is now accurate.
        """
        self.click(self.ADD_TO_CART_BACKPACK)
        # Wait for button to swap to Remove = JS has finished
        self.wait_for_element(self.REMOVE_BACKPACK)

    def remove_backpack_from_cart(self):
        """
        Click 'Remove' for Backpack and WAIT for the button to change
        back to 'Add to cart' before returning.

        Same reason as above — we wait for the DOM to reflect the
        removal before any caller reads the badge count.
        """
        self.click(self.REMOVE_BACKPACK)
        # Wait for button to swap back to Add to cart = JS has finished
        self.wait_for_element(self.ADD_TO_CART_BACKPACK)

    def add_bike_light_to_cart(self):
        """Click 'Add to cart' for Bike Light and wait for button swap."""
        self.click(self.ADD_TO_CART_BIKE_LIGHT)
        self.wait_for_element(self.REMOVE_BIKE_LIGHT)

    def remove_bike_light_from_cart(self):
        """Click 'Remove' for Bike Light and wait for button swap."""
        self.click(self.REMOVE_BIKE_LIGHT)
        self.wait_for_element(self.ADD_TO_CART_BIKE_LIGHT)

    def is_remove_button_visible(self, product: str = "backpack") -> bool:
        """True if Remove button is visible (item is in cart)."""
        locator = self.REMOVE_BACKPACK if product == "backpack" else self.REMOVE_BIKE_LIGHT
        return self.is_element_visible(locator)

    # ── Navigation ────────────────────────────────────────────────────

    def go_to_cart(self):
        self.click(self.CART_ICON)

    def logout(self):
        self.click(self.MENU_BUTTON)
        self.click(self.LOGOUT_LINK)