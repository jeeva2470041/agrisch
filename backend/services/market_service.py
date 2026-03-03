"""
AgriScheme Backend — Market Price Service (Production).

3-tier data strategy:
  1. Cache  — JSON file cache with 6-hour TTL
  2. API    — data.gov.in Open Government Data Platform (live mandi prices)
  3. MSP    — Fallback to government MSP-based simulation

Env vars:
  DATA_GOV_API_KEY — Free API key from https://data.gov.in/
  MARKET_CACHE_TTL — Cache time-to-live in seconds (default: 21600 = 6 hrs)
  MARKET_MODE      — "api" (default) | "msp_only" (skip API entirely)

API Resource:
  data.gov.in resource for daily commodity prices from AGMARKNET.
  API Docs: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
"""

import os
import json
import time
import logging
import math
import random
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ─── Configuration ────────────────────────────────────────────────────────

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")
MARKET_CACHE_TTL = int(os.getenv("MARKET_CACHE_TTL", "21600"))  # 6 hours
MARKET_MODE = os.getenv("MARKET_MODE", "api").lower()

# data.gov.in resource ID for AGMARKNET daily commodity prices
_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
_API_BASE = f"https://api.data.gov.in/resource/{_RESOURCE_ID}"

# Cache file
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CACHE_DIR = os.path.join(_BACKEND_DIR, "data")
_CACHE_FILE = os.path.join(_CACHE_DIR, "market_cache.json")

# ─── MSP / Base Prices (₹/quintal, 2024-25 GOI declared) ─────────────────

_BASE_PRICES = {
    "Rice":       {"price": 2320, "unit": "quintal"},
    "Wheat":      {"price": 2275, "unit": "quintal"},
    "Maize":      {"price": 2090, "unit": "quintal"},
    "Cotton":     {"price": 7121, "unit": "quintal"},
    "Sugarcane":  {"price": 315,  "unit": "quintal"},
    "Soybean":    {"price": 4892, "unit": "quintal"},
    "Groundnut":  {"price": 6783, "unit": "quintal"},
    "Mustard":    {"price": 5650, "unit": "quintal"},
    "Jowar":      {"price": 3371, "unit": "quintal"},
    "Bajra":      {"price": 2625, "unit": "quintal"},
    "Ragi":       {"price": 4290, "unit": "quintal"},
    "Tur":        {"price": 7550, "unit": "quintal"},
    "Moong":      {"price": 8682, "unit": "quintal"},
    "Urad":       {"price": 7400, "unit": "quintal"},
    "Coconut":    {"price": 3400, "unit": "quintal"},
    "Tea":        {"price": 22000, "unit": "quintal"},
    "Coffee":     {"price": 29400, "unit": "quintal"},
    "Jute":       {"price": 5050, "unit": "quintal"},
    "Tobacco":    {"price": 7600, "unit": "quintal"},
    "Rubber":     {"price": 17200, "unit": "quintal"},
    "Millets":    {"price": 2625, "unit": "quintal"},
    "Pulses":     {"price": 7400, "unit": "quintal"},
    "Sunflower":  {"price": 7280, "unit": "quintal"},
    "Spices":     {"price": 32000, "unit": "quintal"},
    "Vegetables": {"price": 2500, "unit": "quintal"},
    "Fruits":     {"price": 4500, "unit": "quintal"},
    "Oilseeds":   {"price": 5650, "unit": "quintal"},
}

# Mapping: our crop names → data.gov.in commodity names
_CROP_TO_COMMODITY = {
    "Rice": "Rice", "Wheat": "Wheat", "Maize": "Maize",
    "Cotton": "Cotton", "Sugarcane": "Sugarcane",
    "Soybean": "Soyabean", "Groundnut": "Groundnut",
    "Mustard": "Mustard", "Jowar": "Jowar(Sorghum)",
    "Bajra": "Bajra(Pearl Millet)", "Ragi": "Ragi (Finger Millet)",
    "Tur": "Arhar (Tur/Red Gram)", "Moong": "Moong(Green Gram)",
    "Urad": "Urad (Blackgram)", "Coconut": "Coconut",
    "Tea": "Tea", "Coffee": "Coffee",
    "Jute": "Jute", "Tobacco": "Tobacco",
    "Millets": "Bajra(Pearl Millet)",
    "Pulses": "Arhar (Tur/Red Gram)",
    "Sunflower": "Sunflower",
    "Oilseeds": "Mustard",
}

# Key mandis per state
_STATE_MANDIS = {
    "Tamil Nadu":       ["Coimbatore", "Madurai", "Salem"],
    "Kerala":           ["Ernakulam", "Thrissur", "Kozhikode"],
    "Andhra Pradesh":   ["Guntur", "Kurnool", "Vijayawada"],
    "Telangana":        ["Hyderabad", "Warangal", "Nizamabad"],
    "Karnataka":        ["Hubli", "Mysore", "Davangere"],
    "Maharashtra":      ["Pune", "Nagpur", "Nashik"],
    "Punjab":           ["Amritsar", "Ludhiana", "Jalandhar"],
    "Haryana":          ["Karnal", "Hisar", "Sirsa"],
    "Uttar Pradesh":    ["Lucknow", "Agra", "Kanpur"],
    "Madhya Pradesh":   ["Indore", "Bhopal", "Jabalpur"],
    "Rajasthan":        ["Jaipur", "Jodhpur", "Kota"],
    "Gujarat":          ["Ahmedabad", "Rajkot", "Surat"],
    "West Bengal":      ["Kolkata", "Bardhaman", "Siliguri"],
    "Bihar":            ["Patna", "Muzaffarpur", "Bhagalpur"],
    "Odisha":           ["Bhubaneswar", "Cuttack", "Sambalpur"],
    "Assam":            ["Guwahati", "Silchar", "Jorhat"],
    "Jharkhand":        ["Ranchi", "Dhanbad", "Jamshedpur"],
    "Chhattisgarh":     ["Raipur", "Bilaspur", "Durg"],
    "Uttarakhand":      ["Dehradun", "Haridwar", "Haldwani"],
    "Himachal Pradesh": ["Shimla", "Mandi", "Kangra"],
    "Goa":              ["Panaji", "Margao"],
    "All":              ["Delhi", "Mumbai", "Chennai"],
}

# Default crops per state
_STATE_CROPS = {
    "Tamil Nadu":       ["Rice", "Sugarcane", "Coconut", "Groundnut", "Cotton"],
    "Kerala":           ["Coconut", "Rice", "Tea", "Coffee", "Spices"],
    "Andhra Pradesh":   ["Rice", "Cotton", "Groundnut", "Sugarcane", "Maize"],
    "Telangana":        ["Rice", "Cotton", "Maize", "Soybean", "Tur"],
    "Karnataka":        ["Rice", "Ragi", "Sugarcane", "Cotton", "Groundnut"],
    "Maharashtra":      ["Sugarcane", "Cotton", "Soybean", "Groundnut", "Jowar"],
    "Punjab":           ["Wheat", "Rice", "Cotton", "Maize", "Sugarcane"],
    "Haryana":          ["Wheat", "Rice", "Mustard", "Sugarcane", "Bajra"],
    "Uttar Pradesh":    ["Wheat", "Rice", "Sugarcane", "Mustard", "Maize"],
    "Madhya Pradesh":   ["Wheat", "Soybean", "Maize", "Tur", "Mustard"],
    "Rajasthan":        ["Wheat", "Mustard", "Bajra", "Groundnut", "Jowar"],
    "Gujarat":          ["Cotton", "Groundnut", "Wheat", "Rice", "Sugarcane"],
    "West Bengal":      ["Rice", "Jute", "Tea", "Maize", "Mustard"],
    "Bihar":            ["Rice", "Wheat", "Maize", "Sugarcane", "Tur"],
}


# ─── Cache ────────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    """Load the market price cache from disk."""
    if not os.path.exists(_CACHE_FILE):
        return {}
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict):
    """Save the market price cache to disk."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logger.warning("Failed to save market cache: %s", e)


def _get_cached(state: str, crop: str) -> dict | None:
    """Return cached data if valid (within TTL)."""
    cache = _load_cache()
    key = f"{state}:{crop}"
    entry = cache.get(key)
    if entry and time.time() - entry.get("timestamp", 0) < MARKET_CACHE_TTL:
        logger.debug("Cache hit: %s", key)
        return entry.get("data")
    return None


def _set_cache(state: str, crop: str, data: dict):
    """Store data in cache with current timestamp."""
    cache = _load_cache()
    key = f"{state}:{crop}"
    cache[key] = {"timestamp": time.time(), "data": data}
    _save_cache(cache)


# ─── data.gov.in API ──────────────────────────────────────────────────────

def _fetch_from_api(state: str, commodity: str, limit: int = 50) -> list | None:
    """Fetch real mandi prices from data.gov.in AGMARKNET API.

    Returns list of price records, or None on failure.
    """
    if not DATA_GOV_API_KEY:
        logger.debug("No DATA_GOV_API_KEY set — skipping API call")
        return None

    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "limit": limit,
        "filters[commodity]": commodity,
    }

    # Add state filter (data.gov.in uses state name directly)
    if state and state != "All":
        params["filters[state]"] = state

    try:
        response = requests.get(
            _API_BASE,
            params=params,
            timeout=10,
            headers={"Accept": "application/json"},
        )

        if response.status_code == 429:
            logger.warning("data.gov.in API rate limited")
            return None

        if response.status_code != 200:
            logger.warning(
                "data.gov.in API returned %d: %s",
                response.status_code, response.text[:200],
            )
            return None

        data = response.json()
        records = data.get("records", [])

        if not records:
            logger.debug("No records from API for %s / %s", state, commodity)
            return None

        return records

    except requests.exceptions.Timeout:
        logger.warning("data.gov.in API timeout for %s / %s", state, commodity)
        return None
    except requests.exceptions.ConnectionError:
        logger.warning("data.gov.in API connection error")
        return None
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning("data.gov.in API parse error: %s", e)
        return None


def _parse_api_records(records: list, crop: str) -> dict | None:
    """Parse API records into our standard price format.

    Returns price info dict or None if records are unusable.
    """
    if not records:
        return None

    valid_prices = []
    mandi_name = None
    arrival_date = None

    for rec in records:
        try:
            modal = float(rec.get("modal_price", 0))
            min_p = float(rec.get("min_price", 0))
            max_p = float(rec.get("max_price", 0))
            if modal <= 0:
                continue

            valid_prices.append({
                "modal": modal,
                "min": min_p,
                "max": max_p,
                "market": rec.get("market", ""),
                "date": rec.get("arrival_date", ""),
                "district": rec.get("district", ""),
                "variety": rec.get("variety", ""),
            })

            if not mandi_name:
                mandi_name = rec.get("market", "")
            if not arrival_date:
                arrival_date = rec.get("arrival_date", "")

        except (ValueError, TypeError):
            continue

    if not valid_prices:
        return None

    # Aggregate: weighted average of modal prices
    avg_price = sum(p["modal"] for p in valid_prices) / len(valid_prices)
    positive_mins = [p["min"] for p in valid_prices if p["min"] > 0]
    min_price = min(positive_mins) if positive_mins else avg_price
    max_price = max(p["max"] for p in valid_prices) if valid_prices else avg_price

    # Compare with MSP for trend
    msp = _BASE_PRICES.get(crop, {}).get("price", avg_price)
    change = round(avg_price - msp, 0)
    change_pct = round((change / msp) * 100, 1) if msp else 0

    if change_pct > 1:
        trend = "up"
    elif change_pct < -1:
        trend = "down"
    else:
        trend = "stable"

    return {
        "crop": crop,
        "price": round(avg_price, 0),
        "min_price": round(min_price, 0),
        "max_price": round(max_price, 0),
        "unit": "₹/quintal",
        "change": change,
        "change_pct": change_pct,
        "trend": trend,
        "mandi": mandi_name or "Various",
        "data_date": arrival_date or datetime.now().strftime("%d/%m/%Y"),
        "source": "data.gov.in (AGMARKNET)",
        "records_count": len(valid_prices),
    }


# ─── MSP Fallback ────────────────────────────────────────────────────────

def _generate_msp_price(base_price: float) -> float:
    """Generate a realistic fluctuating price based on MSP."""
    now = datetime.now()
    day_seed = now.year * 1000 + now.timetuple().tm_yday
    hour_factor = math.sin(now.hour * 0.3) * 0.02

    random.seed(day_seed)
    daily_pct = random.uniform(-0.05, 0.05)
    random.seed()

    return round(base_price * (1 + daily_pct + hour_factor), 0)


def _get_msp_price(crop: str, mandi: str = "N/A") -> dict:
    """Get MSP-based simulated price for a crop."""
    info = _BASE_PRICES.get(crop)
    if not info:
        return None

    current = _generate_msp_price(info["price"])
    change = round(current - info["price"], 0)
    change_pct = round((change / info["price"]) * 100, 1) if info["price"] else 0

    if change_pct > 1:
        trend = "up"
    elif change_pct < -1:
        trend = "down"
    else:
        trend = "stable"

    return {
        "crop": crop,
        "price": current,
        "unit": f"₹/{info['unit']}",
        "change": change,
        "change_pct": change_pct,
        "trend": trend,
        "mandi": mandi,
        "source": "MSP (Government of India 2024-25)",
    }


# ─── Main Public API ─────────────────────────────────────────────────────

def get_market_prices(state: str, crop: str = None) -> dict:
    """Get market prices for a state, with real API + cache + MSP fallback.

    Args:
        state: Indian state name (or "All")
        crop:  Optional specific crop filter

    Returns:
        dict with: state, mandis, last_updated, prices[], source
    """
    # Determine which crops to show
    if crop and crop in _BASE_PRICES:
        crop_list = [crop]
    else:
        crop_list = _STATE_CROPS.get(state, list(_BASE_PRICES.keys())[:8])

    mandis = _STATE_MANDIS.get(state, _STATE_MANDIS["All"])
    prices = []
    source = "msp_fallback"

    for c in crop_list:
        price_data = None

        # ── Tier 1: Cache ──
        cached = _get_cached(state, c)
        if cached:
            price_data = cached
            source = cached.get("source", "cache")

        # ── Tier 2: data.gov.in API ──
        if price_data is None and MARKET_MODE != "msp_only":
            commodity = _CROP_TO_COMMODITY.get(c, c)
            records = _fetch_from_api(state, commodity)
            if records:
                parsed = _parse_api_records(records, c)
                if parsed:
                    price_data = parsed
                    source = "data.gov.in (AGMARKNET)"
                    _set_cache(state, c, parsed)

        # ── Tier 3: MSP Fallback ──
        if price_data is None:
            price_data = _get_msp_price(c, mandis[0] if mandis else "N/A")
            source = "MSP (Government of India)"

        if price_data:
            prices.append(price_data)

    return {
        "state": state,
        "mandis": mandis,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prices": prices,
        "source": source,
        "cache_ttl_seconds": MARKET_CACHE_TTL,
    }
