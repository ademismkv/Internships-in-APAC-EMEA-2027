"""Ashby adapter.

    GET https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=false

Response: {"jobs":[{"id","title","location","secondaryLocations":[{"location"}],
                    "applyUrl"|"jobUrl"}]}
Token = org slug in apply URLs, e.g. jobs.ashbyhq.com/pylon-labs -> "pylon-labs".
"""
from __future__ import annotations
from . import base

SOURCE = "ashby"


def fetch(company: str, token: str, **_ignored) -> list[dict]:
    url = (f"https://api.ashbyhq.com/posting-api/job-board/{token}"
           "?includeCompensation=false")
    data = base.get_json(url)
    out: list[dict] = []
    for job in data.get("jobs", []):
        locs = [job.get("location", "")]
        for sec in job.get("secondaryLocations", []) or []:
            if sec.get("location"):
                locs.append(sec["location"])
        loc = ", ".join(dict.fromkeys(filter(None, locs)))
        out.append(base.record(
            company=company, title=job.get("title", ""), location=loc,
            url=job.get("applyUrl") or job.get("jobUrl", ""),
            source=SOURCE, ext_id=job.get("id", ""),
        ))
    return out
