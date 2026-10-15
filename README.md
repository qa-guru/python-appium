# Мобильные тесты на Python

Учебный проект QA.GURU: поиск в Wikipedia на **pytest + Appium-Python-Client** и отчёт Allure. Без Selene.

Ветка `browserstack-ios` добавляет iOS-маршруты к `selenoid`, которая продолжает примеры [`main`](https://github.com/qa-guru/python-appium/tree/main) → [`driver`](https://github.com/qa-guru/python-appium/tree/driver) → [`attachments`](https://github.com/qa-guru/python-appium/tree/attachments). В Jenkins используется job `python_mobile_tests`.

## Материалы занятия

- [Презентация в PDF](python-mobile-2.pdf) — 16:9, для показа и раздачи.
- [Презентация в HTML](python-mobile-2.html) — открывается без сервера. Стрелки переключают слайды, **F** включает полный экран, **N** показывает заметки преподавателя.
- Этот README — подробные команды настройки и запуска.

## Что есть в проекте

- Создание Android-сессии на эмуляторе, телефоне, Selenoid и BrowserStack.
- Выбор локального устройства через `UDID`.
- Screenshot, XML страницы и видео в Allure.
- Настройки iOS-драйвера для BrowserStack, Simulator и настоящего iPhone.

**Тест поиска кроссплатформенный.** `conftest.py` выбирает Android-локаторы или iOS predicate/accessibility-id по платформе сессии. iOS-прогоны проверены на BrowserStack, Simulator и настоящем iPhone. Это smoke-тест: ввод `Appium` и наличие результатов; открытие статьи он не проверяет.

## Быстрая навигация

- [Python и venv](#1-подготовить-python)
- [Android SDK: macOS, Linux и Windows](#2-подготовить-android-sdk)
- [Appium и Inspector](#3-установить-appium-и-inspector)
- [Запуск Android: локально, Selenoid, BrowserStack](#4-запустить-android-тест)
- [Запуск iOS: BrowserStack, Simulator и iPhone](#5-запустить-ios-тест)
- [Вложения и отчёт Allure](#6-посмотреть-результаты-в-allure)
- [Разбор ошибок](#если-тест-не-запускается)
- [Проверка перед занятием](#перед-занятием)

## 1. Подготовить Python

На занятии используем Python 3.14. Все версии Python-пакетов указаны в `requirements.txt`; не обновляйте Selenium или Appium-клиент отдельно от остальных зависимостей.

### macOS и Linux

Команды выполняются в корне проекта. Если venv уже создан, используйте его; `.env` копируем только при отсутствии файла:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
if [ ! -f .env ]; then
    cp .env.example .env   # optional — defaults already point at the school farm
fi
pytest --collect-only tests
```

### Windows, PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
.\.venv\Scripts\pytest.exe --collect-only tests
```

Активация venv не обязательна: на Windows можно вызывать его Python и pytest напрямую, не меняя Execution Policy.

`--collect-only` проверяет импорт и обнаружение тестов. Он не создаёт мобильную сессию и не проверяет доступ к ферме.

Настройки читаются из переменных окружения и `.env`. Переменные процесса имеют приоритет над `.env`. Реальные пароли и ключи не добавляйте в Git; файл `.env.example` нужен только как образец.

## 2. Подготовить Android SDK

Нужны **JDK 21**, **Android Studio** и **Android SDK**. В SDK Manager установите:

- Android SDK Platform для выбранной версии Android;
- Platform-Tools — здесь находится `adb`;
- Build-Tools и Command-line Tools;
- Android Emulator и system image, если используете эмулятор.

В Device Manager создайте AVD. Архитектура образа должна подходить компьютеру: arm64 для Apple Silicon, подходящий x86_64-образ для Intel/AMD. APK тоже должен поддерживать архитектуру устройства.

### macOS

Путь к SDK проверьте в Android Studio. Для стандартного расположения:

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$JAVA_HOME/bin:$PATH"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
export PATH="$ANDROID_HOME/emulator:$PATH"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
java -version
adb version
emulator -list-avds
```

### Linux

Укажите каталог установленного JDK 21. SDK часто находится в `$HOME/Android/Sdk`, но окончательный путь берите из Android Studio:

```bash
export JAVA_HOME="/path/to/jdk-21"
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$JAVA_HOME/bin:$PATH"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
export PATH="$ANDROID_HOME/emulator:$PATH"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
java -version
adb version
emulator -list-avds
```

`/path/to/jdk-21` — место для вашего пути, не готовое значение. Если инструменты нужны в каждом терминале, сохраните проверенные переменные в настройках своей shell.

### Windows, PowerShell

Замените пример пути к JDK на свой:

```powershell
$env:JAVA_HOME = "C:\Tools\jdk-21"
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:Path = "$env:JAVA_HOME\bin;" +
    "$env:ANDROID_HOME\platform-tools;" +
    "$env:ANDROID_HOME\emulator;" +
    "$env:ANDROID_HOME\cmdline-tools\latest\bin;" + $env:Path
java -version
adb version
emulator -list-avds
```

Для постоянных переменных используйте настройки своей учётной записи Windows и затем откройте новый терминал.

## 3. Установить Appium и Inspector

Python-клиент, Appium Server, драйверы и Inspector — разные инструменты. Сервер устанавливается через npm, Python-клиент — через `requirements.txt`.

Для учебного окружения используем Node.js 26, npm 10+ и следующие версии:

```bash
npm install -g appium@3.5.0
appium driver install uiautomator2@6.0.0
appium --version
appium driver list --installed
appium driver doctor uiautomator2
```

UiAutomator2 6 поддерживает Android 8.0 и новее. Отдельно проверьте минимальную версию Android выбранного APK.

[Appium Inspector](https://appium.github.io/appium-inspector/latest/quickstart/installation/) устанавливается отдельно. Скачайте официальный release для своей ОС и архитектуры. Inspector подключается к работающему Appium Server: host, port, SSL и base path должны совпадать с настройкой `APPIUM_URL`.

В Appium 2 и 3 путь по умолчанию — `/`. Если сервер запущен с `--base-path /wd/hub`, клиент тоже должен использовать `/wd/hub`. Это зависит от настройки сервера, а не от номера его версии.

В Zero Design System используйте уже зарегистрированный Appium-стенд. Из корня этого рабочего пространства:

```bash
python3 scripts/stands/ensure.py appium-wd-hub
```

Укажите возвращённый endpoint в `APPIUM_URL`. Не запускайте второй сервер на занятом порту и не перезапускайте общий стенд. В отдельном учебном окружении сервер запускается штатным способом этого окружения; команды установки выше его не запускают.

## 4. Запустить Android-тест

Следующие Bash-команды предполагают активированный venv. На Windows задайте те же значения через `$env:NAME = "value"` и используйте `.\.venv\Scripts\pytest.exe`.

### Эмулятор

Запустите AVD в Device Manager и дождитесь старта Android:

```bash
adb devices -l
```

Устройство должно иметь статус `device`, не `offline` или `unauthorized`. Если подключено несколько устройств, укажите `UDID` из этого списка.

Локально используем [официальную stable-сборку Wikipedia 50611-r-2026-10-07](https://releases.wikimedia.org/mobile/android/wikipedia/stable/wikipedia-50611-r-2026-10-07.apk). Сохраните APK на машине Appium Server и укажите путь к нему:

```bash
# pinned Wikipedia stable → ANDROID_APP (a local file path, not a URL)
DEVICE_HOST=emulator ANDROID_APP=./wikipedia-50611-r-2026-10-07.apk pytest tests
```

SHA-256 из описания сборки в `config.py`:

```text
bb95806f913f6b377c9453e92d4345006a9dff6a051b9380c46cf2f9d7fa4a19
```

Проверить скачанный файл можно через `shasum -a 256` на macOS, `sha256sum` на Linux или `Get-FileHash -Algorithm SHA256` на Windows. Версию APK между прогонами не меняем: вместе с ней могут измениться экран первого запуска и локаторы.

### Настоящий Android

Включите Developer Options и USB debugging, подключите телефон по USB и подтвердите Trust This Computer. Затем снова проверьте `adb devices -l`.

Подставьте настоящий serial вместо `<serial>`:

```bash
# a real device (USB debugging on) or a specific emulator — serial from `adb devices`
DEVICE_HOST=real ANDROID_APP=./wikipedia-50611-r-2026-10-07.apk UDID="<serial>" pytest tests
```

Используйте учебное устройство. В Android-настройках проекта стоит `noReset=False`; не запускайте их на личном приложении с важными данными без согласия владельца.

### Selenoid

Для Selenoid локальный Appium не нужен: сессия создаётся на учебной Android-ферме. Настройки доступа — `SELENOID_URL`, `SELENOID_USER`, `SELENOID_PASSWORD` (или `SELENOID_PASS`). Пароль передаётся отдельно через `AppiumClientConfig`, а не вставляется в URL.

```bash
DEVICE_HOST=selenoid pytest tests
```

В этой ветке по умолчанию используется Android `16.0`. Другую доступную версию можно выбрать через `PLATFORM_VERSION`; наличие версии проверяйте по каталогу фермы.

На ферме оставлен **Wikipedia sample 2017 года**, package `org.wikipedia.alpha`. Современная stable-сборка в предыдущих запусках на этой ферме зависала и давала таймауты, поэтому по умолчанию используется sample. Для локального эмулятора и телефона берём stable, package `org.wikipedia`.

Это разные интерфейсы. В stable поиск находится в нижнем меню, сначала может появиться окно Search widget, а поле ввода отображается после нажатия Search Wikipedia. В `conftest.py` есть локаторы и действия для обеих Android-сборок.

Selenoid выбирает контейнер по `browserName=android` и `browserVersion`. В этом режиме не передаём `appium:appPackage`: Appium внутри контейнера отклоняет сочетание. `selenoid:options` включает VNC и запись видео.

Если заменяете APK фермы, `ANDROID_APP` должен быть URL, доступным с фермы, а не путём на ноутбуке. iOS на этом Selenoid не поддерживается.

### BrowserStack

Задайте в `.env` или переменных процесса свои `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY` и `BROWSERSTACK_APP`, затем:

```bash
DEVICE_HOST=browserstack pytest tests
```

`BROWSERSTACK_APP` — идентификатор загруженной сборки вида `bs://…`. По умолчанию `BROWSERSTACK_PLATFORM=Android`; для iOS используйте отдельную команду ниже. На своём iPhone можно запускать App Store приложение по bundleId, но это не заменяет загрузку приложения для BrowserStack App Automate.

## 5. Запустить iOS-тест

Для локального iOS нужны Mac, полный Xcode, установленный runtime и XCUITest. Лицензию и запросы доверия подтверждает владелец компьютера/телефона.

```bash
xcode-select -p
xcodebuild -version
xcrun simctl list devices available
appium driver install xcuitest@12.8.0
appium driver doctor xcuitest
```

Проверьте [совместимость Xcode, macOS, iOS и XCUITest](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/system-requirements/).

Тест `tests/test_search.py` кроссплатформенный: `conftest.py` выбирает набор локаторов по `platformName` сессии (UiAutomator на Android → predicate/accessibility-id на iOS). iOS-ветка проверена на iPhone 17 Simulator (iOS 26.5) — onboarding с кнопками `App Onboarding * Button`, поиск через Tab Bar `Search`, поле `XCUIElementTypeSearchField`.

### Закреплённая Wikipedia fixture

Исходники учебной сборки живут в [qa-guru/wikipedia-ios, ветка qa-guru-fixture](https://github.com/qa-guru/wikipedia-ios/tree/qa-guru-fixture), отдельно от тестов. Для повторов используем Release **[qaguru-ios-fixture-v1.0.0](https://github.com/qa-guru/wikipedia-ios/releases/tag/qaguru-ios-fixture-v1.0.0)**, а не `latest`:

- [Wikipedia-browserstack.ipa](https://github.com/qa-guru/wikipedia-ios/releases/download/qaguru-ios-fixture-v1.0.0/Wikipedia-browserstack.ipa) — ARM64 device-сборка с ad-hoc подписью для переподписи в BS; не устанавливается напрямую на real iPhone.
- [Wikipedia-simulator.app.zip](https://github.com/qa-guru/wikipedia-ios/releases/download/qaguru-ios-fixture-v1.0.0/Wikipedia-simulator.app.zip) — universal ARM64/x86_64 `.app`; runtime проверен на ARM64, x86_64 не проверен.
- [SHA256SUMS.txt](https://github.com/qa-guru/wikipedia-ios/releases/download/qaguru-ios-fixture-v1.0.0/SHA256SUMS.txt) и [LICENSE.txt](https://github.com/qa-guru/wikipedia-ios/releases/download/qaguru-ios-fixture-v1.0.0/LICENSE.txt).

В этих артефактах нет персональных provisioning profiles или Apple signing certificates. Bundle ID — `com.qaguru.wikipedia`, app group — `group.com.qaguru.wikipedia`, минимум iOS — `17.6`. Real-сборка подписывается своей Team из исходников fork; семидневное ограничение Personal Team этим Release не отменяется.

SHA-256 закреплён здесь независимо от скачиваемого checksum-файла:

```text
28a2102a2f52d0e92de6da410cdc71c02399767c54989d6ce671ef2075f41b3b  Wikipedia-browserstack.ipa
8492824f7ca580d00167decd5631733778ca78bbedd86b71a6764bb761b29791  Wikipedia-simulator.app.zip
```

Скачайте вне Git-дерева и проверьте до загрузки / установки:

```bash
FIXTURE_DIR="${TMPDIR:-/tmp}/qaguru-wikipedia-ios-v1.0.0"
mkdir -p "$FIXTURE_DIR"
curl --fail --location --output "$FIXTURE_DIR/Wikipedia-browserstack.ipa" \
  https://github.com/qa-guru/wikipedia-ios/releases/download/qaguru-ios-fixture-v1.0.0/Wikipedia-browserstack.ipa
curl --fail --location --output "$FIXTURE_DIR/Wikipedia-simulator.app.zip" \
  https://github.com/qa-guru/wikipedia-ios/releases/download/qaguru-ios-fixture-v1.0.0/Wikipedia-simulator.app.zip
printf '%s  %s\n' \
  28a2102a2f52d0e92de6da410cdc71c02399767c54989d6ce671ef2075f41b3b "$FIXTURE_DIR/Wikipedia-browserstack.ipa" \
  8492824f7ca580d00167decd5631733778ca78bbedd86b71a6764bb761b29791 "$FIXTURE_DIR/Wikipedia-simulator.app.zip" \
  | shasum -a 256 -c -
```

Для Simulator распакуйте `Wikipedia.app` через `ditto -x -k "$FIXTURE_DIR/Wikipedia-simulator.app.zip" "$FIXTURE_DIR/simulator"` и задайте `IOS_APP="$FIXTURE_DIR/simulator/Wikipedia.app"`. Для BS используйте `$FIXTURE_DIR/Wikipedia-browserstack.ipa` в upload-команде ниже с `ios_app_groups_support=true`, затем задайте возвращённый `BROWSERSTACK_APP=bs://…` своей учётки. BS хранит загруженные приложения ограниченное время, поэтому его app ID не заменяет закреплённый GitHub Release.

### BrowserStack iOS

Нужна `.ipa`, собранная для физического устройства, и App Automate Username / Access Key в `.env` или окружении. Выбирайте устройство и OS из [каталога BrowserStack](https://www.browserstack.com/docs/app-automate/api-reference/appium/devices), учитывая deployment target приложения: у проверенной Wikipedia минимум iOS `17.6`.

При загрузке Wikipedia обязательно передайте `ios_app_groups_support=true`: BrowserStack переподписывает приложение, а `MWKDataStore` требует доступ к app group. Без её entitlement приложение может упасть при запуске. [Документация переподписи](https://www.browserstack.com/docs/app-automate/appium/resign-ios-apps).

Из корня проекта, с активированным venv, загрузите IPA; замените `/path/to/Wikipedia.ipa` своим путём:

```bash
python - <<'PY'
import requests
from config import load_config

config = load_config()
with open("/path/to/Wikipedia.ipa", "rb") as app:
    response = requests.post(
        "https://api-cloud.browserstack.com/app-automate/upload",
        auth=(config.browserstack_user, config.browserstack_key),
        files={"file": ("Wikipedia.ipa", app, "application/octet-stream")},
        data={"ios_app_groups_support": "true"},
        timeout=120,
    )
response.raise_for_status()
print(response.json()["app_url"])
PY
```

Полученный `bs://…` задайте в `BROWSERSTACK_APP`. Credentials в команды не подставляйте. Переменные процесса имеют приоритет над `.env`; при смене учётки уберите старые exports `BROWSERSTACK_USERNAME` / `BROWSERSTACK_ACCESS_KEY` и их aliases `BROWSERSTACK_USER` / `BROWSERSTACK_KEY`.

Проверенный вариант запуска — iPhone 16 Pro Max / iOS 27. Доступность этой конфигурации сверяйте с каталогом:

```bash
RUN_ID="$(date +%Y%m%d-%H%M%S)"
DEVICE_HOST=browserstack BROWSERSTACK_PLATFORM=iOS \
APPIUM_URL=https://hub.browserstack.com/wd/hub \
DEVICE_NAME="iPhone 16 Pro Max" PLATFORM_VERSION=27 \
pytest tests/test_search.py --alluredir="allure-results/ios-browserstack-$RUN_ID"
```

Локальный Appium и подпись WDA вашей Personal Team для BS не нужны. `.app` для Simulator не заменяет device `.ipa`.

### Simulator

Нужна `.app`, собранная для `iphonesimulator`, а не device `.ipa`. Для Simulator не требуется платная Apple Developer учётная запись.

В [Wikipedia iOS](https://github.com/wikimedia/wikipedia-ios) используются проект `Wikipedia.xcodeproj` и scheme `Wikipedia`. Сборку лучше подготовить до занятия. Upstream `scripts/setup` устанавливает SwiftLint/ClangFormat и Git hook; сначала прочитайте скрипт, не запускайте его автоматически на каждом рабочем месте.

Пример команд в подготовленной копии исходников (проверено: Xcode 27.0, iPhone 17 / iOS 26.5):

```bash
# проект требует генерируемый файл конфигурации (scripts/setup_bundle_id делает то же самое)
if [ ! -f Configurations/OpenSourceDebug.xcconfig ]; then
    printf 'DEVELOPMENT_TEAM=AKK7J2GV64\nSIGNING_DISAMBIGUATOR=\n' \
      > Configurations/OpenSourceDebug.xcconfig
fi

xcodebuild \
  -project Wikipedia.xcodeproj \
  -scheme Wikipedia \
  -configuration Debug \
  -sdk iphonesimulator \
  -derivedDataPath ./build \
  build
# → build/Products/Debug-iphonesimulator/Wikipedia.app
```

Не добавляйте `CODE_SIGNING_ALLOWED=NO`: без подписи в бинарь не попадают entitlements, `group.org.wikimedia.wikipedia` не выделяется, и приложение падает при запуске в `MWKDataStore` (SIGABRT на nil-пути контейнера). Для симулятора достаточно «Sign to Run Locally».

После смены bundle ID / app group или отключения extensions используйте свежий `derivedDataPath`. В старой `.app` могут остаться `.appex` с прежними IDs, что приводит к `Mismatched bundle IDs` при установке. Не удаляйте чужие артефакты ради пересборки.

Проверьте архитектуру и фактический путь к полученной `.app`. Затем задайте настройки; значения в угловых скобках замените данными из Xcode/simctl:

```bash
# simulator — needs a simulator build of the app (xcodebuild -sdk iphonesimulator)
export DEVICE_HOST=ios_simulator
export APPIUM_URL="<verified-local-appium-endpoint>"
export IOS_APP="./Wikipedia.app"
export UDID="<simulator-udid>"
export DEVICE_NAME="<simulator-name>"
export PLATFORM_VERSION="<ios-version>"
RUN_ID="$(date +%Y%m%d-%H%M%S)"
pytest tests/test_search.py --alluredir="allure-results/ios-simulator-$RUN_ID"
```

`DEVICE_NAME` и `PLATFORM_VERSION` задайте явно: их общие значения по умолчанию рассчитаны на Android. Переменная `PLATFORM` в этой ветке не используется; платформа выбирается через `DEVICE_HOST`.

### Настоящий iPhone

Установите Wikipedia из App Store. Для управления UI подпишите WebDriverAgent и проверьте его запуск на этом телефоне:

1. Подключите iPhone и выполните pairing в Xcode.
2. На телефоне подтвердите доверие компьютеру.
3. Включите Developer Mode и UI Automation.
4. Откройте WDA: `appium driver run xcuitest open-wda`.
5. Выберите свою Team, настройте подпись и provisioning для устройства.

[Инструкция по подписи WDA](https://appium.github.io/appium-xcuitest-driver/latest/getting-started/provisioning-profile/) описывает бесплатный Personal Team и платный Apple Developer account. У бесплатных профилей есть ограничения и срок действия; проверьте подпись перед занятием.

По [официальным данным Apple](https://itunes.apple.com/lookup?id=324715238), bundleId Wikipedia из App Store — **`org.wikimedia.wikipedia`**. На 14.10.2026 указана версия `2026.09.29`, минимум iOS `17.6`. Пересобирать Wikipedia для этого способа не нужно, но WDA всё равно должен быть подготовлен.

```bash
# real iPhone — App Store build by bundleId, WDA must be signed for the device
export DEVICE_HOST=ios_real
export APPIUM_URL="<verified-local-appium-endpoint>"
export UDID="<iphone-udid>"
export DEVICE_NAME="<iphone-name>"
export PLATFORM_VERSION="<ios-version>"
export BUNDLE_ID=org.wikimedia.wikipedia
export XCODE_ORG_ID="<apple-team-id>"
export WDA_BUNDLE_ID="<unique-wda-bundle-id>"
export WDA_LOCAL_PORT="<checked-free-port>"
export WDA_ALLOW_PROVISIONING=false
RUN_ID="$(date +%Y%m%d-%H%M%S)"
pytest tests/test_search.py --alluredir="allure-results/ios-real-$RUN_ID"
```

Замените значения в угловых скобках своими. `XCODE_ORG_ID` и `UDID` обязательны. Default `BUNDLE_ID` — `org.wikimedia.wikipedia`; для собственной подписанной сборки задайте её ID явно. Проверенный scratch-вариант использовал `com.qaguru.wikipedia` и app group `group.com.qaguru.wikipedia`.

`WDA_BUNDLE_ID` должен быть доступен вашей Apple Team: профиль создаётся для runner с суффиксом `.xctrunner`. `WDA_LOCAL_PORT` по умолчанию `8100`; если порт занят, согласуйте другой свободный порт через реестр стендов, а не останавливайте чужой процесс. В проверенном real-прогоне использовался `8101`.

`WDA_ALLOW_PROVISIONING=false` по умолчанию. Только с разрешения владельца Team включайте `WDA_ALLOW_PROVISIONING=true`: это передаёт `allowProvisioningDeviceRegistration` и разрешает Xcode создать/обновить provisioning profile и зарегистрировать указанное устройство. Personal Team выдаёт профили на [7 дней](https://developer.apple.com/help/account/basics/about-your-developer-account/); после истечения потребуется обновить подпись.

Держите iPhone разблокированным с включённым экраном до конца прогона. Если iOS показывает Untrusted Developer, владелец телефона должен подтвердить доверие в Settings → General → VPN & Device Management. Если предложено Allow & Restart, завершите этот шаг вручную.

В примерах предустановленного приложения Appium рекомендует `noReset=True`; в текущем `_ios_real` эта настройка явно не выставлена. Согласуйте состояние приложения до первого запуска, особенно на личном телефоне.

## 6. Посмотреть результаты в Allure

Установите CLI для отчёта отдельно от Python-плагина:

```bash
npm install -g allure-commandline@2.34.1
allure --version
```

Для этих команд используем Allure CLI 2 и JDK 21. В `pytest.ini` уже включён `--alluredir=allure-results`. Чтобы результаты разных запусков не смешивались, можно выбрать новый каталог:

```bash
RUN_ID="$(date +%Y%m%d-%H%M%S)"
pytest tests --alluredir="allure-results/$RUN_ID"
allure generate "allure-results/$RUN_ID" \
  -o "allure-report/$RUN_ID"
```

Отчёт открывайте штатным способом своего окружения. В рабочем пространстве со стендами используйте зарегистрированный просмотрщик. Не открывайте `index.html` Allure как обычный файл: браузер может заблокировать загрузку данных отчёта.

Что прикладывает проект:

- **Screenshot и XML** — до завершения сессии.
- **Screenshot on failure** — в момент падения теста, до teardown. Для ошибки setup есть отдельный сбор.
- **Локальное видео** — если драйвер поддерживает `start_recording_screen`; запись останавливается до `quit()`.
- **Selenoid video** — скачивается после `quit()`, когда ферма завершит MP4.
- **BrowserStack video и ссылка на сессию** — через App Automate API после `quit()`.

Если helper не смог получить вложение, он добавляет пояснение в отчёт. При неудачном старте локальной записи фикстура продолжает тест без видео; его наличие нужно проверить отдельно. Автоматического сбора logcat или логов Appium Server в этой ветке пока нет.

## Если тест не запускается

- **Сессия не создаётся:** проверьте `APPIUM_URL`, base path, установленный driver и доступ к серверу.
- **adb показывает unauthorized:** подтвердите запрос на телефоне. Для offline проверьте подключение и дождитесь загрузки Android.
- **APK не найден:** `ANDROID_APP` локального профиля должен быть файлом на машине Appium Server. На ферме нужен URL.
- **Не найден элемент:** откройте screenshot и XML; проверьте сборку приложения, onboarding, локаль и окно Search widget.
- **xcodebuild 65/70:** проверьте подпись WDA, provisioning и выбранный Xcode/iOS.
- **Нет видео:** проверьте поддержку локальной записи или `enableVideo` фермы, завершение сессии и доступ к MP4.
- **Ошибка сертификата HTTPS:** не отключайте проверку TLS. Проверьте зависимости venv, CA-сертификаты и настройки сети. Helpers проекта используют `requests` с certifi.

## Перед занятием

- Выберите стартовую версию кода и проверьте один Android-тест на показываемых устройствах.
- Подготовьте конкретный APK и проверьте его SHA-256.
- Сверьте host, base path и доступ к Appium/Selenoid.
- Проверьте screenshot, XML и видео после обычного прогона и контролируемого падения.
- Для iOS подготовьте simulator `.app`, установленное приложение / подписанный WDA на iPhone или device `.ipa` для BS с поддержкой app groups. Запускайте тот же `tests/test_search.py` с настройками соответствующего маршрута.
- Сверьте программу и домашнее задание с GetCourse: при подготовке этих материалов доступ к страницам уроков требовал авторизации.

Для проверки или правки самих материалов мобильные сессии запускать не нужно. HTML работает без HTTP-сервера; PDF — печатная версия слайдов, заметки преподавателя остаются только в HTML.
