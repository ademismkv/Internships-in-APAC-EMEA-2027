"""SmartRecruiters adapter.

    GET https://api.smartrecruiters.com/v1/companies/{token}/postings?limit=100&offset=N

Response: {"totalFound","content":[{"id","name","location":{"city","country"}}]}
Apply URL = https://jobs.smartrecruiters.com/{token}/{id}
"""
from __future__ import annotations
from . import base

SOURCE = "smartrecruiters"
PAGE = 100


def fetch(company: str, token: str, **_ignored) -> list[dict]:
    out, offset = [], 0
    while True:
        url = (f"https://api.smartrecruiters.com/v1/companies/{token}/postings"
               f"?limit={PAGE}&offset={offset}")
        data = base.get_json(url)
        content = data.get("content", [])
        for job in content:
            loc = job.get("location", {}) or {}
            loc_str = ", ".join(filter(None, [
                loc.get("city", ""), (loc.get("country", "") or "").upper()]))
            out.append(base.record(
                company=company, title=job.get("name", ""), location=loc_str,
                url=f"https://jobs.smartrecruiters.com/{token}/{job.get('id','')}",
                source=SOURCE, ext_id=job.get("id", ""),
            ))
        offset += PAGE
        if offset >= data.get("totalFound", 0) or not content:
            break
    return out
