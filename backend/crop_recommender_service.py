"""
AgriScheme Backend — Smart Crop Recommendation Service.
Uses Gemini AI with multi-factor analysis (soil, weather, market, schemes)
to recommend the most profitable and suitable crops for a farmer.
"""
import os
import json
import logging
import requests
from dotenv import load_dotenv

from weather_service import get_weather
from market_service import get_market_prices

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def _clean_gemini_json(raw_text: str) -> dict:
    """Parse Gemini response text into a dict, handling markdown fences,
    thinking blocks, and truncated JSON."""
    import re
    cleaned = raw_text.strip()

    # Remove markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r'```(?:json)?\s*\n(.*?)```', cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

    # Fallback: extract first { ... } block if text has preamble
    if not cleaned.startswith("{"):
        brace_pos = cleaned.find("{")
        if brace_pos != -1:
            cleaned = cleaned[brace_pos:]

    # Try parsing as-is first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Truncation repair: strip trailing incomplete entry and close brackets
    # Remove trailing partial string values / keys
    # Step 1: strip any trailing incomplete quoted string
    cleaned = re.sub(r',\s*"[^"]*$', '', cleaned)           # trailing key without close quote
    cleaned = re.sub(r':\s*"[^"]*$', ': ""', cleaned)       # trailing value without close quote
    cleaned = re.sub(r',\s*"[^"]*"\s*:\s*"[^"]*$', '', cleaned)  # partial key:value
    cleaned = re.sub(r',\s*"[^"]*"\s*:\s*\[[^\]]*$', '', cleaned)  # partial key:[array
    cleaned = re.sub(r',\s*\{[^}]*$', '', cleaned)          # trailing partial object in array
    cleaned = cleaned.rstrip().rstrip(',')                   # trailing commas

    # Step 2: close remaining open brackets/braces
    open_braces = cleaned.count("{") - cleaned.count("}")
    open_brackets = cleaned.count("[") - cleaned.count("]")
    cleaned += "]" * max(0, open_brackets)
    cleaned += "}" * max(0, open_braces)

    return json.loads(cleaned)


def recommend_crops(
    state: str,
    season: str,
    soil_type: str = "",
    ph: float = None,
    water_availability: str = "Medium",
    land_size: float = 1.0,
    lat: float = None,
    lon: float = None,
    language: str = "en",
) -> dict:
    """Recommend top crops based on multi-factor analysis.

    Args:
        state: Indian state name.
        season: Kharif / Rabi / Zaid.
        soil_type: Soil type (optional).
        ph: Soil pH (optional).
        water_availability: Low / Medium / High.
        land_size: Farm size in hectares.
        lat/lon: GPS coordinates for weather data (optional).
        language: Response language code.

    Returns:
        dict with 'recommendations' list or 'error' key.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured on the server."}

    lang_map = {"en": "English", "hi": "Hindi", "ta": "Tamil", "ml": "Malayalam"}
    lang_name = lang_map.get(language, "English")

    # ── Gather context data ──
    weather_context = "Weather data not available."
    if lat and lon:
        try:
            weather_data = get_weather(lat, lon)
            if weather_data:
                current = weather_data.get("current", {})
                daily = weather_data.get("daily", [])
                total_precip = sum(d.get("precipitation", 0) for d in daily)
                weather_context = (
                    f"Current temperature: {current.get('temperature', 'N/A')}°C, "
                    f"Humidity: {current.get('humidity', 'N/A')}%, "
                    f"5-day precipitation forecast: {total_precip:.1f}mm"
                )
        except Exception as e:
            logger.warning("Weather fetch for crop rec failed: %s", e)

    market_context = "Market price data not available."
    try:
        market_data = get_market_prices(state)
        if market_data and "prices" in market_data:
            prices = market_data["prices"][:10]  # Top 10 crops
            price_lines = [
                f"  {p['crop']}: ₹{p.get('price', 'N/A')}/quintal (MSP: ₹{p.get('msp', 'N/A')})"
                for p in prices
            ]
            market_context = "Current market prices in " + state + ":\n" + "\n".join(price_lines)
    except Exception as e:
        logger.warning("Market data fetch for crop rec failed: %s", e)

    # ── Gather matching schemes context ──
    scheme_context = ""
    try:
        from db import get_schemes_collection
        schemes_coll = get_schemes_collection()
        scheme_query = {
            "states": {"$in": [state, "All", "All India"]},
        }
        if season:
            scheme_query["$or"] = [
                {"season": season},
                {"season": "All"},
                {"season": ""},
                {"season": {"$exists": False}},
            ]
        schemes = list(schemes_coll.find(scheme_query, {"_id": 0, "scheme_name": 1, "crops": 1, "benefit": 1}).limit(20))
        if schemes:
            scheme_lines = []
            for s in schemes:
                crops_str = ", ".join(s.get("crops", [])[:5])
                scheme_lines.append(f"  {s.get('scheme_name', 'Unknown')}: for [{crops_str}] — {s.get('benefit', '')}")
            scheme_context = "\nAvailable government schemes:\n" + "\n".join(scheme_lines)
    except Exception as e:
        logger.warning("Scheme data fetch for crop rec failed: %s", e)

    # ── Build soil context ──
    soil_context = ""
    if soil_type:
        soil_context += f"Soil type: {soil_type}\n"
    if ph is not None:
        soil_context += f"Soil pH: {ph}\n"
    if not soil_context:
        soil_context = "Soil data: not provided (use general recommendations for the region)\n"

    prompt = f"""You are an expert agricultural advisor for Indian farmers. Based on the following information, recommend the top 5 most suitable and profitable crops.

FARMER DETAILS:
- State: {state}
- Season: {season}
- Land size: {land_size} hectares
- Water availability: {water_availability}

SOIL DATA:
{soil_context}

WEATHER:
{weather_context}

MARKET DATA:
{market_context}
{scheme_context}

Respond in {lang_name} with the following JSON structure ONLY (no markdown, no explanation outside JSON):
{{
    "recommendations": [
        {{
            "crop": "Rice",
            "suitability_score": 92,
            "expected_yield": "4.5 tonnes/hectare",
            "expected_revenue": "₹90,000/hectare",
            "investment_estimate": "₹35,000/hectare",
            "water_requirement": "High",
            "growth_duration": "120-150 days",
            "matching_schemes": ["PM-KISAN", "PMFBY"],
            "reasoning": "Short explanation of why this crop is recommended",
            "risk_factors": ["Flood risk in monsoon", "Pest susceptibility"],
            "tips": ["Use SRI method for better yield", "Apply DAP at sowing"]
        }}
    ],
    "general_advice": "Overall advice for the farmer based on conditions",
    "best_sowing_window": "Recommended sowing period for the top crop"
}}

suitability_score: 0-100 (100 = perfect match).
Rank by profitability × suitability. Be realistic with yield and revenue estimates for Indian conditions.
Include at least 5 crop recommendations."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 8192},
    }

    try:
        resp = requests.post(
            GEMINI_URL, params={"key": GEMINI_API_KEY},
            json=payload, timeout=45,
        )
        if resp.status_code != 200:
            logger.error("Gemini crop rec error %s: %s", resp.status_code, resp.text)
            return {"error": f"AI service returned status {resp.status_code}"}

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return {"error": "No response from AI model."}

        parts = candidates[0].get("content", {}).get("parts", [])
        # Gemini 2.5 Flash may return "thought" parts before the actual text.
        # Find the last non-thought text part.
        raw_text = ""
        for part in reversed(parts):
            if part.get("thought"):
                continue
            if part.get("text", "").strip():
                raw_text = part["text"]
                break
        if not raw_text:
            return {"error": "Empty response from AI model."}

        result = _clean_gemini_json(raw_text)

        # Validate structure
        if "recommendations" not in result or not isinstance(result["recommendations"], list):
            return {"error": "Invalid response structure from AI."}

        # Ensure each recommendation has required fields
        for rec in result["recommendations"]:
            rec.setdefault("crop", "Unknown")
            rec.setdefault("suitability_score", 50)
            rec.setdefault("expected_yield", "N/A")
            rec.setdefault("expected_revenue", "N/A")
            rec.setdefault("investment_estimate", "N/A")
            rec.setdefault("water_requirement", "Medium")
            rec.setdefault("growth_duration", "N/A")
            rec.setdefault("matching_schemes", [])
            rec.setdefault("reasoning", "")
            rec.setdefault("risk_factors", [])
            rec.setdefault("tips", [])

        result.setdefault("general_advice", "")
        result.setdefault("best_sowing_window", "")

        return result

    except json.JSONDecodeError as e:
        logger.error("Crop recommendation JSON parse error: %s", e)
        return {"error": "Failed to parse AI response."}
    except Exception as e:
        logger.error("Crop recommendation error: %s", e)
        return {"error": f"Recommendation failed: {e}"}
