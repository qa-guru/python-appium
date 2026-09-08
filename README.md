# python-appium

Python twin of [qa-guru/mobile-tests-22](https://github.com/qa-guru/mobile-tests-22). **pytest + Appium-Python-Client**, no Selene.

This lesson is BrowserStack only. Emulator / real device — next lesson.

| Branch | What |
|--------|------|
| [`main`](https://github.com/qa-guru/python-appium/tree/main) | BrowserStack sample, one test |
| [`driver`](https://github.com/qa-guru/python-appium/tree/driver) | `BrowserstackDriver` + pytest fixture |
| [`attachments`](https://github.com/qa-guru/python-appium/tree/attachments) | Allure screenshot / page source / video |

After the test: Allure screenshot, page source, BrowserStack video (`helpers/attach.py`).

Caps live in `drivers/browserstack.py`. Keys come from the environment, not from the test.

```bash
cp .env.example .env
# fill BROWSERSTACK_USERNAME / BROWSERSTACK_ACCESS_KEY / BROWSERSTACK_APP

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest tests
```
