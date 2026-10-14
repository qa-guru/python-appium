import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import has_elements, open_search_field


@allure.title("successfulSearchTest")
def test_successful_search(driver, config):
    wait = WebDriverWait(driver, config.timeout)
    with allure.step("Type search"):
        field = open_search_field(driver, config.timeout)
        field.send_keys("Appium")
    with allure.step("Verify content found"):
        assert wait.until(has_elements)
