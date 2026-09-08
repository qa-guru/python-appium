# python-appium

Python twin of [qa-guru/mobile-tests-22](https://github.com/qa-guru/mobile-tests-22): Wikipedia search on a device.

**pytest + Appium-Python-Client.** No Selene.

| Java | Here |
|------|------|
| `$(accessibilityId("Search Wikipedia"))` | `AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia"` |
| `BrowserstackDriver` | `DEVICE_HOST=browserstack` |
| `./gradlew selenoid` | `DEVICE_HOST=selenoid` (Jenkins default) |

Jenkins: [python_mobile_tests](https://jenkins.qa.guru/job/python_mobile_tests/).

## Local

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Selenoid (same farm as [python_ui_tests](https://jenkins.qa.guru/job/python_ui_tests/)):

```bash
DEVICE_HOST=selenoid pytest tests
```

Emulator (Appium on [`/wd/hub`](http://127.0.0.1:4723/wd/hub)):

```bash
# Wikipedia alpha APK → ANDROID_APP
DEVICE_HOST=emulator ANDROID_APP=./app-alpha-universal-release.apk pytest tests
```

BrowserStack (own account, like mobile-tests-22):

```bash
DEVICE_HOST=browserstack \
  BROWSERSTACK_USERNAME=… BROWSERSTACK_ACCESS_KEY=… BROWSERSTACK_APP=bs://… \
  pytest tests
```
