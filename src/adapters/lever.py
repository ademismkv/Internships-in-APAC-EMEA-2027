"""Lever adapter.

    GET https://api.lever.co/v0/postings/{token}?mode=json

Response: [{"id","text","categories":{"location","team","commitment"},"hostedUrl"}]
Token = slug in apply URLs, e.g. jobs.lever.co/palantir -> "palantir".
"""
from __future__ import annotations
from . import base

SOURCE = "lever"


def fetch(company: str, token: str, **_ignored) -> list[dict]:
    data = base.get_json(f"https://api.lever.co/v0/postings/{token}?mode=json")
    out: list[dict] = []
    for job in data:
        cats = job.get("categories") or {}
        loc = cats.get("location", "")
        if cats.get("allLocations"):
            loc = ", ".join(cats["allLocations"])
        out.append(base.record(
            company=company, title=job.get("text", ""), location=loc,
            url=job.get("hostedUrl", ""), source=SOURCE, ext_id=job.get("id", ""),
        ))
    return out
