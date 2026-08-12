"""Classify a role: internship? / category / season-year.

Heuristics run on the title. Conservative-but-inclusive: better to surface a
borderline role for human review than to silently drop a real one.
"""
from __future__ import annotations
import re

INTERN_PATTERNS = [
    r"\bintern(ship)?\b", r"\bco-?op\b", r"\bsummer analyst\b",
    r"\bindustrial placement\b", r"\bplacement\b", r"\bcampus\b",
    r"\bwork experience\b", r"\bapprentice(ship)?\b", r"\btrainee\b",
    r"(新卒|実習生|インターン)", r"(实习|實習)", r"(인턴|채용연계형)",
]
_INTERN_RE = re.compile("|".join(INTERN_PATTERNS), re.IGNORECASE)
_NEG_RE = re.compile(r"\binternal\b|\binternational\b", re.IGNORECASE)


def is_internship(title: str) -> bool:
    if not title:
        return False
    # If the only "intern" match comes from internal/international, reject.
    if _INTERN_RE.search(title):
        stripped = _NEG_RE.sub("", title)
        return bool(_INTERN_RE.search(stripped))
    return False


CATEGORY_RULES = [
    ("Quantitative Finance",
     r"\bquant(itative)?\b|\btrader\b|\btrading\b|\bmarket maker\b"),
    ("Data Science, AI & ML",
     r"\bmachine learning\b|\bdeep learning\b|\bdata scien|\bnlp\b|"
     r"\bresearch scientist\b|\bapplied scientist\b|\b(ai|ml)\b"),
    ("Hardware Engineering",
     r"\bhardware\b|\bfpga\b|\basic\b|\brtl\b|\bverilog\b|\bembedded\b|"
     r"\bsilicon\b|\bchip\b|\belectrical engineer\b|\bcircuit\b"),
    ("Product Management",
     r"\bproduct manager\b|\bproduct management\b|\bproduct intern\b|\bapm\b|"
     r"\bproduct operations\b"),
    ("Software Engineering",
     r"\bsoftware\b|\bswe\b|\bdeveloper\b|\bengineer\b|\bfull.?stack\b|"
     r"\bbackend\b|\bfrontend\b|\bplatform\b|\binfrastructure\b|\bsystems\b"),
]
_CAT_RES = [(n, re.compile(rx, re.IGNORECASE)) for n, rx in CATEGORY_RULES]
DEFAULT_CATEGORY = "Software Engineering"


def category(title: str) -> str:
    for name, rx in _CAT_RES:
        if rx.search(title or ""):
            return name
    return DEFAULT_CATEGORY


_YEAR_RE = re.compile(r"\b(20\d{2})\b")


def season_year(title: str):
    m = _YEAR_RE.search(title or "")
    return m.group(1) if m else None


def is_stale_year(title: str, target_year: str = "2027") -> bool:
    """True only if the title names a year strictly older than target."""
    y = season_year(title)
    return y is not None and y < target_year


def season_ok(title: str, target_year: str = "2027") -> bool:
    """Keep if it names the target year OR names no year. Drop only if it names a
    *different* year (older or a future non-target year like 2028)."""
    y = season_year(title)
    return y is None or y == target_year
