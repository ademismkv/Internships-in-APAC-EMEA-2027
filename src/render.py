"""Render state -> README.md (active) and README-Inactive.md (closed)."""
from __future__ import annotations
from datetime import date, datetime, timezone

CATEGORY_ORDER = [
    ("Software Engineering", "💻"),
    ("Quantitative Finance", "📈"),
    ("Data Science, AI & ML", "🤖"),
    ("Hardware Engineering", "🔧"),
    ("Product Management", "📱"),
]


def _age(first_seen: str, today: date) -> str:
    try:
        first = date.fromisoformat(first_seen)
    except ValueError:
        return "?"
    days = (today - first).days
    if days <= 0:
        return "🆕"
    if days < 30:
        return f"{days}d"
    if days < 365:
        return f"{days // 30}mo"
    return f"{days // 365}y"


def _anchor(name: str) -> str:
    return name.lower().replace(" ", "-").replace(",", "").replace("&", "")


def _row(r: dict, today: date) -> str:
    title = r["title"].replace("|", "\\|")
    loc = r["location"].replace("|", "\\|")
    apply_cell = f"[Apply]({r['url']})" if r.get("url") else "—"
    return (f"| **{r['company']}** | {title} | {loc} | {apply_cell} "
            f"| {_age(r['first_seen'], today)} |")


def render_active(state: dict, *, today: date | None = None) -> str:
    today = today or datetime.now(timezone.utc).date()
    active = [r for r in state.values() if r.get("active", True)]
    counts = {}
    for r in active:
        counts[r["category"]] = counts.get(r["category"], 0) + 1

    L = ["# Internships in APAC 2027 🌏", ""]
    L.append("A community-maintained list of **student internships across the "
             "Asia-Pacific region** — software, quant, data/ML, hardware, and "
             "product roles for any 2027 season. Covers Hong Kong, Singapore, "
             "Tokyo, Seoul, Shanghai, Taipei, India, SE Asia and Oceania.")
    L.append("")
    L.append(f"**{len(active)} active roles** · updated automatically · "
             "contribute via [issue](../../issues/new/choose)")
    L.append("")
    idx = []
    for name, emoji in CATEGORY_ORDER:
        idx.append(f"{emoji} [{name}](#{_anchor(name)}) ({counts.get(name, 0)})")
    L.append(" · ".join(idx))
    L.append("")
    L.append("> 🆕 posted today · `Nd` = days listed · 🔒 closed roles live in "
             "[README-Inactive.md](README-Inactive.md)")
    L.append("")
    L.append("---")
    L.append("")
    for name, emoji in CATEGORY_ORDER:
        rows = [r for r in active if r["category"] == name]
        if not rows:
            continue
        rows.sort(key=lambda r: (r["first_seen"], r["company"]), reverse=True)
        L.append(f"## {emoji} {name}")
        L.append("")
        L.append("| Company | Role | Location | Application | Age |")
        L.append("| --- | --- | --- | --- | --- |")
        L += [_row(r, today) for r in rows]
        L.append("")
    L.append("---")
    L.append("")
    L.append("_Generated automatically. Do not edit by hand — edit "
             "`data/registry.json` / `data/crowdsourced.json` and let the updater "
             "regenerate this file._")
    L.append("")
    return "\n".join(L)


def render_inactive(state: dict, *, today: date | None = None) -> str:
    today = today or datetime.now(timezone.utc).date()
    closed = [r for r in state.values() if not r.get("active", True)]
    L = ["# Closed / Archived Roles 🔒", ""]
    L.append(f"Roles no longer active ({len(closed)}). Kept for reference; never "
             "deleted.")
    L.append("")
    if not closed:
        L.append("_None yet._")
        L.append("")
        return "\n".join(L)
    closed.sort(key=lambda r: r.get("last_seen", ""), reverse=True)
    L.append("| Company | Role | Location | Link | Closed because | Last seen |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    reason_label = {"link_dead": "link dead", "stale_year": "previous year"}
    for r in closed:
        title = r["title"].replace("|", "\\|")
        loc = r["location"].replace("|", "\\|")
        link = f"[link]({r['url']})" if r.get("url") else "—"
        reason = reason_label.get(r.get("close_reason"), r.get("close_reason") or "—")
        L.append(f"| **{r['company']}** | {title} | {loc} | {link} | {reason} "
                 f"| {r.get('last_seen', '?')} |")
    L.append("")
    return "\n".join(L)
