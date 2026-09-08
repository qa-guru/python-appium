import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# todo bad practice - move from public repo (to .properties / ci secrets
USER = "yvikbrwprpkpbzor_L2F1zU"
KEY = "xuyDnBxEyiwqe8i55ZT6"


def test_successful_search():
    options = UiAutomator2Options()

    # Set your access credentials
    options.set_capability("browserstack.user", USER)
    options.set_capability("browserstack.key", KEY)

    # Set URL of the application under test
    options.set_capability("app", "bs://4a3a60b0c95582cbe777c8fe604110542238aced")

    # Specify device and os_version for testing
    options.set_capability("platformName", "android")
    options.set_capability("deviceName", "Samsung Galaxy S22 Ultra")
    options.set_capability("platformVersion", "12.0")

    # Set other BrowserStack capabilities
    options.set_capability("project", "First Python Project")
    options.set_capability("build", "browserstack-build-1")
    options.set_capability("name", "first_test")

    driver = webdriver.Remote(
        f"https://{USER}:{KEY}@hub.browserstack.com/wd/hub",
        options=options,
    )

    # skip onboarding screen (back)
    greeting_title = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Wikipedia"))
    )

    driver.back()

    search_element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((AppiumBy.ID, "org.wikipedia.alpha:id/nav_tab_search"))
    )
    search_element.click()

    search_element = WebDriverWait(driver, 30).until(
        # EC.element_to_be_clickable((AppiumBy.XPATH, "//android.view.View[@content-desc='Close']"))
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Close"))
    )
    search_element.click()

    search_element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((AppiumBy.ID, "org.wikipedia.alpha:id/search_text_view"))
    )
    search_element.click()

    insert_text_element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((AppiumBy.ID, "org.wikipedia.alpha:id/search_src_text"))
    )
    insert_text_element.send_keys("Appium")

    time.sleep(5) # move from sleep

    titles = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (AppiumBy.ID, "org.wikipedia.alpha:id/fragment_search_results")
        )
    )
    titles = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
    assert any("Appium" in (t.text or "") for t in titles)

    # all_products_name = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
    # assert len(all_products_name) > 0

    driver.quit()
