from __future__ import annotations

import base64
import json
from urllib.request import Request, urlopen

from config import TestConfig


def video_url(config: TestConfig, session_id: str) -> str:
    """Same as Java helpers.Browserstack.videoUrl — env creds, not hardcoded."""
    url = f"https://api.browserstack.com/app-automate/sessions/{session_id}.json"
    token = f"{config.browserstack_user}:{config.browserstack_key}".encode("ascii")
    req = Request(url)
    req.add_header("Authorization", "Basic " + base64.b64encode(token).decode("ascii"))
    with urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["automation_session"]["video_url"]
