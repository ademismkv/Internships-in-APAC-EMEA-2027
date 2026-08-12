"""Workday adapter (POST, paginated, per-tenant).

Read tenant/dc/site out of the careers URL:
    https://{tenant}.{dc}.myworkdayjobs.com/{site}
    e.g. capitalone.wd12.myworkdayjobs.com/Capital_One
         -> tenant="capitalone", dc="wd12", site="Capital_One"

    POST https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
    body: {"appliedFacets":{}, "limit":20, "offset":N, "searchText":""}
Response: {"total", "jobPostings":[{"title","externalPath","locationsText"}]}
Apply URL = https://{tenant}.{dc}.myworkdayjobs.com/{site}{externalPath}
"""
from __future__ import annotations
from . import base

SOURCE = "workday"
PAGE = 20


def fetch(company, token="", *, tenant, dc, site, **_ignored):
    api = f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    base_site = f"https://{tenant}.{dc}.myworkdayjobs.com/{site}"
    out, offset = [], 0
    while True:
        body = {"appliedFacets": {}, "limit": PAGE, "offset": offset, "searchText": ""}
        data = base.post_json(api, json=body)
        postings = data.get("jobPostings", [])
        for job in postings:
            path = job.get("externalPath", "")
            out.append(base.record(
                company=company, title=job.get("title", ""),
                location=job.get("locationsText", ""),
                url=base_site + path if path else base_site,
                source=SOURCE, ext_id=path or job.get("title", ""),
            ))
        offset += PAGE
        if offset >= data.get("total", 0) or not postings:
            break
    return out
