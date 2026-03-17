# tests/test_products.py
"""
Products / Inventory Test Suite
================================
Covers product listing and cart-badge interactions on /inventory.html.
All tests use 'logged_in_driver' because login is not under test here.
"""

import logging
from pages.inventory_page import InventoryPage
from utils.config import Config

logger = logging.getLogger(__name__)

BACKPACK_PRODUCT = "Sauce Labs Backpack"


class TestProducts:

    def test_product_list_loads(self, logged_in_driver):
        """
        TC_PROD_001  Inventory page shows all 6 products after login.

        This is a smoke test — if products don't load, nothing else works.
        """
        inventory = InventoryPage(logged_in_driver)

        assert inventory.is_loaded(), \
            "Inventory container not visible after login"

        count = inventory.get_product_count()
        assert count == 6, \
            f"Expected 6 products, found {count}"

        logger.info("PASSED  TC_PROD_001  product list loads (%d items)", count)

    def test_add_product_to_cart(self, logged_in_driver):
        """
        TC_PROD_002  'Add to cart' increments the cart badge by 1.

        Flow:
          1. Record initial cart count (should be 0)
          2. Click 'Add to cart' on Backpack
          3. Assert badge shows initial_count + 1
          4. Assert 'Remove' button is now visible (button swapped)
        """
        inventory = InventoryPage(logged_in_driver)

        initial = inventory.get_cart_count()
        assert initial == 0, f"Cart should be empty at start, was {initial}"

        inventory.add_backpack_to_cart()

        updated = inventory.get_cart_count()
        assert updated == initial + 1, \
            f"Cart badge expected {initial + 1}, got {updated}"

        assert inventory.is_remove_button_visible("backpack"), \
            "Remove button not visible after adding Backpack"

        logger.info("PASSED  TC_PROD_002  add to cart → badge = %d", updated)

    def test_remove_product_from_cart(self, logged_in_driver):
        """
        TC_PROD_003  'Remove' on inventory page decrements the cart badge.

        Flow:
          1. Add Backpack (setup)
          2. Assert count == 1
          3. Click Remove
          4. Assert count == 0 and badge is gone
        """
        inventory = InventoryPage(logged_in_driver)

        # Setup
        inventory.add_backpack_to_cart()
        assert inventory.get_cart_count() == 1, \
            "Setup failed: Backpack not added to cart"

        # Action
        inventory.remove_backpack_from_cart()

        # Assert
        count = inventory.get_cart_count()
        assert count == 0, \
            f"Cart badge should be 0 after remove, got {count}"

        logger.info("PASSED  TC_PROD_003  remove from cart → badge = 0")
