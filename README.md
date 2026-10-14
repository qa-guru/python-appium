# python-appium · selenoid

Not this BrowserStack lesson. This branch is the school farm ([python_mobile_tests](https://jenkins.qa.guru/job/python_mobile_tests/)). Emulator / real device — next lesson.

This lesson's ladder: [`main`](https://github.com/qa-guru/python-appium/tree/main) → [`driver`](https://github.com/qa-guru/python-appium/tree/driver) → [`attachments`](https://github.com/qa-guru/python-appium/tree/attachments).

---

Python twin of [qa-guru/mobile-tests-22](https://github.com/qa-guru/mobile-tests-22): Wikipedia search on a device.

**pytest + Appium-Python-Client.** No Selene.

| Java | Here |
|------|------|
| `$(accessibilityId("Search Wikipedia"))` | `AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia"` |
| `BrowserstackDriver` | `DEVICE_HOST=browserstack` |
| `./gradlew selenoid` | `DEVICE_HOST=selenoid` (Jenkins default) |

Jenkins: [python_mobile_tests](https://jenkins.qa.guru/job/python_mobile_tests/).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env   # optional — defaults already point at the school farm
```

All configuration is env-driven (`DEVICE_HOST`, `SELENOID_*`, `BROWSERSTACK_*`,
`ANDROID_APP`, `PLATFORM_VERSION` …). Credentials travel as HTTP basic auth via
`AppiumClientConfig` — never embedded in `APPIUM_URL`, so they don't leak into
logs or the Allure report.

## Routes

Selenoid — school farm, Android only:

```bash
DEVICE_HOST=selenoid pytest tests
```

- `browserName=android` + `browserVersion` (live catalog: `5.1`, `15.0`, `16.0`;
  default `16.0`, override with `PLATFORM_VERSION`).
- Selenoid routes on `browserName` — **don't** send `appium:appPackage` next to
  it, Appium inside the container rejects the combination.
- `selenoid:options` enables VNC + video. `conftest` downloads
  `/video/<session>.mp4` after `driver.quit()` (the farm still muxes the file —
  the attach helper polls until it's published).

The farm keeps the 20 MB 2017 Wikipedia **sample** APK
(`org.wikipedia.alpha`) as its default app: the current stable APK is 84 MB and
the farm's emulators die under that load (ANR storm, session timeouts). The
stable build is for local emulator/real — locators in `conftest.py` and the test
cover both packages (`org.wikipedia` / `org.wikipedia.alpha`).

Emulator / real device — local Appium (`http://127.0.0.1:4723`, Appium 3 serves
on `/`; for an old Appium 2 setup use `appium --base-path /wd/hub`). The server
needs `ANDROID_HOME` exported and `platform-tools` on `PATH`:

```bash
# pinned Wikipedia stable → ANDROID_APP (a local file path, not a URL)
DEVICE_HOST=emulator ANDROID_APP=./wikipedia-50611-r-2026-10-07.apk pytest tests

# a real device (USB debugging on) or a specific emulator — serial from `adb devices`
DEVICE_HOST=real ANDROID_APP=./wikipedia-50611-r-2026-10-07.apk UDID=<serial> pytest tests
```

Stable Wikipedia differs from the old alpha sample: search lives in the bottom
nav (`nav_tab_search`), the first tap opens a "Search widget" promo sheet, and
the input field is a Compose `EditText` that appears only after tapping the
"Search Wikipedia" hint. `conftest.py` carries locator sets for both channels.

iOS (macOS only, Appium + xcuitest driver):

```bash
# simulator — needs a simulator build of the app (xcodebuild -sdk iphonesimulator)
DEVICE_HOST=ios_simulator IOS_APP=./Wikipedia.app pytest tests

# real iPhone — App Store build by bundleId, WDA must be signed for the device
DEVICE_HOST=ios_real UDID=<iphone-udid> BUNDLE_ID=org.wikipedia pytest tests
```

Prerequisites: full Xcode (not just Command Line Tools), license accepted
(`sudo xcodebuild -license accept`), xcuitest driver
(`appium driver install xcuitest`). For `ios_real` the WebDriverAgent needs a
signing profile — free Personal Team works (7-day provisioning).

BrowserStack (own account, like mobile-tests-22):

```bash
DEVICE_HOST=browserstack \
  BROWSERSTACK_USERNAME=… BROWSERSTACK_ACCESS_KEY=… BROWSERSTACK_APP=bs://… \
  pytest tests
```

## Attachments (Allure)

| What | When |
|------|------|
| screenshot + page source | teardown, while the session is alive |
| screenshot on failure | `pytest_runtest_makereport` — the failing state, before teardown |
| video (mp4) + report link | local: on-device screenrecord, stopped before `quit()`; farms: `/video/<session>.mp4` / BrowserStack session API, polled after `quit()` |

Every attachment is best-effort: an artifact that can't be fetched shows up as a
diagnostic note in the report and never masks the test's own result.

```bash
pytest tests
allure serve allure-results
```

## Notes

- `onboarding` in `conftest.py` — the fixture walks the Wikipedia onboarding
  (`Skip`/`Next`/old `fragment_onboarding_*` ids) and dismisses Android system
  dialogs (ANR "Wait"/"OK") before the test starts.
- `requirements.txt` is pinned; Appium-Python-Client ≥ 6 is required for
  `AppiumClientConfig`.
- macOS Python quirk: if `urlopen` fails with `CERTIFICATE_VERIFY_FAILED`,
  that's the missing system CA bundle — this repo uses `requests` (bundled
  certifi), so install requirements and the problem is gone.
