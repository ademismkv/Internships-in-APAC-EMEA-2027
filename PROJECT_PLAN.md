# Internships in APAC 2027 — Project Plan

A single public GitHub repo that maintains a broad, community-fed list of
**student internships across APAC** (any 2027 season), rendered as Simplify-style
README tables and kept fresh automatically.

This document is the agreed blueprint. No code is written until it's approved.

---

## 1. Locked decisions

| Area | Decision |
| --- | --- |
| Repo | One **public** repo, `Internships-in-APAC-2027`, personal account |
| Audience | Students / internships **only** (no new-grad) |
| Season | Any **2027** season — winter, spring, summer, fall |
| Region | **All APAC** — East, Southeast, South Asia + Oceania |
| Coverage goal | **Maximally broad**, not limited to big ATS platforms |
| Categories | Software Engineering · Quant · Data Science/AI/ML · Hardware · Product Management |
| Sources | ATS adapters **+** crowdsourced role+link submissions |
| Dedup | Keep every distinct posting, keyed on source job ID |
| Active/closed | Live page = active. Close only on (a) dead link × 2 runs, or (b) explicit previous-year mention (immediate) |
| Undated roles | Kept indefinitely; close only when their link dies |
| Age column | Yes (`0d` / `5d` / `2mo`) from `first_seen` |
| Archiving | Closed roles move to `README-Inactive.md`, never deleted |
| Liveness | Every link (ATS + crowdsourced) pinged on a schedule |
| Scraping ethics | Public JSON endpoints only, rate-limited, retries, no login-walled / ToS-forbidden sources |
| Automation | GitHub Actions cron → fetch + liveness → regenerate READMEs → commit |
| Presentation | Simplify-style tables, no website, no attribution, no sponsorship flags |
| Maintainer | You, actively |

---

## 2. The core idea (why this is tractable)

"Every bit of APAC" sounds like scraping thousands of sites. It isn't, because
coverage splits into two engines:

1. **Automated** — most large employers (incl. every US firm's APAC office) run
   hiring on a *handful* of Applicant Tracking Systems that expose public JSON.
   One adapter per ATS unlocks hundreds of companies. This is the backbone.
2. **Crowdsourced** — the long tail that no adapter reaches (native Asian portals,
   university-only postings, WeChat/PR announcements) comes in as human-submitted
   role+link via GitHub issues, then persists in our own data.

The list = automated backbone + crowdsourced tail, merged into one state file and
rendered.

---

## 3. Repository layout

```
Internships-in-APAC-2027/
├── README.md                     # generated — active roles, by category
├── README-Inactive.md            # generated — closed/archived roles
├── PROJECT_PLAN.md               # this document
├── CONTRIBUTING.md               # how to submit a role
│
├── data/
│   ├── registry.json             # companies we auto-fetch  {company, ats, token, ...}
│   ├── crowdsourced.json         # ingested manual submissions {company, title, url, ...}
│   └── listings.json             # THE STATE — every role ever seen + status/age
│
├── src/
│   ├── main.py                   # orchestrator: fetch → filter → diff → render
│   ├── liveness.py               # ping links, detect dead pages
│   ├── normalize.py              # location aliasing + APAC filter
│   ├── classify.py               # internship? / category / season-year
│   ├── diff.py                   # stateful update: new / seen / missing → active flag
│   ├── render.py                 # state → README markdown
│   ├── ingest.py                 # crowdsourced.json → into the fetch stream
│   └── adapters/
│       ├── base.py               # common schema + HTTP helper (retries, backoff)
│       ├── greenhouse.py
│       ├── lever.py
│       ├── ashby.py
│       ├── workday.py
│       └── smartrecruiters.py
│
├── .github/
│   ├── workflows/
│   │   └── update.yml            # cron: run pipeline, commit regenerated READMEs
│   └── ISSUE_TEMPLATE/
│       └── new_role.yml          # structured role submission form
│
├── tests/                        # unit tests for normalize / classify / diff / render
├── requirements.txt
└── pyproject.toml
```

Everything a human edits is in `data/` (registry + ingested submissions). Both
README files are build artifacts — never hand-edited.

---

## 4. Data schemas

### 4.1 `registry.json` — what we auto-fetch
```json
[
  { "company": "Optiver",  "ats": "greenhouse",     "token": "optiver" },
  { "company": "Palantir", "ats": "lever",          "token": "palantir" },
  { "company": "Pylon",    "ats": "ashby",          "token": "pylon-labs" },
  { "company": "Capital One", "ats": "workday",
    "tenant": "capitalone", "dc": "wd12", "site": "Capital_One" },
  { "company": "Western Digital", "ats": "smartrecruiters", "token": "WesternDigital" }
]
```

### 4.2 `crowdsourced.json` — ingested manual submissions
```json
[
  { "company": "Tencent", "title": "Software Engineer Intern",
    "location": "Shenzhen", "url": "https://careers.tencent.com/...",
    "category": "Software Engineering", "source": "crowdsourced" }
]
```

### 4.3 `listings.json` — the persistent state (the important one)
```json
{
  "greenhouse:optiver:7985973002": {
    "company": "Optiver",
    "title": "Software Developer Internship 2026-27",
    "location": "Hong Kong, Singapore",
    "url": "https://...",
    "category": "Software Engineering",
    "source": "greenhouse",
    "first_seen": "2026-08-12",
    "last_seen":  "2026-08-12",
    "active": true,
    "misses": 0,
    "close_reason": null
  }
}
```
`misses` = consecutive runs the role was absent/dead. `close_reason` ∈
`{null, "link_dead", "stale_year"}`.

---

## 5. The pipeline (one run)

```
                    ┌──────────────────────────────┐
                    │ 1. LOAD                       │
                    │  registry.json                │
                    │  crowdsourced.json            │
                    │  listings.json (prev state)   │
                    └──────────────┬───────────────┘
                                   ▼
        ┌──────────────────────────────────────────────┐
        │ 2. FETCH (per registry entry, via adapter)    │
        │    + inject crowdsourced entries              │
        │    → raw roles [{company,title,location,url}] │
        └──────────────┬───────────────────────────────┘
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 3. FILTER  (three gates, in order)            │
        │    a. is_internship(title)?                   │
        │    b. is_apac(location)?                       │
        │    c. season ok? (2027 or undated; drop only  │
        │       if title names a *different* year)      │
        └──────────────┬───────────────────────────────┘
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 4. CLASSIFY → SWE / Quant / Data-ML / HW / PM │
        └──────────────┬───────────────────────────────┘
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 5. DIFF against previous state                │
        │   new key        → add, first_seen=today      │
        │   seen again     → last_seen=today, misses=0  │
        │   missing/dead   → misses+=1                   │
        │   stale-year     → active=false immediately   │
        │   misses >= 2    → active=false (link_dead)   │
        └──────────────┬───────────────────────────────┘
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 6. LIVENESS (safety net)                      │
        │   ping each active link; dead → misses+=1     │
        │   (catches roles that linger in an API but    │
        │    whose apply page is gone)                  │
        └──────────────┬───────────────────────────────┘
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 7. RENDER                                     │
        │   active   → README.md  (by category)         │
        │   inactive → README-Inactive.md               │
        │   write listings.json                         │
        └──────────────┬───────────────────────────────┘
                       ▼
        ┌──────────────────────────────────────────────┐
        │ 8. COMMIT  (GitHub Actions)                    │
        │   git commit README*.md data/listings.json    │
        └──────────────────────────────────────────────┘
```

### Active / closed logic (your rule, precisely)
- A role is **active** while its page is live.
- Close triggers:
  - **stale_year** — title/text explicitly names a *previous* year (2025/2026) →
    close **immediately** (hard evidence).
  - **link_dead** — link 404s / redirects to a dead/"filled" page for **2
    consecutive runs** → close (2-run buffer avoids false closes from API blips).
- **Undated** roles never self-close; only a dead link takes them down.

---

## 6. Crowdsource flow

```
Contributor opens "New role" issue (structured form: company, title, location,
URL, category)
        │
        ▼
You review. If good, add the entry to data/crowdsourced.json (a quick copy-paste,
or later a small script that reads the issue and appends).
        │
        ▼
Next pipeline run ingests it exactly like an ATS role: it gets filtered,
classified, age-tracked, liveness-checked, and rendered — and persists in
listings.json so it's "in our memory."
```
v1 is **manual approval** (you paste approved submissions into
`crowdsourced.json`). A future nicety: an Action that parses the issue and opens
a PR automatically — explicitly out of scope for v1.

---

## 7. Coverage strategy (how "all APAC" actually gets filled)

| Tier | Source | Coverage | Effort |
| --- | --- | --- | --- |
| 1 | Greenhouse / Lever / Ashby / Workday / SmartRecruiters | US firms' APAC offices + quant + many startups | Low — 5 adapters, grow the registry |
| 2 | Regional platforms with clean feeds (later) | Wanted (KR), Wantedly (JP), Prosple/GradConnection (SG/HK) | Medium — added post-v1 |
| 3 | Native megacap portals (later) | Tencent, ByteDance, Samsung, Rakuten | High/brittle — reverse-engineered feeds, only if worth it |
| 4 | **Crowdsource** | Everything the above miss | Human — the catch-all |

v1 ships Tier 1 + Tier 4. Tiers 2–3 are explicitly deferred so v1 is accurate and
shippable rather than broad-but-broken.

---

## 8. Scheduling & ethics
- **Cadence:** daily cron (plenty for internships; far less noise/rate-risk than
  hourly). Adjustable.
- **Politeness:** per-host rate limiting, exponential backoff, realistic
  User-Agent, public JSON endpoints only. No login-walled sources, nothing a
  site's terms clearly forbid.
- **Failure handling:** a company that 404s or errors is skipped for that run and
  logged to the Action output — never silently corrupts the list, never crashes
  the run.

---

## 9. Build order (milestones)

**M1 — Skeleton that renders.** Schemas + a tiny seed `registry.json` + `render.py`
+ a hand-made `listings.json`. Output: a real README from fake data. *Proves the
look.*

**M2 — Adapters + filter + classify.** All five adapters (correct to each ATS's
real JSON), `normalize.py`, `classify.py`. Run locally against a few real boards.
*Proves we can pull real APAC roles.*

**M3 — Stateful diff + age + auto-close.** `diff.py` implementing your active/close
rules + `first_seen` age. *Proves freshness/closing works across runs.*

**M4 — Liveness checker.** `liveness.py` pinging links. *Proves dead links close.*

**M5 — Crowdsource ingest.** `ingest.py` + issue template + `CONTRIBUTING.md`.
*Proves the tail path works.*

**M6 — Automation.** `update.yml` cron that runs it all and commits. Seed the
registry with a real starter set of APAC-present companies. *Ship.*

**M7 — Grow.** Expand the registry, tune location aliases, add Tier-2 sources if
you want more reach.

Each milestone is independently testable and leaves the repo in a working state.

---

## 10. Known risks / honest caveats
- **Sandbox limitation (build-time only):** the environment I build in can't reach
  ATS APIs, so adapter HTTP calls are validated against known response shapes and
  tested with mock data; first *live* fetch happens on your GitHub Actions.
- **Registry tokens drift:** boards change slugs; a 404 means "fix the token," not
  "code is broken." Failures are logged, not fatal.
- **Location mess:** APAC location strings are inconsistent; the alias table will
  need occasional additions as new formats appear.
- **Maintenance is the real cost:** the code runs itself, but registry curation
  and crowdsource review are ongoing human work. You've accepted this.
- **Tier 3 giants absent in v1:** Tencent/Samsung/etc. arrive via crowdsource
  until/unless dedicated feeds are built.
```
