"""Twin of qa-guru/mobile-tests-22 drivers.BrowserstackDriver."""

from __future__ import annotations

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.webdriver import WebDriver

from config import TestConfig


def create_driver(config: TestConfig) -> WebDriver:
    options = UiAutomator2Options()
    options.set_capability("browserstack.user", config.user)
    options.set_capability("browserstack.key", config.key)
    options.set_capability("app", config.app)
    options.set_capability("device", config.device)
    options.set_capability("os_version", config.os_version)
    options.set_capability("project", "First Python Project")
    options.set_capability("build", "browserstack-build-1")
    options.set_capability("name", "first_test")
    return webdriver.Remote("https://hub.browserstack.com/wd/hub", options=options)
