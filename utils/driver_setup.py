# utils/driver_setup.py

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(browser: str = "chrome", headless: bool = False) -> webdriver.Chrome:

    if browser.lower() != "chrome":
        raise ValueError(f"Browser '{browser}' is not supported. Use 'chrome'.")

    options = Options()

    if headless:
        options.add_argument("--headless=new")

    # ── Stability flags (CI + general) ────────────────────────────────
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")

    # ── THE FIX: Disable Chrome password manager popups ───────────────
    #
    # Chrome's built-in Password Manager detected "secret_sauce" as a
    # breached password and showed a blocking "Change your password"
    # dialog over the page. This dialog intercepted all clicks and
    # prevented Selenium from interacting with cart/checkout buttons.
    #
    # These three flags together eliminate the problem:
    #
    # --disable-features=PasswordCheck
    #   Turns off the real-time password breach checking service.
    #   This is what triggers the "found in a data breach" dialog.
    #
    # --password-store=basic
    #   Stops Chrome from using the OS keychain or any password store.
    #   Prevents the password manager from saving or flagging credentials.
    #
    # --use-mock-keychain
    #   On Mac/Linux: uses a mock keychain instead of the real system
    #   keychain. On Windows it's a no-op but harmless to include.
    #
    options.add_argument("--disable-features=PasswordCheck")
    options.add_argument("--password-store=basic")
    options.add_argument("--use-mock-keychain")

    # ── Also disable these via ChromeOptions prefs ─────────────────────
    #
    # Chrome has two layers of password management:
    #   1. Command-line flags (above) — controls the breach-check service
    #   2. User profile preferences (below) — controls the save/autofill UI
    #
    # Disabling both layers ensures no password-related popup appears
    # at any point during the test session.
    #
    options.add_experimental_option("prefs", {
        # Disable the "Save password?" bubble after form submission
        "credentials_enable_service": False,
        # Disable password autofill suggestions on input fields
        "profile.password_manager_enabled": False,
        # Disable the leak detection that triggers the breach dialog
        "profile.password_manager_leak_detection": False,
    })

    # ── Also exclude automation flags that cause instability ──────────
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    options.add_experimental_option("useAutomationExtension", False)

    # ── WinError-193 safety net ───────────────────────────────────────
    driver_path = ChromeDriverManager().install()
    if os.name == "nt" and not driver_path.endswith(".exe"):
        folder = os.path.dirname(driver_path)
        for fname in os.listdir(folder):
            if fname == "chromedriver.exe":
                driver_path = os.path.join(folder, fname)
                break

    print(f"[INFO] ChromeDriver path: {driver_path}")

    service = Service(executable_path=driver_path)
    driver  = webdriver.Chrome(service=service, options=options)

    driver.implicitly_wait(3)
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    return driver


def quit_driver(driver: webdriver.Chrome) -> None:
    if driver:
        driver.quit()