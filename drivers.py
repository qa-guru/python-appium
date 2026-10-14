"""Session factory ≈ Java BrowserstackDriver + etalon AndroidDriverProvider (local / selenoid)."""

from __future__ import annotations

from pathlib import Path

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.appium_connection import AppiumConnection
from appium.webdriver.client_config import AppiumClientConfig
from appium.webdriver.webdriver import WebDriver

from config import TestConfig

# Selenium's default is socket.getdefaulttimeout() = None — a stalled hub
# connection would hang forever. Session create on a farm takes ~2 min.
_HTTP_TIMEOUT_S = 300


def create_driver(config: TestConfig) -> WebDriver:
    builders = {
        "browserstack": _browserstack,
        "selenoid": _selenoid,
        "emulator": _local,
        "real": _local,
        "ios_simulator": _ios_simulator,
        "ios_real": _ios_real,
    }
    if config.device_host not in builders:
        raise ValueError(
            "DEVICE_HOST: emulator, real, selenoid, browserstack, "
            "ios_simulator, ios_real"
        )
    return webdriver.Remote(
        _executor(config), options=builders[config.device_host](config)
    )


def _executor(config: TestConfig) -> AppiumConnection:
    """Basic auth via ClientConfig — never in the URL (it would leak into logs)."""
    kwargs: dict = {}
    if config.device_host == "selenoid" and config.selenoid_user:
        kwargs = {"username": config.selenoid_user, "password": config.selenoid_password}
    elif config.device_host == "browserstack" and config.browserstack_user:
        kwargs = {
            "username": config.browserstack_user,
            "password": config.browserstack_key,
        }
    return AppiumConnection(
        client_config=AppiumClientConfig(
            remote_server_addr=config.appium_url, timeout=_HTTP_TIMEOUT_S, **kwargs
        )
    )


def _android_base(config: TestConfig, *, with_package: bool) -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.auto_grant_permissions = True
    options.no_reset = False
    options.new_command_timeout = 120
    options.app_wait_activity = "org.wikipedia.*"
    options.app_activity = config.app_activity
    if with_package:
        options.app_package = config.app_package
    return options


def _local(config: TestConfig) -> UiAutomator2Options:
    app = config.android_app
    path = Path(app).expanduser()
    if not path.is_file():
        raise FileNotFoundError(
            f"APK not found: {app}. Download the pinned Wikipedia stable to ANDROID_APP="
        )
    options = _android_base(config, with_package=True)
    options.app = str(path.resolve())
    if config.udid:
        options.udid = config.udid  # real device serial, or emulator-5554
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    return options


def _selenoid(config: TestConfig) -> UiAutomator2Options:
    if not config.android_app:
        raise ValueError("Set ANDROID_APP to an APK URL for Selenoid")
    # Selenoid routes on browserName=android. Appium inside rejects appPackage+browserName.
    options = _android_base(config, with_package=False)
    options.new_command_timeout = 300  # app download+install on the farm is slow
    options.set_capability("browserName", "android")
    options.set_capability("browserVersion", config.platform_version or "16.0")
    options.device_name = "android"
    options.app = config.android_app
    options.set_capability(
        "selenoid:options",
        {"enableVNC": True, "enableVideo": True},
    )
    return options


def _browserstack(config: TestConfig) -> UiAutomator2Options | XCUITestOptions:
    if not config.browserstack_user or not config.browserstack_key:
        raise ValueError("Set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
    app = config.browserstack_app or config.android_app
    if not app:
        raise ValueError("Set BROWSERSTACK_APP=bs://…")
    platform = config.browserstack_platform.lower()
    if platform == "ios":
        options = _ios_base(config)
    elif platform == "android":
        options = _android_base(config, with_package=True)
    else:
        raise ValueError("BROWSERSTACK_PLATFORM: Android or iOS")
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


def _ios_base(config: TestConfig) -> XCUITestOptions:
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.new_command_timeout = 120
    options.device_name = config.device_name
    if config.platform_version:
        options.platform_version = config.platform_version
    return options


def _ios_simulator(config: TestConfig) -> XCUITestOptions:
    """IOS_APP = path to a simulator .app build (xcodebuild -sdk iphonesimulator)."""
    if not config.ios_app:
        raise ValueError("Set IOS_APP to a simulator .app build of Wikipedia")
    path = Path(config.ios_app).expanduser()
    if not path.is_dir():
        raise FileNotFoundError(
            f"Simulator .app not found: {config.ios_app} — build Wikipedia "
            "with -sdk iphonesimulator first"
        )
    options = _ios_base(config)
    options.app = str(path.resolve())
    if config.udid:
        options.udid = config.udid  # simulator UDID from `xcrun simctl list`
    return options


def _ios_real(config: TestConfig) -> XCUITestOptions:
    """App Store Wikipedia via bundleId; WDA must be signed (xcodeOrgId etc.)."""
    if not config.udid:
        raise ValueError("Set UDID to the iPhone's UDID (xcrun xctrace list devices)")
    options = _ios_base(config)
    options.udid = config.udid
    options.set_capability("appium:bundleId", config.bundle_id)
    options.set_capability("appium:wdaLocalPort", config.wda_local_port)
    options.set_capability(
        "appium:allowProvisioningDeviceRegistration", config.wda_allow_provisioning
    )
    options.set_capability("appium:xcodeSigningId", "iPhone Developer")
    return options
