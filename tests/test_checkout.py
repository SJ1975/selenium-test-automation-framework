# tests/test_checkout.py
"""
Checkout Test Suite
===================
Covers the complete 3-step checkout flow.

This is the most important end-to-end test in the suite — it validates
the full purchase journey a real customer would follow.

Step 1: /checkout-step-one.html  — personal information form
Step 2: /checkout-step-two.html  — order summary / overview
Step 3: /checkout-complete.html  — order confirmation
"""

import logging
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils.config import Config

logger = logging.getLogger(__name__)

BACKPACK_NAME = "Sauce Labs Backpack"

# Checkout form constants (imported from config but aliased here for readability)
CHECKOUT_FIRST_NAME = Config.FIRST_NAME
CHECKOUT_LAST_NAME  = Config.LAST_NAME
CHECKOUT_ZIP_CODE   = Config.POSTAL_CODE


class TestCheckout:

    def test_complete_checkout_flow(self, logged_in_driver):
        """
        TC_CHK_001  Full end-to-end purchase journey completes successfully.

        Flow:
          1. Add Backpack → navigate to cart
          2. Proceed to checkout
          3. Fill personal info → Continue
          4. Review overview → Finish
          5. Assert confirmation header: 'Thank you for your order!'
        """
        # ── Step 1: add item ──────────────────────────────────────────
        inventory = InventoryPage(logged_in_driver)
        inventory.add_backpack_to_cart()
        inventory.go_to_cart()

        # ── Step 2: proceed from cart ─────────────────────────────────
        cart = CartPage(logged_in_driver)
        assert cart.get_cart_item_count() == 1, \
            "Setup: expected 1 item in cart before checkout"

        cart.proceed_to_checkout()

        # ── Step 3: fill shipping info ────────────────────────────────
        checkout = CheckoutPage(logged_in_driver)
        assert checkout.get_page_title() == "Checkout: Your Information", \
            "Did not reach checkout info page"

        checkout.fill_shipping_info(
            first    = CHECKOUT_FIRST_NAME,
            last     = CHECKOUT_LAST_NAME,
            zip_code = CHECKOUT_ZIP_CODE,
        )

        # ── Step 4: verify overview ───────────────────────────────────
        assert checkout.get_page_title() == "Checkout: Overview", \
            "Did not reach checkout overview page"

        total = checkout.get_total_price()
        assert "Total:" in total, \
            f"Total price not displayed correctly: '{total}'"

        # ── Step 5: finish and confirm ────────────────────────────────
        checkout.click_finish()

        assert checkout.is_order_confirmed(), \
            "Order confirmation page not displayed"

        header = checkout.get_confirmation_header()
        assert "Thank you for your order" in header, \
            f"Expected confirmation header, got: '{header}'"

        logger.info("PASSED  TC_CHK_001  complete checkout flow → '%s'", header)

    def test_checkout_missing_first_name(self, logged_in_driver):
        """
        TC_CHK_002  Submitting checkout form without first name shows error.

        Passes an empty string as first name to fill_shipping_info().
        fill_shipping_info() skips the field when the value is empty,
        so Continue is clicked with the first-name input blank.

        Expected: validation error, user stays on Step 1.
        """
        # Setup: get to checkout step 1
        inventory = InventoryPage(logged_in_driver)
        inventory.add_backpack_to_cart()
        inventory.go_to_cart()

        CartPage(logged_in_driver).proceed_to_checkout()

        checkout = CheckoutPage(logged_in_driver)
        assert checkout.get_page_title() == "Checkout: Your Information", \
            "Setup failed: not on checkout info page"

        # Submit form with first name intentionally blank
        checkout.fill_shipping_info(
            first    = "",                    # ← intentionally empty
            last     = CHECKOUT_LAST_NAME,
            zip_code = CHECKOUT_ZIP_CODE,
        )

        # Assert: still on Step 1 and error is shown
        assert checkout.get_page_title() == "Checkout: Your Information", \
            "Should have stayed on info page after missing first name"

        assert checkout.is_error_displayed(), \
            "No validation error shown for missing first name"

        logger.info("PASSED  TC_CHK_002  missing first name → validation error")

    def test_checkout_with_multiple_items(self, logged_in_driver):
        """
        TC_CHK_003  Checkout completes successfully with two items in cart.
        """
        inventory = InventoryPage(logged_in_driver)
        inventory.add_backpack_to_cart()
        inventory.add_bike_light_to_cart()
        inventory.go_to_cart()

        cart = CartPage(logged_in_driver)
        assert cart.get_cart_item_count() == 2, \
            "Setup: expected 2 items in cart"

        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_driver)
        checkout.fill_shipping_info(
            first    = CHECKOUT_FIRST_NAME,
            last     = CHECKOUT_LAST_NAME,
            zip_code = CHECKOUT_ZIP_CODE,
        )
        checkout.click_finish()

        assert checkout.is_order_confirmed(), \
            "Order confirmation not shown for multi-item checkout"

        logger.info("PASSED  TC_CHK_003  multi-item checkout → order confirmed")
