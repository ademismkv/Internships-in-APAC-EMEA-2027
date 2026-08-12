"""ByteDance / TikTok adapter (Tier-2 custom).

ByteDance, TikTok, Lark etc. run on the same in-house "talent" platform, which
exposes a public search API. Unlike an ATS token, this needs a POST with a JSON
body and (usually) a cookie primed by first hitting the site. Because the header
requirements can shift and this can't be tested from a no-network sandbox, the
adapter is deliberately configurable and fails soft: any error is raised as
FetchError, which the orchestrator logs and skips without crashing the run.

Registry entry:
    { "company": "ByteDance", "ats": "bytedance",
      "api_host": "https://jobs.bytedance.com",
      "web_host": "https://jobs.bytedance.com/en",
      "portal_type": 6, "keyword": "intern" }

  portal_type 6 = campus/intern portal, 2 = experienced. web_host is where the
  human-facing /position/{id}/detail page lives (…/en for English).

API (best-known public shape):
    POST {api_host}/api/v1/search/job/posts
    body: {"keyword","limit","offset","portal_type", ...id_list fields[]}
    resp: {"code":0,"data":{"count":N,"job_post_list":[
             {"id","title","city_info":{"name"} | "city_list":[{"name"}]}]}}
"""
from __future__ import annotations

import requests

from . import base

SOURCE = "bytedance"
PAGE = 50


def _empty_lists() -> dict:
    return {k: [] for k in (
        "job_category_id_list", "tag_id_list", "location_code_list",
        "subject_id_list", "recruitment_id_list", "job_function_id_list",
        "storefront_id_list",
    )}


def fetch(company: str, token: str = "", *,
          api_host: str = "https://jobs.bytedance.com",
          web_host: str = "https://jobs.bytedance.com/en",
          portal_type: int = 6, keyword: str = "intern", **_ignored) -> list[dict]:
    api = f"{api_host.rstrip('/')}/api/v1/search/job/posts"
    session = requests.Session()
    session.headers.update({**base.HEADERS, "content-type": "application/json"})
    # Prime cookies (some deployments 400 the API without a prior page hit).
    try:
        session.get(api_host, timeout=base.TIMEOUT)
    except requests.RequestException:
        pass

    out: list[dict] = []
    offset = 0
    while True:
        body = {"keyword": keyword, "limit": PAGE, "offset": offset,
                "portal_type": portal_type, "portal_entrance": 1, **_empty_lists()}
        try:
            resp = session.post(api, json=body, timeout=base.TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as exc:
            raise base.FetchError(f"bytedance POST failed: {api} :: {exc}")

        data = payload.get("data") or {}
        posts = data.get("job_post_list") or []
        for job in posts:
            loc = ""
            if job.get("city_info"):
                loc = job["city_info"].get("name", "")
            elif job.get("city_list"):
                loc = ", ".join(c.get("name", "") for c in job["city_list"])
            jid = job.get("id", "")
            out.append(base.record(
                company=company, title=job.get("title", ""), location=loc,
                url=f"{web_host.rstrip('/')}/position/{jid}/detail",
                source=SOURCE, ext_id=jid,
            ))

        offset += PAGE
        total = data.get("count", 0)
        if offset >= total or not posts:
            break
    return out
