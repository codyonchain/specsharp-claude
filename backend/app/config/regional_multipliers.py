"""
Regional cost multipliers.

Design goals:
- Keep the public contract: get_regional_multiplier(location: str) -> float
- Avoid huge per-city configs (no 6000-line file)
- Be robust to common user inputs: "City, ST", "City ST", or just "City"
- Provide solid 80/20 differentiation between regions (Nashville vs Manchester vs Dallas, etc.)
- Allow small metro overrides + state defaults, with an explicit baseline.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

# National baseline (neutral). All other values are relative to this.
BASELINE_MULTIPLIER = 1.00


# ---------------------------------------------------------------------------
# Metro overrides (small list; expand over time)
# Keys are (city_lower, state_upper) for exactness.
# ---------------------------------------------------------------------------

METRO_OVERRIDES: Dict[Tuple[str, str], float] = {
    # ---------------------------------------------------------------------
    # Tier A — Very High Cost (US leaders)
    # ---------------------------------------------------------------------
    ("new york", "NY"): 1.30,
    ("san francisco", "CA"): 1.26,
    ("san jose", "CA"): 1.24,

    # ---------------------------------------------------------------------
    # Tier B — High Cost (major coastal & high-labor metros)
    # ---------------------------------------------------------------------
    ("boston", "MA"): 1.18,
    ("seattle", "WA"): 1.14,
    ("washington", "DC"): 1.14,
    ("los angeles", "CA"): 1.15,
    ("san diego", "CA"): 1.12,

    # ---------------------------------------------------------------------
    # Tier C — Upper-Mid (large metros with steady cost pressure)
    # ---------------------------------------------------------------------
    ("chicago", "IL"): 1.12,
    ("philadelphia", "PA"): 1.10,
    ("denver", "CO"): 1.04,
    ("miami", "FL"): 1.05,
    ("portland", "OR"): 1.06,
    ("minneapolis", "MN"): 1.05,
    ("baltimore", "MD"): 1.06,
    ("sacramento", "CA"): 1.10,

    # ---------------------------------------------------------------------
    # Tier D — Baseline-ish (strong volume markets, moderate costs)
    # ---------------------------------------------------------------------
    ("nashville", "TN"): 1.02,
    ("atlanta", "GA"): 0.99,
    ("charlotte", "NC"): 0.99,
    ("raleigh", "NC"): 1.00,
    ("orlando", "FL"): 1.00,
    ("tampa", "FL"): 1.00,
    ("jacksonville", "FL"): 0.98,
    ("richmond", "VA"): 1.01,
    ("hartford", "CT"): 1.08,
    ("pittsburgh", "PA"): 1.03,
    ("st. louis", "MO"): 0.99,
    ("kansas city", "MO"): 0.98,
    ("indianapolis", "IN"): 0.97,
    ("columbus", "OH"): 0.98,
    ("cincinnati", "OH"): 0.97,
    ("cleveland", "OH"): 0.97,
    ("detroit", "MI"): 1.00,
    ("salt lake city", "UT"): 0.99,
    ("las vegas", "NV"): 1.00,

    # ---------------------------------------------------------------------
    # Tier E — Lower Cost (many Sunbelt / Plains markets)
    # ---------------------------------------------------------------------
    ("dallas", "TX"): 0.97,
    ("houston", "TX"): 0.96,
    ("austin", "TX"): 0.99,
    ("san antonio", "TX"): 0.94,
    ("phoenix", "AZ"): 0.95,

    # ---------------------------------------------------------------------
    # New England non-major metro sanity anchor
    # ---------------------------------------------------------------------
    ("manchester", "NH"): 1.07,
}

MARKET_METRO_OVERRIDES: Dict[Tuple[str, str], float] = {
    # Tier A — strongest/most expensive demand markets
    ("new york", "NY"): 1.20,
    ("san francisco", "CA"): 1.18,
    ("san jose", "CA"): 1.16,
    ("boston", "MA"): 1.12,
    ("seattle", "WA"): 1.10,
    ("washington", "DC"): 1.12,
    ("los angeles", "CA"): 1.10,
    ("san diego", "CA"): 1.07,

    # Tier B — strong markets
    ("miami", "FL"): 1.10,
    ("denver", "CO"): 1.06,
    ("chicago", "IL"): 1.05,
    ("philadelphia", "PA"): 1.04,
    ("portland", "OR"): 1.03,

    # Tier C — high-volume baseline-ish
    ("nashville", "TN"): 1.03,
    ("atlanta", "GA"): 1.02,
    ("charlotte", "NC"): 1.02,
    ("raleigh", "NC"): 1.02,
    ("orlando", "FL"): 1.02,
    ("tampa", "FL"): 1.02,

    # Tier D — large Sunbelt / lower-cost but strong growth
    ("dallas", "TX"): 1.03,
    ("austin", "TX"): 1.05,
    ("houston", "TX"): 1.00,
    ("phoenix", "AZ"): 1.02,
    ("las vegas", "NV"): 1.02,

    # Additional
    ("minneapolis", "MN"): 1.01,
    ("baltimore", "MD"): 1.02,
    ("sacramento", "CA"): 1.03,
    ("jacksonville", "FL"): 1.01,
    ("richmond", "VA"): 1.01,
    ("hartford", "CT"): 1.01,
    ("pittsburgh", "PA"): 1.00,
    ("st. louis", "MO"): 1.00,
    ("kansas city", "MO"): 1.00,
    ("indianapolis", "IN"): 1.00,
    ("columbus", "OH"): 1.00,
    ("cincinnati", "OH"): 1.00,
    ("cleveland", "OH"): 0.99,
    ("detroit", "MI"): 0.99,
    ("salt lake city", "UT"): 1.02,

    # New England anchor
    ("manchester", "NH"): 1.01,
}

# Optional: city-only inference for cities that are unambiguous in your app.
# This is the key to making NLP "city only" still work.
UNAMBIGUOUS_CITY_TO_STATE: Dict[str, str] = {
    "new york": "NY",
    "san francisco": "CA",
    "san jose": "CA",
    "boston": "MA",
    "seattle": "WA",
    "washington": "DC",
    "los angeles": "CA",
    "san diego": "CA",

    "chicago": "IL",
    "philadelphia": "PA",
    "denver": "CO",
    "miami": "FL",
    "portland": "OR",
    "minneapolis": "MN",
    "baltimore": "MD",
    "sacramento": "CA",

    "nashville": "TN",
    "atlanta": "GA",
    "charlotte": "NC",
    "raleigh": "NC",
    "orlando": "FL",
    "tampa": "FL",
    "jacksonville": "FL",
    "richmond": "VA",
    "hartford": "CT",
    "pittsburgh": "PA",
    "st. louis": "MO",
    "kansas city": "MO",
    "indianapolis": "IN",
    "columbus": "OH",
    "cincinnati": "OH",
    "cleveland": "OH",
    "detroit": "MI",
    "salt lake city": "UT",
    "las vegas": "NV",

    "dallas": "TX",
    "houston": "TX",
    "austin": "TX",
    "san antonio": "TX",
    "phoenix": "AZ",

    "manchester": "NH",
}


# ---------------------------------------------------------------------------
# State defaults (all 50 states, compact)
# These are deliberately "directionally correct" indices, not perfect RSMeans.
# You can refine later without touching any building-type logic.
# ---------------------------------------------------------------------------

STATE_DEFAULTS: Dict[str, float] = {
    # West Coast / Pacific (higher)
    "CA": 1.14, "WA": 1.10, "OR": 1.06, "AK": 1.20, "HI": 1.25,

    # Northeast / Mid-Atlantic (higher)
    "MA": 1.14, "NY": 1.16, "NJ": 1.10, "CT": 1.08, "RI": 1.08,
    "PA": 1.05, "MD": 1.06, "DC": 1.10, "VA": 1.03, "DE": 1.03,

    # New England / North (moderate-high)
    "NH": 1.05, "VT": 1.05, "ME": 1.04,

    # Midwest (mixed)
    "IL": 1.06, "MI": 1.02, "OH": 0.98, "WI": 1.01, "MN": 1.05,
    "IN": 0.97, "IA": 0.96, "MO": 0.98, "KS": 0.97, "NE": 0.96,
    "ND": 0.97, "SD": 0.96,

    # Southeast (baseline-ish)
    "TN": 1.00, "GA": 0.99, "NC": 0.99, "SC": 0.98, "AL": 0.96, "MS": 0.95,
    "KY": 0.98, "FL": 1.00, "LA": 0.95, "AR": 0.94, "WV": 0.97,

    # Texas / Plains (lower)
    "TX": 0.96, "OK": 0.93,

    # Mountain / Southwest (generally lower-mid)
    "AZ": 0.95, "NM": 0.94, "CO": 1.02, "UT": 0.98, "NV": 1.00,
    "ID": 0.98, "MT": 0.99, "WY": 0.98,
}

MARKET_STATE_DEFAULTS: Dict[str, float] = {
    # Higher-demand coastal
    "CA": 1.06, "NY": 1.08, "MA": 1.05, "WA": 1.04, "OR": 1.02, "NJ": 1.03, "CT": 1.02,
    "FL": 1.03, "DC": 1.05,

    # Baseline-ish
    "TN": 1.02, "GA": 1.02, "NC": 1.02, "SC": 1.01, "VA": 1.01, "PA": 1.01, "IL": 1.01,
    "CO": 1.02, "AZ": 1.01, "NV": 1.01, "UT": 1.01, "TX": 1.02,

    # Slightly lower demand
    "OH": 0.99, "MI": 0.99, "IN": 0.99, "WI": 0.99, "MN": 1.00, "MO": 0.99, "KS": 0.99,
    "AL": 0.98, "MS": 0.98, "AR": 0.98, "OK": 0.98, "LA": 0.98, "KY": 0.99, "WV": 0.98,
    "NM": 0.99, "ID": 0.99, "MT": 0.99, "WY": 0.99, "ND": 0.99, "SD": 0.99, "NE": 0.99, "IA": 0.99,
    "ME": 0.99, "NH": 1.00, "VT": 0.99, "RI": 1.01, "MD": 1.01, "DE": 1.00,

    # Remote / special
    "AK": 1.00, "HI": 1.05,
}


# ---------------------------------------------------------------------------
# Backward-compatible dict export (kept for any UI / display usage)
# This is NOT the source of truth anymore; METRO_OVERRIDES + STATE_DEFAULTS are.
# ---------------------------------------------------------------------------

REGIONAL_MULTIPLIERS: Dict[str, float] = {
    # Keep a small, readable set — mainly for display/debug.
    "Nashville, TN": METRO_OVERRIDES[("nashville", "TN")],
    "Manchester, NH": METRO_OVERRIDES[("manchester", "NH")],
    "Dallas, TX": METRO_OVERRIDES[("dallas", "TX")],
    "default": BASELINE_MULTIPLIER,
}


# ---------------------------------------------------------------------------
# Parsing + resolving
# ---------------------------------------------------------------------------

_LOCATION_RE = re.compile(
    r"^\s*(?P<city>[A-Za-z .'\-]+?)\s*(?:,|\s)\s*(?P<state>[A-Za-z]{2})\s*$"
)

def _normalize_city(city: str) -> str:
    return re.sub(r"\s+", " ", city.strip().lower())

def _normalize_state(state: str) -> str:
    return state.strip().upper()

def parse_location(location: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Attempt to parse a user-provided location string into (city, state).

    Supports:
    - "City, ST"
    - "City ST"
    - "City" (state inferred only if city is in UNAMBIGUOUS_CITY_TO_STATE)
    """
    if not location:
        return None, None

    loc = location.strip()
    m = _LOCATION_RE.match(loc)
    if m:
        city = _normalize_city(m.group("city"))
        state = _normalize_state(m.group("state"))
        return city, state

    # City-only fallback: try to infer state for known cities
    city_only = _normalize_city(loc)
    inferred_state = UNAMBIGUOUS_CITY_TO_STATE.get(city_only)
    if inferred_state:
        return city_only, inferred_state

    return city_only if city_only else None, None


def resolve_multiplier(city: Optional[str], state: Optional[str]) -> float:
    """
    Resolve cost multiplier using:
    1) Exact metro override (city,state)
    2) State default
    3) Baseline
    """
    if city and state:
        key = (_normalize_city(city), _normalize_state(state))
        if key in METRO_OVERRIDES:
            return METRO_OVERRIDES[key]
        if key[1] in STATE_DEFAULTS:
            return STATE_DEFAULTS[key[1]]
        return BASELINE_MULTIPLIER

    if state:
        st = _normalize_state(state)
        return STATE_DEFAULTS.get(st, BASELINE_MULTIPLIER)

    return BASELINE_MULTIPLIER


def resolve_market_multiplier(city: Optional[str], state: Optional[str]) -> float:
    """
    Resolve market (revenue) multiplier using metro/state defaults.
    """
    if city and state:
        key = (_normalize_city(city), _normalize_state(state))
        if key in MARKET_METRO_OVERRIDES:
            return MARKET_METRO_OVERRIDES[key]

    if state:
        st = _normalize_state(state)
        if st in MARKET_STATE_DEFAULTS:
            return MARKET_STATE_DEFAULTS[st]

    return 1.0


def get_regional_multiplier(location: str) -> float:
    """
    Public API used by CleanEngineV2.
    Keep this stable forever.
    """
    city, state = parse_location(location)
    return float(resolve_multiplier(city, state))


def _location_has_explicit_state(location: Optional[str]) -> bool:
    if not location:
        return False
    loc = location.strip()
    if "," in loc:
        return True
    # Check for trailing two-letter state code
    tail = loc.split()[-1]
    return len(tail) == 2 and tail.isalpha()


def resolve_location_context(location: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Return a structured view of how a location string resolved so callers
    can persist explainable metadata.
    """
    loc = location or ""
    city, state = parse_location(loc)
    explicit_state = _location_has_explicit_state(loc)
    inferred_city_state = bool(state and not explicit_state)
    normalized_loc = loc.strip() or None

    if inferred_city_state:
        source = "city_inferred"
    elif city and state and (_normalize_city(city), _normalize_state(state)) in METRO_OVERRIDES:
        source = "metro_override"
    elif state and _normalize_state(state) in STATE_DEFAULTS:
        source = "state_default"
    else:
        source = "baseline"

    pretty_location = None
    if city and state:
        pretty_location = f"{city.title()}, {state}"
    elif city:
        pretty_location = city.title()
    elif state:
        pretty_location = state

    base_multiplier = resolve_multiplier(city, state)
    cost_factor = base_multiplier
    market_factor = resolve_market_multiplier(city, state)

    return {
        "city": city,
        "state": state,
        "source": source,
        "location_display": pretty_location or normalized_loc,
        "cost_factor": cost_factor,
        "market_factor": market_factor,
        "multiplier": cost_factor,
    }
