# pages/inventory_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
from utils.config import Config


class InventoryPage(BasePage):

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

    def is_loaded(self) -> bool:
        return self.is_element_visible(self.INVENTORY_CONTAINER)

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def get_product_count(self) -> int:
        return len(self.driver.find_elements(*self.INVENTORY_ITEMS))

    def get_cart_count(self) -> int:
        """
        Return the badge count or 0 if badge is absent.
        Short 3-second wait — badge appears fast or not at all.
        """
        try:
            badge = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.CART_BADGE)
            )
            return int(badge.text)
        except TimeoutException:
            return 0

    # ── The key fix — staleness_of ────────────────────────────────────
    #
    # WHAT staleness_of does:
    # You grab a reference to the button element BEFORE clicking it.
    # After the click, React removes that exact element from the DOM
    # and inserts a new one. staleness_of detects the moment that
    # specific element reference is no longer attached to the DOM.
    #
    # WHY this beats every other wait:
    #
    #   invisibility_of_element_located  — searches DOM by locator,
    #     can match wrong elements, fails if element is hidden not removed
    #
    #   element_to_be_clickable          — requires full interactivity,
    #     race condition between "present" and "enabled"
    #
    #   staleness_of                     — watches the exact object you
    #     clicked, fires the instant React removes it. No ambiguity,
    #     no re-search, no race condition. Most reliable for React.

    def add_backpack_to_cart(self):
        btn = self.wait_for_clickable(self.ADD_TO_CART_BACKPACK)
        btn.click()
        # Wait for THIS exact element to be removed from the DOM
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.staleness_of(btn)
        )

    def remove_backpack_from_cart(self):
        btn = self.wait_for_clickable(self.REMOVE_BACKPACK)
        btn.click()
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.staleness_of(btn)
        )

    def add_bike_light_to_cart(self):
        btn = self.wait_for_clickable(self.ADD_TO_CART_BIKE_LIGHT)
        btn.click()
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.staleness_of(btn)
        )

    def remove_bike_light_from_cart(self):
        btn = self.wait_for_clickable(self.REMOVE_BIKE_LIGHT)
        btn.click()
        WebDriverWait(self.driver, Config.EXPLICIT_WAIT).until(
            EC.staleness_of(btn)
        )

    def is_remove_button_visible(self, product: str = "backpack") -> bool:
        locator = self.REMOVE_BACKPACK if product == "backpack" else self.REMOVE_BIKE_LIGHT
        return self.is_element_visible(locator)

    def go_to_cart(self):
        self.click(self.CART_ICON)

    def logout(self):
        self.click(self.MENU_BUTTON)
        self.click(self.LOGOUT_LINK)