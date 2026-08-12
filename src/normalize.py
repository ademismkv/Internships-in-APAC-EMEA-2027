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
    # --- EMEA ---
    # UK & Ireland
    "London": "UK & Ireland", "Dublin": "UK & Ireland", "Edinburgh": "UK & Ireland",
    "Manchester": "UK & Ireland", "Cambridge": "UK & Ireland",
    # Western Europe
    "Amsterdam": "Western Europe", "Paris": "Western Europe", "Berlin": "Western Europe",
    "Munich": "Western Europe", "Frankfurt": "Western Europe", "Zurich": "Western Europe",
    "Geneva": "Western Europe", "Brussels": "Western Europe",
    "Luxembourg": "Western Europe", "Vienna": "Western Europe",
    # Southern Europe
    "Madrid": "Southern Europe", "Barcelona": "Southern Europe", "Milan": "Southern Europe",
    "Lisbon": "Southern Europe", "Rome": "Southern Europe",
    # Nordics
    "Stockholm": "Nordics", "Oslo": "Nordics", "Copenhagen": "Nordics",
    "Helsinki": "Nordics",
    # Eastern Europe
    "Warsaw": "Eastern Europe", "Prague": "Eastern Europe", "Budapest": "Eastern Europe",
    "Bucharest": "Eastern Europe", "Krakow": "Eastern Europe",
    # Middle East
    "Dubai": "Middle East", "Abu Dhabi": "Middle East", "Riyadh": "Middle East",
    "Doha": "Middle East", "Kuwait City": "Middle East", "Tel Aviv": "Middle East",
    "Istanbul": "Middle East",
    # Africa
    "Cairo": "Africa", "Johannesburg": "Africa", "Lagos": "Africa", "Nairobi": "Africa",
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
    # --- EMEA aliases ---
    "london": "London", "uk": "London", "united kingdom": "London",
    "england": "London", "britain": "London", "edinburgh": "Edinburgh",
    "manchester": "Manchester", "cambridge": "Cambridge",
    "dublin": "Dublin", "ireland": "Dublin",
    "amsterdam": "Amsterdam", "netherlands": "Amsterdam", "the netherlands": "Amsterdam",
    "paris": "Paris", "france": "Paris",
    "berlin": "Berlin", "munich": "Munich", "münchen": "Munich", "frankfurt": "Frankfurt",
    "germany": "Berlin", "zurich": "Zurich", "zürich": "Zurich", "geneva": "Geneva",
    "switzerland": "Zurich", "brussels": "Brussels", "belgium": "Brussels",
    "luxembourg": "Luxembourg", "vienna": "Vienna", "austria": "Vienna",
    "madrid": "Madrid", "barcelona": "Barcelona", "spain": "Madrid",
    "milan": "Milan", "rome": "Rome", "italy": "Milan",
    "lisbon": "Lisbon", "portugal": "Lisbon",
    "stockholm": "Stockholm", "sweden": "Stockholm", "oslo": "Oslo", "norway": "Oslo",
    "copenhagen": "Copenhagen", "denmark": "Copenhagen", "helsinki": "Helsinki",
    "finland": "Helsinki",
    "warsaw": "Warsaw", "poland": "Warsaw", "krakow": "Krakow", "kraków": "Krakow",
    "prague": "Prague", "czech": "Prague", "budapest": "Budapest", "hungary": "Budapest",
    "bucharest": "Bucharest", "romania": "Bucharest",
    "dubai": "Dubai", "abu dhabi": "Abu Dhabi", "uae": "Dubai",
    "riyadh": "Riyadh", "saudi arabia": "Riyadh", "saudi": "Riyadh",
    "doha": "Doha", "qatar": "Doha", "kuwait city": "Kuwait City", "kuwait": "Kuwait City",
    "tel aviv": "Tel Aviv", "israel": "Tel Aviv",
    "istanbul": "Istanbul", "turkey": "Istanbul", "türkiye": "Istanbul",
    "cairo": "Cairo", "egypt": "Cairo", "johannesburg": "Johannesburg",
    "south africa": "Johannesburg", "lagos": "Lagos", "nigeria": "Lagos",
    "nairobi": "Nairobi", "kenya": "Nairobi",
}

# Region groups.
APAC_REGIONS = {"East Asia", "Southeast Asia", "South Asia", "Oceania"}
EMEA_REGIONS = {"UK & Ireland", "Western Europe", "Southern Europe", "Nordics",
                "Eastern Europe", "Middle East", "Africa"}
TARGET_REGIONS = APAC_REGIONS | EMEA_REGIONS  # this project tracks EMEA + APAC

ALL_REGIONS = set(CITY_REGION.values())
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


def region_of(raw: str) -> str | None:
    """Macro-region of the first recognized city, or None."""
    for c in canonical_cities(raw):
        if c in CITY_REGION:
            return CITY_REGION[c]
    return None


def is_target(raw: str, regions: set[str] = TARGET_REGIONS) -> bool:
    """True if the role is in a region this project tracks (EMEA + APAC)."""
    return any(CITY_REGION.get(c) in regions for c in canonical_cities(raw))


def is_apac(raw: str, regions: set[str] = APAC_REGIONS) -> bool:
    """APAC-only membership (kept for tests / APAC-specific callers)."""
    return any(CITY_REGION.get(c) in regions for c in canonical_cities(raw))


def display_location(raw: str, regions: set[str] = TARGET_REGIONS) -> str:
    cities = [c for c in canonical_cities(raw) if CITY_REGION.get(c) in regions]
    return ", ".join(cities) if cities else raw.strip()
