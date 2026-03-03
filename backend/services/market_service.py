"""
AgriScheme Backend — Market Price service.
Provides simulated but realistic crop market prices.

Uses base MSP / average mandi prices with small daily fluctuations
so prices look live and dynamic without depending on unreliable
external APIs.
"""
import random
import math
from datetime import datetime

# Base prices in ₹/quintal (approximate real MSP / market prices 2024-25)
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
}

# Key mandis per state (top 2-3 markets)
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

# Default crops shown per state
_STATE_CROPS = {
    "Tamil Nadu":       ["Rice", "Sugarcane", "Coconut", "Groundnut", "Cotton"],
    "Kerala":           ["Coconut", "Rice", "Tea", "Coffee", "Rubber", "Spices"],
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


def _generate_price(base_price):
    """Generate a realistic fluctuating price based on time-of-day."""
    # Use current time as seed for deterministic-ish daily variation
    now = datetime.now()
    day_seed = now.year * 1000 + now.timetuple().tm_yday
    hour_factor = math.sin(now.hour * 0.3) * 0.02  # ±2% intra-day swing

    # Deterministic daily variation (±5%)
    random.seed(day_seed)
    daily_pct = random.uniform(-0.05, 0.05)
    random.seed()  # Reset to true random

    price = base_price * (1 + daily_pct + hour_factor)
    return round(price, 0)


def _get_trend(base_price, current_price):
    """Determine price trend."""
    diff_pct = (current_price - base_price) / base_price * 100
    if diff_pct > 1:
        return "up"
    elif diff_pct < -1:
        return "down"
    return "stable"


def get_market_prices(state, crop=None):
    """Get market prices for a state.

    Args:
        state: Indian state name
        crop:  Optional specific crop filter

    Returns:
        dict with market info and crop prices
    """
    # Determine which crops to show
    if crop and crop in _BASE_PRICES:
        crop_list = [crop]
    else:
        crop_list = _STATE_CROPS.get(state, list(_BASE_PRICES.keys())[:8])

    # Determine mandis
    mandis = _STATE_MANDIS.get(state, _STATE_MANDIS["All"])

    prices = []
    for c in crop_list:
        info = _BASE_PRICES.get(c)
        if not info:
            continue

        current_price = _generate_price(info["price"])
        trend = _get_trend(info["price"], current_price)

        # Change amount
        change = round(current_price - info["price"], 0)

        prices.append({
            "crop": c,
            "price": current_price,
            "unit": f"₹/{info['unit']}",
            "change": change,
            "change_pct": round((change / info["price"]) * 100, 1),
            "trend": trend,
            "mandi": mandis[0],  # Primary mandi
        })

    return {
        "state": state,
        "mandis": mandis,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prices": prices,
    }
