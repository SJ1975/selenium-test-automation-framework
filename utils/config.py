# utils/config.py
"""
Configuration Module
====================
Single source of truth for all test settings.
Change values here — they apply everywhere automatically.
"""


class Config:

    # ── Application ───────────────────────────────────────────────────
    BASE_URL = "https://www.saucedemo.com"

    # ── Valid test accounts (provided by saucedemo publicly) ──────────
    STANDARD_USER    = "standard_user"
    LOCKED_OUT_USER  = "locked_out_user"
    PROBLEM_USER     = "problem_user"
    PASSWORD         = "secret_sauce"

    # ── Invalid credentials (used in negative tests) ──────────────────
    INVALID_USER     = "wrong_user"
    INVALID_PASSWORD = "wrong_password"

    # ── Checkout form data ────────────────────────────────────────────
    FIRST_NAME   = "John"
    LAST_NAME    = "Doe"
    POSTAL_CODE  = "12345"

    # ── Timeouts (seconds) ────────────────────────────────────────────
    EXPLICIT_WAIT     = 10
    PAGE_LOAD_TIMEOUT = 30

    # ── Report output path ────────────────────────────────────────────
    REPORT_PATH = "reports/test_report.html"
