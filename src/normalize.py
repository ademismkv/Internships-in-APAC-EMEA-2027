"""Location canonicalization + APAC filtering.

ATS location strings are inconsistent ("Hong Kong", "HK", "香港", "Central",
"Singapore", "SG", "Shanghai, China", "Bengaluru"...). We map aliases to a
canonical city, tag each city with a region, and expose is_apac() so the pipeline
keeps only APAC roles. All APAC regions are kept (incl. Oceania).
"""
from __future__ import annotations
import re

CITY_REGION = {
    # East Asia
    "Hong Kong": "East Asia", "Shanghai": "East Asia", "Beijing": "East Asia",
    "Shenzhen": "East Asia", "Guangzhou": "East Asia", "Hangzhou": "East Asia",
    "Taipei": "East Asia", "Tokyo": "East Asia", "Osaka": "East Asia",
    "Seoul": "East Asia",
    # Southeast Asia
    "Singapore": "Southeast Asia", "Kuala Lumpur": "Southeast Asia",
    "Jakarta": "Southeast Asia", "Bangkok": "Southeast Asia",
    "Manila": "Southeast Asia", "Ho Chi Minh City": "Southeast Asia",
    "Hanoi": "Southeast Asia",
    # South Asia
    "Mumbai": "South Asia", "Bengaluru": "South Asia", "Hyderabad": "South Asia",
    "Gurugram": "South Asia", "Pune": "South Asia", "Chennai": "South Asia",
    "New Delhi": "South Asia",
    # Oceania (APAC)
    "Sydney": "Oceania", "Melbourne": "Oceania",
}

ALIASES = {
    "hong kong": "Hong Kong", "hongkong": "Hong Kong", "hong kong sar": "Hong Kong",
    "hk": "Hong Kong", "香港": "Hong Kong",
    "kowloon": "Hong Kong", "quarry bay": "Hong Kong",
    "singapore": "Singapore", "sg": "Singapore", "sgp": "Singapore", "新加坡": "Singapore",
    "shanghai": "Shanghai", "上海": "Shanghai", "beijing": "Beijing", "北京": "Beijing",
    "peking": "Beijing", "shenzhen": "Shenzhen", "深圳": "Shenzhen",
    "guangzhou": "Guangzhou", "广州": "Guangzhou", "hangzhou": "Hangzhou", "杭州": "Hangzhou",
    "taipei": "Taipei", "台北": "Taipei", "taiwan": "Taipei",
    "tokyo": "Tokyo", "東京": "Tokyo", "osaka": "Osaka",
    "seoul": "Seoul", "서울": "Seoul", "gangnam": "Seoul", "korea": "Seoul",
    "south korea": "Seoul", "republic of korea": "Seoul",
    "kuala lumpur": "Kuala Lumpur", "kl": "Kuala Lumpur", "malaysia": "Kuala Lumpur",
    "jakarta": "Jakarta", "indonesia": "Jakarta", "bangkok": "Bangkok", "thailand": "Bangkok",
    "manila": "Manila", "philippines": "Manila", "taguig": "Manila",
    "ho chi minh": "Ho Chi Minh City", "ho chi minh city": "Ho Chi Minh City",
    "saigon": "Ho Chi Minh City", "hanoi": "Hanoi", "vietnam": "Ho Chi Minh City",
    "mumbai": "Mumbai", "bombay": "Mumbai", "bengaluru": "Bengaluru", "bangalore": "Bengaluru",
    "hyderabad": "Hyderabad", "gurugram": "Gurugram", "gurgaon": "Gurugram",
    "pune": "Pune", "chennai": "Chennai", "new delhi": "New Delhi", "delhi": "New Delhi",
    "sydney": "Sydney", "melbourne": "Melbourne",
}

ALL_REGIONS = set(CITY_REGION.values())

# Word tokens across Latin + CJK (hiragana/katakana, unified Han, Hangul), so
# "Singapore (SG)" -> ["singapore", "sg"] and "東京, Japan" -> ["東京", "japan"].
_TOKEN = re.compile(r"[0-9a-z\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]+")


def canonical_cities(raw: str) -> list[str]:
    if not raw:
        return []
    text = raw.lower()
    found: list[str] = []
    # 1. Multi-word aliases: substring match on the whole string (longest first).
    for alias in sorted(ALIASES, key=len, reverse=True):
        if " " in alias and alias in text and ALIASES[alias] not in found:
            found.append(ALIASES[alias])
    # 2. Single-token aliases: exact token match (handles HK, SG, CJK, parens).
    for tok in _TOKEN.findall(text):
        if tok in ALIASES and ALIASES[tok] not in found:
            found.append(ALIASES[tok])
    return found


def is_apac(raw: str, regions: set[str] = ALL_REGIONS) -> bool:
    return any(CITY_REGION.get(c) in regions for c in canonical_cities(raw))


def display_location(raw: str, regions: set[str] = ALL_REGIONS) -> str:
    cities = [c for c in canonical_cities(raw) if CITY_REGION.get(c) in regions]
    return ", ".join(cities) if cities else raw.strip()
