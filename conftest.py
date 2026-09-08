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


@pytest.fixture(scope="session")
def config() -> TestConfig:
    return load_config()


@pytest.fixture
def driver(config: TestConfig) -> WebDriver:
    drv = create_driver(config)
    drv.implicitly_wait(0)
    _skip_wikipedia_onboarding(drv, config.timeout)
    yield drv
    session_id = drv.session_id
    attach.screenshot(drv)
    attach.page_source(drv)
    drv.quit()
    attach.video(config, session_id)


def _skip_wikipedia_onboarding(driver: WebDriver, timeout: float) -> None:
    skip = (AppiumBy.ID, "org.wikipedia.alpha:id/fragment_onboarding_skip_button")
    search = (AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia")
    wait = WebDriverWait(driver, min(timeout, 15))
    try:
        el = wait.until(EC.presence_of_element_located(skip))
        el.click()
    except Exception:
        pass
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(search))
