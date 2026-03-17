# tests/test_cart.py
"""
Cart Page Test Suite
====================
Covers /cart.html interactions.

get_cart_item_count() here counts cart_item ROW elements on the cart page —
NOT the shopping_cart_badge in the header.  These are different locators
for different purposes.
"""

import logging
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

logger = logging.getLogger(__name__)

BACKPACK_NAME   = "Sauce Labs Backpack"
BIKE_LIGHT_NAME = "Sauce Labs Bike Light"


class TestCart:

    def test_items_appear_in_cart(self, logged_in_driver):
        """
        TC_CART_001  Item added on inventory page appears on /cart.html.

        Flow:
          1. Add Backpack from inventory
          2. Navigate to cart
          3. Assert Backpack name appears in the cart list
          4. Assert row count == 1
        """
        inventory = InventoryPage(logged_in_driver)
        inventory.add_backpack_to_cart()
        inventory.go_to_cart()

        cart = CartPage(logged_in_driver)

        assert cart.is_item_in_cart(BACKPACK_NAME), \
            f"'{BACKPACK_NAME}' not found in cart items"

        count = cart.get_cart_item_count()
        assert count == 1, \
            f"Expected 1 cart row, found {count}"

        logger.info("PASSED  TC_CART_001  item appears in cart (count=%d)", count)

    def test_multiple_items_in_cart(self, logged_in_driver):
        """
        TC_CART_002  Two items added both appear on /cart.html.
        """
        inventory = InventoryPage(logged_in_driver)
        inventory.add_backpack_to_cart()
        inventory.add_bike_light_to_cart()
        inventory.go_to_cart()

        cart = CartPage(logged_in_driver)

        count = cart.get_cart_item_count()
        assert count == 2, \
            f"Expected 2 cart rows, found {count}"

        assert cart.is_item_in_cart(BACKPACK_NAME), \
            f"'{BACKPACK_NAME}' missing from cart"

        assert cart.is_item_in_cart(BIKE_LIGHT_NAME), \
            f"'{BIKE_LIGHT_NAME}' missing from cart"

        logger.info("PASSED  TC_CART_002  two items in cart (count=%d)", count)

    def test_remove_item_from_cart(self, logged_in_driver):
        """
        TC_CART_003  Clicking Remove on /cart.html removes the item.

        Flow:
          1. Add Backpack and navigate to cart
          2. Assert 1 item present
          3. Click Remove
          4. Assert cart is now empty
        """
        inventory = InventoryPage(logged_in_driver)
        inventory.add_backpack_to_cart()
        inventory.go_to_cart()

        cart = CartPage(logged_in_driver)
        assert cart.get_cart_item_count() == 1, \
            "Setup failed: expected 1 item before removal"

        cart.remove_backpack()

        assert cart.is_cart_empty(), \
            "Cart should be empty after removing the only item"

        logger.info("PASSED  TC_CART_003  item removed from cart page")

    def test_cart_page_title(self, logged_in_driver):
        """
        TC_CART_004  Cart page title reads 'Your Cart'.
        """
        InventoryPage(logged_in_driver).go_to_cart()

        title = CartPage(logged_in_driver).get_page_title()
        assert title == "Your Cart", \
            f"Expected 'Your Cart', got '{title}'"

        logger.info("PASSED  TC_CART_004  cart page title correct")

    def test_continue_shopping_returns_to_inventory(self, logged_in_driver):
        """
        TC_CART_005  'Continue Shopping' navigates back to /inventory.html.
        """
        from pages.inventory_page import InventoryPage as _Inv

        inventory = InventoryPage(logged_in_driver)
        inventory.go_to_cart()

        CartPage(logged_in_driver).continue_shopping()

        assert _Inv(logged_in_driver).is_loaded(), \
            "Did not return to inventory page after Continue Shopping"

        logger.info("PASSED  TC_CART_005  continue shopping → inventory page")
