"""Twin of qa-guru/mobile-tests-22 SearchTests — Appium-Python-Client, no Selene."""

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@allure.title("successfulSearchTest")
def test_successful_search(driver, config):
    wait = WebDriverWait(driver, config.timeout)
    with allure.step("Type search"):
        wait.until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia"))
        ).click()
        field = wait.until(
            EC.visibility_of_element_located(
                (AppiumBy.ID, "org.wikipedia.alpha:id/search_src_text")
            )
        )
        field.send_keys("Appium")
    with allure.step("Verify content found"):
        items = wait.until(
            EC.presence_of_all_elements_located(
                (AppiumBy.ID, "org.wikipedia.alpha:id/page_list_item_title")
            )
        )
        assert len(items) > 0
