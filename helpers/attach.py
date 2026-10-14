"""Allure attachments — live artifacts while the session is alive, farm video after quit.

Every collector is best-effort: a missing artifact is attached as a diagnostic
note (visible in the report), it never masks the test result or skips quit().
"""

from __future__ import annotations

import base64
import time
from collections.abc import Callable
from urllib.parse import urlsplit

import allure
import requests
from appium.webdriver.webdriver import WebDriver

from config import TestConfig
from helpers import browserstack


def _attach(name: str, kind, produce: Callable[[], bytes | str]) -> None:
    try:
        body = produce()
    except Exception as exc:
        _unavailable(name, exc)
        return
    allure.attach(body, name=name, attachment_type=kind)


def _unavailable(name: str, exc) -> None:
    message = f"{name}: artifact unavailable — {exc}"
    print(f"\n[attach] {message}")
    allure.attach(
        message,
        name=f"{name} (unavailable)",
        attachment_type=allure.attachment_type.TEXT,
    )


def screenshot(driver: WebDriver, name: str = "screenshot") -> None:
    _attach(name, allure.attachment_type.PNG, driver.get_screenshot_as_png)


def page_source(driver: WebDriver) -> None:
    _attach("page source", allure.attachment_type.XML, lambda: driver.page_source)


def screen_recording(driver: WebDriver) -> None:
    """stop_recording_screen must run while the session is alive (local routes)."""
    _attach(
        "video",
        allure.attachment_type.MP4,
        lambda: base64.b64decode(driver.stop_recording_screen()),
    )


def video(config: TestConfig, session_id: str) -> None:
    """Farms publish the mp4 a few seconds after the session ends — poll, then attach."""
    try:
        if config.device_host == "browserstack":
            _browserstack_video(config, session_id)
        elif config.device_host == "selenoid":
            _selenoid_video(config, session_id)
    except Exception as exc:
        _unavailable("video", exc)


def _browserstack_video(config: TestConfig, session_id: str) -> None:
    session = _poll(
        lambda: browserstack.session(config, session_id),
        lambda s: bool(s.get("video_url")),
    )
    if not session or not session.get("video_url"):
        _unavailable("video", "BrowserStack session api never published video_url")
        return
    if session.get("public_url"):
        allure.dynamic.link(session["public_url"], name="BrowserStack session")
    body = browserstack.download(config, session["video_url"])
    allure.attach(
        body, name="video", attachment_type=allure.attachment_type.MP4, extension="mp4"
    )


def _selenoid_video(config: TestConfig, session_id: str) -> None:
    """GET /video/<session>.mp4 on the same hub, basic auth like the session."""
    parts = urlsplit(config.appium_url)
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    url = f"{parts.scheme}://{host}{port}/video/{session_id}.mp4"
    auth = (config.selenoid_user, config.selenoid_password) if config.selenoid_user else None
    status, body = _poll_http(url, auth)
    if status != 200:
        _unavailable("video", f"{url} → HTTP {status}")
        return
    allure.dynamic.link(url, name="Selenoid video")
    allure.attach(
        body, name="video", attachment_type=allure.attachment_type.MP4, extension="mp4"
    )


def _poll(fetch: Callable[[], dict], done: Callable[[dict], bool], attempts: int = 10):
    result = {}
    for _ in range(attempts):
        try:
            result = fetch()
        except Exception:
            result = {}
        if result and done(result):
            return result
        time.sleep(3)
    return result


def _poll_http(url: str, auth, attempts: int = 15) -> tuple[int, bytes]:
    """The farm still muxes the mp4 for a while after the session ends."""
    status, body = 0, b""
    for _ in range(attempts):
        try:
            resp = requests.get(url, auth=auth, timeout=15)
            status, body = resp.status_code, resp.content
        except requests.RequestException:
            status = 0
        if status == 200:
            break
        time.sleep(5)
    return status, body
