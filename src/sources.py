"""Upstream-list aggregator: pull already-maintained community lists and parse
their markdown tables into our common record schema.

This is the smart core: instead of scraping hundreds of company APIs, we ingest
a few high-quality, actively-maintained lists and unify them. Each source has a
parser keyed by `format`. All fetches hit raw.githubusercontent.com.

Record (role feed):   {company, title, location, url, source, ext_id, via}
Directory entry:      {company, region, url, note, via}
"""
from __future__ import annotations

import re
from . import adapters  # noqa: F401  (kept for namespace symmetry)
from .adapters import base

TAG_RE = re.compile(r"<[^>]+>")
HREF_RE = re.compile(r'href="([^"]+)"')
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def _strip(html: str) -> str:
    return TAG_RE.sub("", html or "").strip()


def _cells(line: str) -> list[str]:
    # A markdown table row: split on unescaped pipes, drop the empty edges.
    parts = [c.strip() for c in line.strip().strip("|").split("|")]
    return parts


def fetch_source(src: dict) -> tuple[list[dict], list[dict]]:
    """Return (role_records, directory_entries) for one configured source."""
    fmt = src.get("format")
    raw = _get_text(src["url"])
    if fmt == "speedyapply":
        return _parse_speedyapply(raw, src), []
    if fmt == "campus_cn":
        return [], _parse_campus_cn(raw, src)
    raise base.FetchError(f"unknown source format: {fmt}")


def _get_text(url: str) -> str:
    import requests
    r = requests.get(url, headers=base.HEADERS, timeout=base.TIMEOUT)
    if r.status_code == 404:
        raise base.FetchError(f"404 source not found: {url}")
    r.raise_for_status()
    return r.text


def _parse_speedyapply(md: str, src: dict) -> list[dict]:
    """Rows: | <a><strong>Company</strong></a> | Position | Location | <a href=apply><img></a> | Age |"""
    out: list[dict] = []
    via = src.get("name", "speedyapply")
    for line in md.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 5:
            continue
        company = _strip(cells[0])
        if not company or company.lower() == "company" or company.startswith("---"):
            continue
        position = _strip(cells[1])
        location = _strip(cells[2])
        m = HREF_RE.search(cells[3])
        apply_url = m.group(1) if m else ""
        if not apply_url:
            continue
        out.append({
            "company": company, "title": position, "location": location,
            "url": apply_url, "source": "feed",
            "ext_id": _norm_url(apply_url), "via": via,
        })
    return out


def _parse_campus_cn(md: str, src: dict) -> list[dict]:
    """Rows: | 公司 | [状态](投递链接) | 更新日期 | 地点 | 备注 | -> directory entries."""
    out: list[dict] = []
    via = src.get("name", "Campus2026")
    for line in md.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 5:
            continue
        company = _strip(cells[0])
        if not company or company in ("公司", "Company") or company.startswith("---"):
            continue
        link_m = MD_LINK_RE.search(cells[1])
        if not link_m:
            continue
        status, url = link_m.group(1), link_m.group(2)
        loc = _strip(cells[3]) or "China"
        if loc in ("全国", ""):
            loc = "China (Nationwide)"
        note = _strip(cells[4])
        out.append({
            "company": company, "region": loc, "url": url,
            "note": f"{status}. {note}".strip(". "), "via": via,
        })
    return out


def _norm_url(u: str) -> str:
    u = (u or "").strip()
    u = u.split("#")[0].rstrip("/")
    return u.lower()


def load_all(sources: list[dict]):
    """Run every enabled source. Returns (roles, directory, errors)."""
    roles, directory, errors = [], [], []
    for src in sources:
        if not src.get("enabled", True):
            continue
        try:
            r, d = fetch_source(src)
            roles.extend(r)
            directory.extend(d)
            print(f"  [source] {src.get('name','?'):28} -> {len(r):4} roles, "
                  f"{len(d):4} directory")
        except base.FetchError as exc:
            errors.append(f"{src.get('name','?')}: {exc}")
            print(f"  [source] {src.get('name','?'):28} -> SKIP: {exc}")
    return roles, directory, errors
