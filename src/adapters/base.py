"""Base adapter contract: common schema + resilient HTTP helpers.

Every ATS adapter turns one company's public job-board API response into a list
of records with a *common* schema, so downstream code never needs to know which
ATS a role came from.

Common record:
    {"company", "title", "location", "url", "source", "ext_id"}
"""

from __future__ import annotations

import time
from typing import Any

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
TIMEOUT = 20


class FetchError(Exception):
    """Raised when an adapter cannot retrieve or parse a board."""


def get_json(url: str, *, retries: int = 3, backoff: float = 1.5, **kwargs) -> Any:
    return _request_json("GET", url, retries=retries, backoff=backoff, **kwargs)


def post_json(url: str, *, retries: int = 3, backoff: float = 1.5, **kwargs) -> Any:
    return _request_json("POST", url, retries=retries, backoff=backoff, **kwargs)


def _request_json(method: str, url: str, *, retries: int, backoff: float, **kwargs):
    headers = {**HEADERS, **kwargs.pop("headers", {})}
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.request(method, url, headers=headers, timeout=TIMEOUT, **kwargs)
            if resp.status_code == 404:
                # Bad registry token, almost always. Don't retry; surface clearly.
                raise FetchError(f"404 Not Found: {url} (check the registry token)")
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(backoff ** (attempt + 1))
    raise FetchError(f"{method} failed after {retries} tries: {url} :: {last}")


def record(*, company, title, location, url, source, ext_id) -> dict:
    return {
        "company": company,
        "title": (title or "").strip(),
        "location": (location or "").strip(),
        "url": url,
        "source": source,
        "ext_id": str(ext_id),
    }
