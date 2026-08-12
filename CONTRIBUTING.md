# Contributing

There are three data files you can edit. **Never** edit `README.md`,
`README-Inactive.md`, or `DIRECTORY.md` — they're regenerated every run.

## Adding sources (this is the main way to grow the list)

### A. Auto-fetch a company → `data/registry.json`
If a company hosts jobs on a supported system, add one line and **every** current
and future intern posting is pulled automatically, with age tracking and
dead-link detection.

Supported systems and how to find the token (look at the company's apply URL):

| System | Apply URL looks like | Registry entry |
| --- | --- | --- |
| Greenhouse | `job-boards.greenhouse.io/optiver` or `…?gh_jid=` | `{ "company": "Optiver", "ats": "greenhouse", "token": "optiver" }` |
| Lever | `jobs.lever.co/palantir` | `{ "company": "Palantir", "ats": "lever", "token": "palantir" }` |
| Ashby | `jobs.ashbyhq.com/pylon-labs` | `{ "company": "Pylon", "ats": "ashby", "token": "pylon-labs" }` |
| SmartRecruiters | `jobs.smartrecruiters.com/WesternDigital` | `{ "company": "Western Digital", "ats": "smartrecruiters", "token": "WesternDigital" }` |
| Workday | `capitalone.wd12.myworkdayjobs.com/Capital_One` | `{ "company": "Capital One", "ats": "workday", "tenant": "capitalone", "dc": "wd12", "site": "Capital_One" }` |
| ByteDance/TikTok | `jobs.bytedance.com` / `careers.tiktok.com` | `{ "company": "TikTok", "ats": "bytedance", "api_host": "https://careers.tiktok.com", "web_host": "https://careers.tiktok.com", "portal_type": 6, "keyword": "intern" }` |

Add `"verified": false` if you're guessing the token. A wrong token just logs
`404 (check the registry token)` and is skipped — it never breaks the run. Once
you confirm a role appears, flip it to `true`.

### B. Directory-only (bespoke portal we can't parse) → `data/watchlist.json`
For native Asian giants and other sites without a parseable API, add a
browse-here link. It renders into `DIRECTORY.md` and gets liveness-checked.

```json
{ "company": "Kakao", "region": "Seoul", "url": "https://careers.kakao.com/", "note": "" }
```

### C. Submit one specific role → GitHub issue
Open a **New role** issue: <../../issues/new/choose>. A maintainer pastes approved
submissions into `data/crowdsourced.json`:

```json
{ "id": "unique-slug", "company": "Tencent", "title": "Software Engineer Intern",
  "location": "Shenzhen", "url": "https://…", "category": "Software Engineering" }
```
Give each entry a unique `id` so two roles that share a landing-page URL don't
collide.


### D. Add an upstream list to aggregate -> `data/sources.json`
The main volume comes from aggregating other maintained community lists. To add
one, append an entry with a `format` parser (`speedyapply` for that table style,
`campus_cn` for the Chinese portal style) and its raw markdown URL:

```json
{ "name": "speedyapply-SWE-2027", "format": "speedyapply",
  "url": "https://raw.githubusercontent.com/speedyapply/2027-SWE-College-Jobs/main/INTERN_INTL.md",
  "enabled": true }
```
New table formats need a small parser in `src/sources.py`.

## Bulk-editing the registry / directory
`data/registry.json` and `data/watchlist.json` are also generated from
`scripts/build_data.py`. For large additions, edit that script and run
`python scripts/build_data.py` — it's easier to manage hundreds of entries in
Python than raw JSON.

## Rules
- **Students/internships only.** No new-grad or full-time roles.
- **EMEA or APAC only.** East / Southeast / South Asia + Oceania. Add unrecognized cities
  to the alias table in `src/normalize.py`.
- **Any 2027 season.** Undated roles are kept; roles naming only a previous year
  (e.g. "Summer 2026") are auto-closed.

## Run locally
```bash
pip install -r requirements.txt
python -m src.main                 # full run (fetch + liveness)
python -m src.main --no-liveness   # skip link pinging (faster)
python -m src.main --no-fetch      # crowdsourced + directory only (offline)
python tests/test_pipeline.py      # logic tests, no network
python scripts/build_data.py       # regenerate registry.json + watchlist.json
```
