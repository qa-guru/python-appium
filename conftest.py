from __future__ import annotations

import pytest
from appium.webdriver.webdriver import WebDriver

from config import TestConfig, load_config
from drivers import create_driver


@pytest.fixture(scope="session")
def config() -> TestConfig:
    return load_config()


@pytest.fixture
def driver(config: TestConfig) -> WebDriver:
    drv = create_driver(config)
    yield drv
    drv.quit()
