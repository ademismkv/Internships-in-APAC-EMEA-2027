"""Ingest crowdsourced submissions into the fetch stream.

data/crowdsourced.json holds human-approved role+link entries. We turn each into
the same common record shape the adapters emit, so downstream filtering,
classification, age-tracking and liveness treat them identically.
"""
from __future__ import annotations

SOURCE = "crowdsourced"


def load(entries: list[dict]) -> list[dict]:
    out: list[dict] = []
    for e in entries:
        url = e.get("url", "")
        # Stable id: prefer explicit id, else derive from the URL.
        ext_id = e.get("id") or url.rstrip("/").split("/")[-1] or e.get("title", "")
        out.append({
            "company": e.get("company", "").strip(),
            "title": e.get("title", "").strip(),
            "location": e.get("location", "").strip(),
            "url": url,
            "source": SOURCE,
            "ext_id": str(ext_id),
            # optional pre-set category from the submitter; classify can override
            "_category_hint": e.get("category"),
        })
    return out
