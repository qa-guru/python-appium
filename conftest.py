from __future__ import annotations

import time

import allure
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import TestConfig, load_config
from drivers import create_driver
from helpers import attach

# Onboarding controls: the 2017 sample has fragment_onboarding_* ids, stable
# Wikipedia renders Compose views — content-desc "Next", text "Skip".
SKIP_LOCS = (
    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Skip")'),
    (AppiumBy.ACCESSIBILITY_ID, "Skip"),
    (AppiumBy.ID, "org.wikipedia:id/fragment_onboarding_skip_button"),
    (AppiumBy.ID, "org.wikipedia.alpha:id/fragment_onboarding_skip_button"),
)
FORWARD_LOCS = (
    (AppiumBy.ACCESSIBILITY_ID, "Next"),
    (AppiumBy.ACCESSIBILITY_ID, "Forward"),
    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Next")'),
    (AppiumBy.ID, "org.wikipedia:id/fragment_onboarding_forward_button"),
    (AppiumBy.ID, "org.wikipedia.alpha:id/fragment_onboarding_forward_button"),
)
# Feed search entry point: stable puts it in the bottom nav (nav_tab_search /
# desc "Search"), the 2017 alpha has a "Search Wikipedia" fake bar on top.
SEARCH_LOCS = (
    (AppiumBy.ID, "org.wikipedia:id/nav_tab_search"),
    (AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia"),
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Search Wikipedia")',
    ),
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().resourceIdMatches(".*id/search_container")',
    ),
    (AppiumBy.ACCESSIBILITY_ID, "Search"),
)
# Search input: alpha has org.wikipedia.alpha:id/search_src_text, stable renders
# a Compose text field exposed as a plain EditText.
FIELD_LOCS = (
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().resourceIdMatches(".*id/search_src_text")',
    ),
    (AppiumBy.CLASS_NAME, "android.widget.EditText"),
)
# First search tap on stable opens a "Search widget" promo sheet — close it.
PROMO_LOCS = (
    (AppiumBy.ACCESSIBILITY_ID, "Close"),
    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Close")'),
)
# Stable shows a "Search Wikipedia" hint; tapping it reveals the real EditText.
HINT_LOCS = (
    (AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia"),
    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Search Wikipedia")'),
)
# Result rows: alpha ids vs stable Compose list entries containing the query.
RESULT_LOCS = (
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().resourceIdMatches(".*id/page_list_item_title")',
    ),
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Appium")',
    ),
)
# Modal system dialogs (ANR "isn't responding", old-app warning) hide the app.
SYSTEM_DIALOG_IDS = (
    "android:id/aerr_wait",  # ANR — "Wait", dismisses the dialog
    "android:id/aerr_close",  # ANR — "Close app", fallback
    "android:id/button1",  # "OK" on the old-version warning
)


# Local routes record video on-device (screenrecord); farms publish mp4 files.
LOCAL_VIDEO_HOSTS = {"emulator", "real"}


@pytest.fixture(scope="session")
def config() -> TestConfig:
    return load_config()


@pytest.fixture
def driver(config: TestConfig) -> WebDriver:
    drv = create_driver(config)
    drv.implicitly_wait(0)
    session_id = drv.session_id
    recording = False
    if config.device_host in LOCAL_VIDEO_HOSTS:
        try:
            drv.start_recording_screen()
            recording = True
        except Exception:
            pass
    try:
        _skip_wikipedia_onboarding(drv, config.timeout)
    except Exception:
        try:
            attach.screenshot(drv, "screenshot on setup failure")
            attach.page_source(drv)
            if recording:
                attach.screen_recording(drv)
        finally:
            drv.quit()
        attach.video(config, session_id)
        raise
    yield drv
    try:
        attach.screenshot(drv)
        attach.page_source(drv)
        if recording:
            attach.screen_recording(drv)
    finally:
        drv.quit()
    attach.video(config, session_id)


def first_visible(driver: WebDriver, locators: tuple, timeout: float):
    last = None
    for by, value in locators:
        try:
            return WebDriverWait(driver, min(timeout, 8)).until(
                EC.visibility_of_element_located((by, value))
            )
        except Exception as exc:
            last = exc
    raise last or TimeoutError(locators)


def dismiss_if_present(driver: WebDriver, locators: tuple, timeout: float = 5) -> bool:
    """One-shot promo/dialog closer — retries briefly, then gives up."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _click_first(driver, locators):
            return True
        time.sleep(0.5)
    return False


def has_elements(driver: WebDriver, locators: tuple) -> bool:
    return any(driver.find_elements(by, value) for by, value in locators)


def open_search_field(driver: WebDriver, timeout: float):
    """Stable exposes the EditText only after tapping the Search Wikipedia hint."""
    try:
        return first_visible(driver, FIELD_LOCS, 8)
    except Exception:
        pass
    first_visible(driver, HINT_LOCS, timeout).click()
    return first_visible(driver, FIELD_LOCS, timeout)


def _skip_wikipedia_onboarding(driver: WebDriver, timeout: float) -> None:
    for _ in range(6):
        if _any_visible(driver, SEARCH_LOCS):
            return
        if _dismiss_system_dialog(driver):
            continue
        if _click_first(driver, SKIP_LOCS):
            continue
        if not _click_first(driver, FORWARD_LOCS):
            break
    first_visible(driver, SEARCH_LOCS, timeout)


def _click_first(driver: WebDriver, locators: tuple) -> bool:
    for by, value in locators:
        els = driver.find_elements(by, value)
        if els and els[0].is_displayed():
            els[0].click()
            time.sleep(0.8)
            return True
    return False


def _dismiss_system_dialog(driver: WebDriver) -> bool:
    for rid in SYSTEM_DIALOG_IDS:
        els = driver.find_elements(AppiumBy.ID, rid)
        if els and els[0].is_displayed():
            els[0].click()
            time.sleep(0.8)
            return True
    return False


def _any_visible(driver: WebDriver, locators: tuple) -> bool:
    for by, value in locators:
        els = driver.find_elements(by, value)
        if any(el.is_displayed() for el in els):
            return True
    return False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Screenshot of the failing state while the session is still alive."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    drv = item.funcargs.get("driver")
    if drv is not None:
        attach.screenshot(drv, "screenshot on failure")
