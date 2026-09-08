# python-appium

Python twin of [qa-guru/java-appium](https://github.com/qa-guru/java-appium). **pytest + Appium-Python-Client**, no Selene.

Historical Java stream: [mobile-tests-22](https://github.com/qa-guru/mobile-tests-22).

This lesson is BrowserStack only. Emulator / real device — next lesson.

| Branch | What |
|--------|------|
| [`main`](https://github.com/qa-guru/python-appium/tree/main) | BrowserStack sample, one test |
| [`driver`](https://github.com/qa-guru/python-appium/tree/driver) | `BrowserstackDriver` + pytest fixture |
| [`attachments`](https://github.com/qa-guru/python-appium/tree/attachments) | Allure screenshot / page source / video |

Jenkins: [python_appium](https://jenkins.qa.guru/job/python_appium/) @ `main`. Java: [java_appium](https://jenkins.qa.guru/job/java_appium/).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest tests
```
