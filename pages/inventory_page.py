# pages/inventory_page.py
"""
Inventory Page Object
=====================
Represents https://www.saucedemo.com/inventory.html
(the product listing page shown after successful login).
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class InventoryPage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────
    INVENTORY_CONTAINER    = (By.ID, "inventory_container")
    PAGE_TITLE             = (By.CLASS_NAME, "title")
    INVENTORY_ITEMS        = (By.CLASS_NAME, "inventory_item")

    # Cart icon and badge (header, present on every post-login page)
    CART_ICON              = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE             = (By.CLASS_NAME, "shopping_cart_badge")

    # Product-specific buttons — data-test attributes are the most stable
    ADD_TO_CART_BACKPACK   = (By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-backpack']")
    REMOVE_BACKPACK        = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-backpack']")
    ADD_TO_CART_BIKE_LIGHT = (By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-bike-light']")
    REMOVE_BIKE_LIGHT      = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-bike-light']")

    # Burger menu
    MENU_BUTTON            = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK            = (By.ID, "logout_sidebar_link")

    # ── Verification ──────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self.is_element_visible(self.INVENTORY_CONTAINER)

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def get_product_count(self) -> int:
        """Return the number of product cards on the page (should be 6)."""
        return len(self.driver.find_elements(*self.INVENTORY_ITEMS))

    # ── Cart badge ────────────────────────────────────────────────────

    def get_cart_count(self) -> int:
        """
        Return the number shown on the cart badge, or 0 if badge is absent.

        KEY DETAIL — why a short wait is necessary:
        The badge appears via JavaScript AFTER the 'Add to cart' click.
        Without a wait, find_elements() runs before the DOM updates and
        returns an empty list → count = 0 (the 'ghost count' bug).

        We use a 3-second WebDriverWait here (shorter than the global 10s)
        because if the badge is going to appear it appears quickly; we
        don't want to add 10 seconds to every cart-count check.
        """
        try:
            badge = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.CART_BADGE)
            )
            return int(badge.text)
        except TimeoutException:
            return 0  # Badge absent = cart empty

    # ── Cart actions ──────────────────────────────────────────────────

    def add_backpack_to_cart(self):
        """Click 'Add to cart' for Sauce Labs Backpack."""
        self.click(self.ADD_TO_CART_BACKPACK)

    def remove_backpack_from_cart(self):
        """
        Click the 'Remove' button for Sauce Labs Backpack.

        IMPORTANT: this button only exists in the DOM AFTER the item has
        been added.  wait_for_clickable() handles the async DOM swap from
        'Add to cart' → 'Remove'.
        """
        self.click(self.REMOVE_BACKPACK)

    def add_bike_light_to_cart(self):
        self.click(self.ADD_TO_CART_BIKE_LIGHT)

    def remove_bike_light_from_cart(self):
        self.click(self.REMOVE_BIKE_LIGHT)

    def is_remove_button_visible(self, product: str = "backpack") -> bool:
        """
        Check whether the Remove button is visible for a product.
        A visible Remove button means the product is currently in the cart.
        """
        locator = self.REMOVE_BACKPACK if product == "backpack" else self.REMOVE_BIKE_LIGHT
        return self.is_element_visible(locator)

    # ── Navigation ────────────────────────────────────────────────────

    def go_to_cart(self):
        """Click the cart icon to navigate to /cart.html."""
        self.click(self.CART_ICON)

    def logout(self):
        """Open the burger menu and click Logout."""
        self.click(self.MENU_BUTTON)
        self.click(self.LOGOUT_LINK)
