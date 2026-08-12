"""Orchestrator: load -> fetch -> filter -> classify -> diff -> liveness -> render.

Run from the repo root:  python -m src.main
Env/flags:
    --no-liveness   skip the link-ping sweep (faster local runs)
    --no-fetch      skip ATS fetches, use only crowdsourced.json (offline test)
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from . import adapters, classify, diff, ingest, liveness, normalize, render, sources
from .adapters.base import FetchError

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REGISTRY = DATA / "registry.json"
CROWD = DATA / "crowdsourced.json"
WATCHLIST = DATA / "watchlist.json"
SOURCES = DATA / "sources.json"
STATE = DATA / "listings.json"
TARGET_YEAR = "2027"


def _load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_all(registry: list[dict]) -> tuple[list[dict], list[str]]:
    """Return (raw_records, error_log). Never raises for a single bad board."""
    raw, errors = [], []
    for entry in registry:
        ats = entry.get("ats")
        try:
            fn = adapters.get(ats)
            cfg = {k: v for k, v in entry.items()
                   if k not in ("company", "ats", "token", "verified")}
            got = fn(entry["company"], entry.get("token", ""), **cfg)
            # remember token for a stable dedup key
            for r in got:
                r["token"] = entry.get("token") or entry.get("tenant", "")
            raw.extend(got)
            print(f"  [{ats:15}] {entry['company']:24} -> {len(got):4} roles")
        except (FetchError, KeyError) as exc:
            errors.append(f"{entry.get('company','?')} ({ats}): {exc}")
            print(f"  [{ats:15}] {entry['company']:24} -> SKIP: {exc}",
                  file=sys.stderr)
    return raw, errors


def pipeline(*, do_fetch=True, do_liveness=True, today: str | None = None) -> dict:
    today = today or date.today().isoformat()
    registry = _load_json(REGISTRY, [])
    crowd = _load_json(CROWD, [])
    state = _load_json(STATE, {})

    print("Fetching ATS boards..." if do_fetch else "Skipping ATS fetch.")
    raw = []
    errors = []
    if do_fetch:
        raw, errors = fetch_all(registry)

    # Aggregate upstream community lists (the main volume driver).
    src_directory = []
    if do_fetch:
        src_roles, src_directory, src_errors = sources.load_all(_load_json(SOURCES, []))
        raw += src_roles
        errors += src_errors

    raw += ingest.load(crowd)
    print(f"Raw roles gathered: {len(raw)}")

    # Filter + classify (EMEA + APAC).
    kept = []
    for r in raw:
        if not classify.is_internship(r["title"]):
            continue
        if not normalize.is_target(r["location"]):
            continue
        if not classify.season_ok(r["title"], TARGET_YEAR):
            continue
        r["location"] = normalize.display_location(r["location"])
        hint = r.get("_category_hint")
        r["category"] = hint if hint else classify.category(r["title"])
        kept.append(r)
    print(f"After filter (intern + EMEA/APAC + season): {len(kept)}")

    # Cross-source dedup: the same posting can appear in several lists. Collapse
    # on the normalized apply URL, keeping provenance of every list it came from.
    deduped: dict[str, dict] = {}
    for r in kept:
        key = r.get("ext_id") or r["url"]
        if key in deduped:
            vias = set(filter(None, [deduped[key].get("via"), r.get("via")]))
            deduped[key]["via"] = ", ".join(sorted(vias))
        else:
            deduped[key] = r
    kept = list(deduped.values())
    print(f"After cross-source dedup: {len(kept)}")

    # Stateful diff.
    state = diff.update_state(state, kept, today=today, target_year=TARGET_YEAR)

    # Liveness sweep (safety net).
    if do_liveness:
        print("Liveness sweep...")
        state = liveness.sweep(state)

    # Render + persist. Directory = curated watchlist + China portals from sources.
    today_d = date.fromisoformat(today)
    watchlist = _load_json(WATCHLIST, []) + src_directory
    (ROOT / "README.md").write_text(
        render.render_active(state, today=today_d), encoding="utf-8")
    (ROOT / "README-Inactive.md").write_text(
        render.render_inactive(state, today=today_d), encoding="utf-8")
    (ROOT / "DIRECTORY.md").write_text(
        render.render_directory(watchlist), encoding="utf-8")
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    active = sum(1 for r in state.values() if r.get("active", True))
    print(f"Done. active={active} total={len(state)} errors={len(errors)}")
    if errors:
        print("Errors:")
        for e in errors:
            print("  -", e)
    return state


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-liveness", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--today", default=None, help="override date (YYYY-MM-DD)")
    args = ap.parse_args(argv)
    pipeline(do_fetch=not args.no_fetch, do_liveness=not args.no_liveness,
             today=args.today)


if __name__ == "__main__":
    main()
