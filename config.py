"""Env — Java puts keys in BrowserstackDriver; we read them from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str = "") -> str:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip()


@dataclass(frozen=True)
class TestConfig:
    user: str
    key: str
    app: str
    device: str
    os_version: str
    timeout: float


def load_config() -> TestConfig:
    user = _env("BROWSERSTACK_USERNAME") or _env("BROWSERSTACK_USER")
    key = _env("BROWSERSTACK_ACCESS_KEY") or _env("BROWSERSTACK_KEY")
    app = _env("BROWSERSTACK_APP")
    if not user or not key:
        raise ValueError("Set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
    if not app:
        raise ValueError("Set BROWSERSTACK_APP=bs://…")
    return TestConfig(
        user=user,
        key=key,
        app=app,
        device=_env("BROWSERSTACK_DEVICE", "Google Pixel 3"),
        os_version=_env("BROWSERSTACK_OS_VERSION", "9.0"),
        timeout=float(_env("TIMEOUT", "30")),
    )
