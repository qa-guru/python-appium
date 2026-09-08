# python-appium

Python twin of [qa-guru/mobile-tests-22](https://github.com/qa-guru/mobile-tests-22). **pytest + Appium-Python-Client**, no Selene.

This lesson is BrowserStack only. Emulator / real device — next lesson.

| Branch | What |
|--------|------|
| [`main`](https://github.com/qa-guru/python-appium/tree/main) | BrowserStack sample, one test |
| [`driver`](https://github.com/qa-guru/python-appium/tree/driver) | `BrowserstackDriver` + pytest fixture |
| [`attachments`](https://github.com/qa-guru/python-appium/tree/attachments) | Allure screenshot / page source / video |

Same credentials and Wikipedia `bs://` as [mobile-tests-22](https://github.com/qa-guru/mobile-tests-22) first commit. Sample APK: [WikipediaSample.apk](https://www.browserstack.com/app-automate/sample-apps/android/WikipediaSample.apk).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest tests
```
