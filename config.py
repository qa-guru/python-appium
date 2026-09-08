"""Env — Java `-DdeviceHost=` / `-Dbrowserstack.user=` for Python."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

WIKIPEDIA_APK = (
    "https://github.com/wikimedia/apps-android-wikipedia"
    "/releases/download/latest/app-alpha-universal-release.apk"
)


def _env(name: str, default: str = "") -> str:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip()


@dataclass(frozen=True)
class TestConfig:
    device_host: str
    appium_url: str
    timeout: float
    android_app: str
    app_package: str
    app_activity: str
    platform_version: str
    device_name: str
    browserstack_user: str
    browserstack_key: str
    browserstack_app: str


def load_config() -> TestConfig:
    host = _env("DEVICE_HOST", "selenoid").lower()
    if host == "browserstack":
        default_url = "https://hub.browserstack.com/wd/hub"
        default_app = _env("BROWSERSTACK_APP")
    elif host == "selenoid":
        default_url = "https://user1:1234@selenoid.qa.guru/wd/hub"
        default_app = WIKIPEDIA_APK
    else:
        default_url = "http://127.0.0.1:4723/wd/hub"
        default_app = _env("ANDROID_APP")
    return TestConfig(
        device_host=host,
        appium_url=_env("APPIUM_URL", default_url),
        timeout=float(_env("TIMEOUT", "30")),
        android_app=_env("ANDROID_APP") or default_app,
        app_package=_env("APP_PACKAGE", "org.wikipedia.alpha"),
        app_activity=_env("APP_ACTIVITY", "org.wikipedia.main.MainActivity"),
        platform_version=_env("PLATFORM_VERSION", "13.0" if host == "selenoid" else "9.0"),
        device_name=_env("DEVICE_NAME", "Google Pixel 3" if host == "browserstack" else "android"),
        browserstack_user=_env("BROWSERSTACK_USERNAME") or _env("BROWSERSTACK_USER"),
        browserstack_key=_env("BROWSERSTACK_ACCESS_KEY") or _env("BROWSERSTACK_KEY"),
        browserstack_app=_env("BROWSERSTACK_APP"),
    )
