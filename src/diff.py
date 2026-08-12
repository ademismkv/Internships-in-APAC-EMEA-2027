"""Stateful diff: fold this run's roles into the persistent state.

This is the only stateful step. It owns first_seen (age), the misses counter, the
active flag, and close_reason. Rules (exactly as agreed):

  * Live page = active.
  * Close triggers:
      - stale_year: title names a *previous* year -> close immediately.
      - link_dead:  role absent/dead for CLOSE_AFTER consecutive runs -> close.
  * Undated roles never self-close; only a dead link takes them down.

Key = "{source}:{token-or-company}:{ext_id}" -> keeps every distinct posting.
"""
from __future__ import annotations
from datetime import date

from . import classify

CLOSE_AFTER = 2  # consecutive misses before we flag link_dead


def make_key(rec: dict) -> str:
    ident = rec.get("token") or rec.get("company", "")
    return f"{rec['source']}:{ident}:{rec['ext_id']}"


def update_state(state: dict, seen: list[dict], *, today: str | None = None,
                 target_year: str = "2027") -> dict:
    """Return the new state dict. `seen` = this run's filtered+classified roles."""
    today = today or date.today().isoformat()
    seen_keys = set()

    # 1. Roles present this run: add new / refresh existing.
    for rec in seen:
        key = make_key(rec)
        seen_keys.add(key)
        stale = classify.is_stale_year(rec["title"], target_year)
        if key in state:
            row = state[key]
            row["last_seen"] = today
            row["misses"] = 0
            # Refresh mutable display fields in case the posting changed.
            row["title"] = rec["title"]
            row["location"] = rec["location"]
            row["url"] = rec["url"]
            row["category"] = rec["category"]
            if stale:
                row["active"] = False
                row["close_reason"] = "stale_year"
            elif row.get("close_reason") == "stale_year":
                # Was mis-flagged before; a non-stale sighting revives it.
                row["active"] = True
                row["close_reason"] = None
        else:
            state[key] = {
                "company": rec["company"], "title": rec["title"],
                "location": rec["location"], "url": rec["url"],
                "category": rec["category"], "source": rec["source"],
                "first_seen": today, "last_seen": today,
                "active": not stale,
                "misses": 0,
                "close_reason": "stale_year" if stale else None,
            }

    # 2. Roles in state but absent this run: increment misses, maybe close.
    for key, row in state.items():
        if key in seen_keys:
            continue
        if not row.get("active", True):
            continue
        row["misses"] = row.get("misses", 0) + 1
        if row["misses"] >= CLOSE_AFTER:
            row["active"] = False
            row["close_reason"] = "link_dead"

    return state
