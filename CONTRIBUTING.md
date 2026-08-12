# Contributing

Two ways to add roles.

## 1. Submit a single role (easiest)
Open a **New role** issue: <../../issues/new/choose>. Fill in company, title,
location, application URL, and category. A maintainer copies approved submissions
into `data/crowdsourced.json`, and the next automated run picks them up — with age
tracking and dead-link detection, same as everything else.

## 2. Add a company to the auto-scraper (best — covers it forever)
If a company hosts jobs on a supported ATS, add one line to `data/registry.json`
and every current and future intern posting is fetched automatically.

Supported ATS + how to find the token (look at the company's apply URL):

| ATS | Apply URL looks like | Registry entry |
| --- | --- | --- |
| Greenhouse | `job-boards.greenhouse.io/optiver` or `...?gh_jid=` | `{ "company": "Optiver", "ats": "greenhouse", "token": "optiver" }` |
| Lever | `jobs.lever.co/palantir` | `{ "company": "Palantir", "ats": "lever", "token": "palantir" }` |
| Ashby | `jobs.ashbyhq.com/pylon-labs` | `{ "company": "Pylon", "ats": "ashby", "token": "pylon-labs" }` |
| SmartRecruiters | `jobs.smartrecruiters.com/WesternDigital` | `{ "company": "Western Digital", "ats": "smartrecruiters", "token": "WesternDigital" }` |
| Workday | `capitalone.wd12.myworkdayjobs.com/Capital_One` | `{ "company": "Capital One", "ats": "workday", "tenant": "capitalone", "dc": "wd12", "site": "Capital_One" }` |

> Registry tokens can drift. If a company logs a `404 (check the registry token)`
> during a run, the token is wrong — fix that one line; it never breaks the rest.

## Rules
- **Students/internships only.** No new-grad or full-time roles.
- **APAC only.** East / Southeast / South Asia + Oceania. See `src/normalize.py`
  for recognized cities; add aliases there if a location isn't matched.
- **Don't edit `README.md` / `README-Inactive.md` / `data/listings.json` by hand** —
  they're generated. Edit the registry or crowdsourced file instead.

## Run locally
```bash
pip install -r requirements.txt
python -m src.main                 # full run (fetch + liveness)
python -m src.main --no-liveness   # skip link pinging (faster)
python -m src.main --no-fetch      # crowdsourced only (offline)
python tests/test_pipeline.py      # logic tests, no network
```
