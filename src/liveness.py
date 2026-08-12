"""Liveness checker: ping active links, flag dead ones.

Safety net for roles that linger in an API (or crowdsourced links with no API at
all) but whose apply page is actually gone. A dead ping increments the same
`misses` counter diff.py uses, so a link dead for CLOSE_AFTER consecutive runs
closes with reason link_dead — consistent with the agreed rule.

We're deliberately gentle: HEAD first (cheap), fall back to GET, treat only clear
failure signals as dead. Ambiguous cases are left alone (never false-close).
"""
from __future__ import annotations
import time
import requests

from .adapters.base import HEADERS
from .diff import CLOSE_AFTER

TIMEOUT = 15
DEAD_MARKERS = (
    "position filled", "no longer available", "job not found",
    "posting is closed", "this job is closed", "not currently accepting",
)


def is_dead(url: str) -> bool:
    """True if the URL clearly points at a gone/closed posting."""
    if not url:
        return True
    try:
        r = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code in (404, 410):
            return True
        if r.status_code == 405 or r.status_code >= 500:
            # HEAD not allowed / server hiccup -> confirm with a light GET.
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code in (404, 410):
            return True
        if r.status_code == 200:
            body = (r.text or "").lower()[:20000]
            return any(m in body for m in DEAD_MARKERS)
    except requests.RequestException:
        # Network flake is NOT proof of death; leave it for a future run.
        return False
    return False


def sweep(state: dict, *, only_active: bool = True, pause: float = 0.3) -> dict:
    """Ping active links; bump misses / close as needed."""
    for row in state.values():
        if only_active and not row.get("active", True):
            continue
        if is_dead(row["url"]):
            row["misses"] = row.get("misses", 0) + 1
            if row["misses"] >= CLOSE_AFTER:
                row["active"] = False
                row["close_reason"] = "link_dead"
        time.sleep(pause)  # politeness between hosts
    return state
