from __future__ import annotations

import pytest
from appium.webdriver.webdriver import WebDriver

from config import TestConfig, load_config
from drivers import create_driver
from helpers import attach


@pytest.fixture(scope="session")
def config() -> TestConfig:
    return load_config()


@pytest.fixture
def driver(config: TestConfig) -> WebDriver:
    drv = create_driver(config)
    yield drv
    session_id = drv.session_id
    attach.screenshot(drv)
    attach.page_source(drv)
    drv.quit()
    attach.video(config, session_id)
