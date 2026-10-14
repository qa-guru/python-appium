from __future__ import annotations

import requests

from config import TestConfig

_SESSION_API = "https://api.browserstack.com/app-automate/sessions/{}.json"


def _auth(config: TestConfig) -> tuple[str, str]:
    return config.browserstack_user, config.browserstack_key


def session(config: TestConfig, session_id: str) -> dict:
    """Same as Java helpers.Browserstack.videoUrl — env creds, not hardcoded."""
    resp = requests.get(
        _SESSION_API.format(session_id), auth=_auth(config), timeout=30
    )
    resp.raise_for_status()
    return resp.json()["automation_session"]


def download(config: TestConfig, url: str) -> bytes:
    """Artifact urls are usually pre-signed; fall back to basic auth on 401/403."""
    resp = requests.get(url, timeout=60)
    if resp.status_code in (401, 403):
        resp = requests.get(url, auth=_auth(config), timeout=60)
    resp.raise_for_status()
    return resp.content


def video_url(config: TestConfig, session_id: str) -> str:
    return session(config, session_id)["video_url"]
