from __future__ import annotations

import allure
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import TestConfig, load_config
from drivers import create_driver
from helpers import attach

SKIP_IDS = (
    "org.wikipedia.alpha:id/fragment_onboarding_skip_button",
    "org.wikipedia.alpha:id/fragment_onboarding_forward_button",
)
SEARCH_LOCS = (
    (AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia"),
    (AppiumBy.ID, "org.wikipedia.alpha:id/search_container"),
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Search Wikipedia")',
    ),
)


@pytest.fixture(scope="session")
def config() -> TestConfig:
    return load_config()


@pytest.fixture
def driver(config: TestConfig) -> WebDriver:
    drv = create_driver(config)
    drv.implicitly_wait(0)
    try:
        _skip_wikipedia_onboarding(drv, config.timeout)
    except Exception:
        attach.screenshot(drv)
        attach.page_source(drv)
        drv.quit()
        raise
    yield drv
    session_id = drv.session_id
    attach.screenshot(drv)
    attach.page_source(drv)
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


def _skip_wikipedia_onboarding(driver: WebDriver, timeout: float) -> None:
    for _ in range(5):
        clicked = False
        for rid in SKIP_IDS:
            els = driver.find_elements(AppiumBy.ID, rid)
            if els and els[0].is_displayed():
                els[0].click()
                clicked = True
                break
        if not clicked:
            break
    first_visible(driver, SEARCH_LOCS, timeout)
