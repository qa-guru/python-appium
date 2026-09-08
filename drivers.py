"""Session factory ≈ Java BrowserstackDriver + etalon AndroidDriverProvider (local / selenoid)."""

from __future__ import annotations

from pathlib import Path

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.webdriver import WebDriver

from config import TestConfig


def create_driver(config: TestConfig) -> WebDriver:
    if config.device_host == "browserstack":
        return webdriver.Remote(config.appium_url, options=_browserstack(config))
    if config.device_host == "selenoid":
        return webdriver.Remote(config.appium_url, options=_selenoid(config))
    if config.device_host in {"emulator", "real"}:
        return webdriver.Remote(config.appium_url, options=_local(config))
    raise ValueError("DEVICE_HOST: emulator, real, selenoid, browserstack")


def _android_base() -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.auto_grant_permissions = True
    options.no_reset = False
    options.new_command_timeout = 120
    options.app_wait_activity = "*"
    return options


def _local(config: TestConfig) -> UiAutomator2Options:
    app = config.android_app
    path = Path(app).expanduser()
    if not path.is_file():
        raise FileNotFoundError(
            f"APK not found: {app}. Download Wikipedia alpha to ANDROID_APP="
        )
    options = _android_base()
    options.app = str(path.resolve())
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    return options


def _selenoid(config: TestConfig) -> UiAutomator2Options:
    if not config.android_app:
        raise ValueError("Set ANDROID_APP to an APK URL for Selenoid")
    options = _android_base()
    options.set_capability("browserName", "android")
    options.set_capability("browserVersion", config.platform_version or "13.0")
    options.device_name = "android"
    options.app = config.android_app
    options.set_capability(
        "selenoid:options",
        {"enableVNC": True, "enableVideo": True},
    )
    return options


def _browserstack(config: TestConfig) -> UiAutomator2Options:
    if not config.browserstack_user or not config.browserstack_key:
        raise ValueError("Set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
    app = config.browserstack_app or config.android_app
    if not app:
        raise ValueError("Set BROWSERSTACK_APP=bs://…")
    options = _android_base()
    options.app = app
    options.device_name = config.device_name
    options.platform_version = config.platform_version
    options.set_capability(
        "bstack:options",
        {
            "userName": config.browserstack_user,
            "accessKey": config.browserstack_key,
            "projectName": "python-appium",
            "buildName": "wikipedia-search",
            "sessionName": "successfulSearchTest",
            "debug": True,
        },
    )
    return options
