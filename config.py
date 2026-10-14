"""Env — Java `-DdeviceHost=` / `-Dbrowserstack.user=` for Python."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()

# Default apps per route. Selenoid: the 20 MB 2017 alpha sample — the school
# farm's emulators choke on the 84 MB stable APK (ANR storm, dead sessions).
# Local emulator/real: pinned Wikipedia stable (org.wikipedia), official channel.
# SHA-256 bb95806f913f6b377c9453e92d4345006a9dff6a051b9380c46cf2f9d7fa4a19
SELENOID_APK = (
    "https://www.browserstack.com/app-automate/sample-apps/android/WikipediaSample.apk"
)
WIKIPEDIA_STABLE_APK = (
    "https://releases.wikimedia.org/mobile/android/wikipedia/stable/"
    "wikipedia-50611-r-2026-10-07.apk"
)

# School farm endpoint + its public guest account (already in this repo's git
# history and the course wiki). Credentials stay out of the URL — they travel
# as HTTP basic auth via AppiumClientConfig / video fetch auth.
SELENOID_URL = "https://selenoid.qa.guru/wd/hub"
SELENOID_USER = "user1"
SELENOID_PASSWORD = "1234"


def _env(name: str, default: str = "") -> str:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip()


def _selenoid_endpoint() -> tuple[str, str, str]:
    """(clean hub url, user, password) — creds from env, or embedded in SELENOID_URL."""
    url = _env("SELENOID_URL", SELENOID_URL)
    parts = urlsplit(url)
    user = _env("SELENOID_USER") or (parts.username or "") or SELENOID_USER
    password = (
        _env("SELENOID_PASSWORD")
        or _env("SELENOID_PASS")
        or (parts.password or "")
        or SELENOID_PASSWORD
    )
    if parts.username:
        netloc = (parts.hostname or "") + (f":{parts.port}" if parts.port else "")
        url = urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    return url, user, password


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
    udid: str
    ios_app: str
    bundle_id: str
    xcode_org_id: str
    wda_bundle_id: str
    selenoid_user: str
    selenoid_password: str = field(repr=False)
    browserstack_user: str = field(repr=False)
    browserstack_key: str = field(repr=False)
    browserstack_app: str = field(repr=False)
    browserstack_platform: str = "Android"
    wda_local_port: int = 8100
    wda_allow_provisioning: bool = False


def load_config() -> TestConfig:
    host = _env("DEVICE_HOST", "selenoid").lower()
    selenoid_url, selenoid_user, selenoid_password = _selenoid_endpoint()
    if host == "browserstack":
        default_url = "https://hub.browserstack.com/wd/hub"
        default_app = _env("BROWSERSTACK_APP")
    elif host == "selenoid":
        default_url = selenoid_url
        default_app = SELENOID_APK
    else:
        default_url = "http://127.0.0.1:4723"
        default_app = _env("ANDROID_APP")
    return TestConfig(
        device_host=host,
        appium_url=_env("APPIUM_URL", default_url),
        timeout=float(_env("TIMEOUT", "30")),
        android_app=_env("ANDROID_APP") or default_app,
        app_package=_env(
            "APP_PACKAGE", "org.wikipedia.alpha" if host == "selenoid" else "org.wikipedia"
        ),
        app_activity=_env("APP_ACTIVITY", "org.wikipedia.main.MainActivity"),
        platform_version=_env("PLATFORM_VERSION", "16.0" if host == "selenoid" else "9.0"),
        device_name=_env("DEVICE_NAME", "Google Pixel 3" if host == "browserstack" else "android"),
        udid=_env("UDID"),
        ios_app=_env("IOS_APP"),
        bundle_id=_env("BUNDLE_ID", "org.wikimedia.wikipedia"),
        xcode_org_id=_env("XCODE_ORG_ID"),
        wda_bundle_id=_env("WDA_BUNDLE_ID", "io.appium.WebDriverAgentRunner"),
        selenoid_user=selenoid_user,
        selenoid_password=selenoid_password,
        browserstack_user=_env("BROWSERSTACK_USERNAME") or _env("BROWSERSTACK_USER"),
        browserstack_key=_env("BROWSERSTACK_ACCESS_KEY") or _env("BROWSERSTACK_KEY"),
        browserstack_app=_env("BROWSERSTACK_APP"),
        browserstack_platform=_env("BROWSERSTACK_PLATFORM", "Android"),
        wda_local_port=int(_env("WDA_LOCAL_PORT", "8100")),
        wda_allow_provisioning=_env("WDA_ALLOW_PROVISIONING", "false").lower() == "true",
    )
