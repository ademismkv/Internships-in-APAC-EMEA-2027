"""End-to-end logic tests using mock ATS records (no network).

Proves: internship filter, APAC filter, category routing, season handling,
the stateful age/close rules across multiple runs, and rendering.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import classify, normalize, diff, render  # noqa: E402


def test_internship_filter():
    assert classify.is_internship("Software Engineer Intern")
    assert classify.is_internship("2027 Summer Analyst")
    assert classify.is_internship("软件开发实习生")           # CN intern
    assert classify.is_internship("소프트웨어 엔지니어 인턴")   # KR intern
    assert not classify.is_internship("Senior Software Engineer")
    assert not classify.is_internship("Internal Audit Manager")      # trap
    assert not classify.is_internship("International Sales Lead")     # trap


def test_apac_filter():
    assert normalize.is_apac("Hong Kong")
    assert normalize.is_apac("Central, Hong Kong SAR")
    assert normalize.is_apac("Singapore (SG)")
    assert normalize.is_apac("東京")                    # Tokyo in JP
    assert normalize.is_apac("Bangalore, India")
    assert not normalize.is_apac("New York, NY")
    assert not normalize.is_apac("London, UK")
    assert not normalize.is_apac("")


def test_category_routing():
    assert classify.category("Quant Trading Intern") == "Quantitative Finance"
    assert classify.category("Machine Learning Intern") == "Data Science, AI & ML"
    assert classify.category("FPGA Hardware Intern") == "Hardware Engineering"
    assert classify.category("Product Manager Intern") == "Product Management"
    assert classify.category("Backend Software Intern") == "Software Engineering"


def test_season_rules():
    assert classify.season_ok("Software Intern 2027")
    assert classify.season_ok("Software Intern")           # undated -> keep
    assert not classify.season_ok("Software Intern 2026")  # old -> drop
    assert classify.is_stale_year("Summer 2025 Intern")
    assert not classify.is_stale_year("Summer Intern")


def _rec(company, title, location, url, source="greenhouse", token="t", ext="1"):
    return {"company": company, "title": title, "location": location, "url": url,
            "source": source, "token": token, "ext_id": ext,
            "category": classify.category(title)}


def test_stateful_age_and_close():
    state = {}

    # --- Run 1 (day 1): two roles appear ---
    run1 = [
        _rec("Optiver", "Software Intern 2027", "Hong Kong", "https://x/1", ext="1"),
        _rec("Citadel", "Quant Intern", "Singapore", "https://x/2", ext="2"),
    ]
    state = diff.update_state(state, run1, today="2027-01-01")
    assert len(state) == 2
    assert all(r["active"] for r in state.values())
    assert state["greenhouse:t:1"]["first_seen"] == "2027-01-01"

    # --- Run 2 (day 6): role 1 persists, role 2 vanishes (miss #1) ---
    run2 = [_rec("Optiver", "Software Intern 2027", "Hong Kong", "https://x/1", ext="1")]
    state = diff.update_state(state, run2, today="2027-01-06")
    assert state["greenhouse:t:2"]["misses"] == 1
    assert state["greenhouse:t:2"]["active"] is True      # 1 miss != closed yet

    # --- Run 3 (day 7): role 2 still gone (miss #2) -> closes link_dead ---
    state = diff.update_state(state, run2, today="2027-01-07")
    assert state["greenhouse:t:2"]["active"] is False
    assert state["greenhouse:t:2"]["close_reason"] == "link_dead"

    # role 1 age reflects first_seen, not last_seen
    from datetime import date
    md = render.render_active(state, today=date(2027, 1, 7))
    assert "6d" in md            # optiver listed 6 days
    assert "Optiver" in md
    assert "Citadel" not in md   # closed -> not in active README

    # closed role shows up in inactive README
    mi = render.render_inactive(state, today=date(2027, 1, 7))
    assert "Citadel" in mi and "link dead" in mi


def test_stale_year_closes_immediately():
    state = {}
    run = [_rec("BigCo", "Summer 2026 Intern", "Tokyo", "https://x/9", ext="9")]
    state = diff.update_state(state, run, today="2027-02-01")
    assert state["greenhouse:t:9"]["active"] is False
    assert state["greenhouse:t:9"]["close_reason"] == "stale_year"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")
