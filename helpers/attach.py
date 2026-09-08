from __future__ import annotations

import allure
from appium.webdriver.webdriver import WebDriver

from config import TestConfig
from helpers import browserstack


def screenshot(driver: WebDriver) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name="screenshot",
        attachment_type=allure.attachment_type.PNG,
    )


def page_source(driver: WebDriver) -> None:
    allure.attach(
        driver.page_source,
        name="page source",
        attachment_type=allure.attachment_type.XML,
    )


def video(config: TestConfig, session_id: str) -> None:
    if config.device_host != "browserstack":
        return
    src = browserstack.video_url(config, session_id)
    html = (
        "<html><body><video width='100%' height='100%' controls autoplay>"
        f"<source src='{src}' type='video/mp4'></video></body></html>"
    )
    allure.attach(html, name="video", attachment_type=allure.attachment_type.HTML)
