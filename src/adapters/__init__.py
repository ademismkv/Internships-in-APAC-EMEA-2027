"""Adapter registry: ATS name -> fetch(company, token, **cfg)."""
from . import ashby, bytedance, greenhouse, lever, smartrecruiters, workday

ADAPTERS = {
    greenhouse.SOURCE: greenhouse.fetch,
    lever.SOURCE: lever.fetch,
    ashby.SOURCE: ashby.fetch,
    workday.SOURCE: workday.fetch,
    smartrecruiters.SOURCE: smartrecruiters.fetch,
    bytedance.SOURCE: bytedance.fetch,
}


def get(ats: str):
    if ats not in ADAPTERS:
        raise KeyError(f"No adapter for ATS '{ats}'. Known: {sorted(ADAPTERS)}")
    return ADAPTERS[ats]
