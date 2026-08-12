"""Greenhouse adapter.

    GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=false

Response: {"jobs": [{"id","title","absolute_url","location":{"name"},"offices":[...]}]}
Token = board slug in apply URLs, e.g. job-boards.greenhouse.io/optiver -> "optiver".
"""
from __future__ import annotations
from . import base

SOURCE = "greenhouse"


def fetch(company: str, token: str, **_ignored) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=false"
    data = base.get_json(url)
    out: list[dict] = []
    for job in data.get("jobs", []):
        loc = (job.get("location") or {}).get("name", "")
        if not loc and job.get("offices"):
            loc = ", ".join(o.get("name", "") for o in job["offices"] if o.get("name"))
        out.append(base.record(
            company=company, title=job.get("title", ""), location=loc,
            url=job.get("absolute_url", ""), source=SOURCE, ext_id=job.get("id", ""),
        ))
    return out
