"""
AgriScheme Backend — Soil Health Analysis Service.
Uses offline color analysis (primary) for soil images, with optional
Gemini Vision fallback. Manual soil test analysis uses ICAR rule engine.
"""
import os
import base64
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

MAX_IMAGE_SIZE = 4 * 1024 * 1024  # 4 MB

# Choose image analysis mode: "offline" (default) | "gemini" | "hybrid"
# "offline"  — uses color analysis only (fast, free, no API needed)
# "gemini"   — uses Gemini Vision only (needs API key + network)
# "hybrid"   — tries offline first; falls back to Gemini on low confidence
IMAGE_ANALYSIS_MODE = os.getenv("SOIL_IMAGE_MODE", "offline").lower()


def _clean_gemini_json(raw_text: str) -> dict:
    """Parse Gemini response text into a dict, handling markdown fences,
    thinking blocks, and truncated JSON."""
    import re
    cleaned = raw_text.strip()

    # Remove markdown code fences
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

    # Truncation repair
    cleaned = re.sub(r',\s*"[^"]*$', '', cleaned)
    cleaned = re.sub(r':\s*"[^"]*$', ': ""', cleaned)
    cleaned = re.sub(r',\s*"[^"]*"\s*:\s*"[^"]*$', '', cleaned)
    cleaned = re.sub(r',\s*"[^"]*"\s*:\s*\[[^\]]*$', '', cleaned)
    cleaned = re.sub(r',\s*\{[^}]*$', '', cleaned)
    cleaned = cleaned.rstrip().rstrip(',')

    open_braces = cleaned.count("{") - cleaned.count("}")
    open_brackets = cleaned.count("[") - cleaned.count("]")
    cleaned += "]" * max(0, open_brackets)
    cleaned += "}" * max(0, open_braces)

    return json.loads(cleaned)


def _analyze_soil_image_gemini(image_base64: str, language: str = "en") -> dict:
    """Analyze a soil image using Gemini Vision (API-based fallback)."""
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured on the server."}

    try:
        raw_bytes = base64.b64decode(image_base64)
    except Exception:
        return {"error": "Invalid base64 image data."}

    # Detect MIME type
    mime_type = "image/jpeg"
    if raw_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        mime_type = "image/png"
    elif raw_bytes[:4] == b'RIFF' and raw_bytes[8:12] == b'WEBP':
        mime_type = "image/webp"

    lang_map = {"en": "English", "hi": "Hindi", "ta": "Tamil", "ml": "Malayalam"}
    lang_name = lang_map.get(language, "English")

    system_prompt = f"""You are an expert soil scientist and agronomist. Analyze the soil image provided.

Respond in {lang_name} with the following JSON structure ONLY (no markdown, no explanation outside JSON):
{{
    "soil_type": "Clay / Loam / Sandy / Silt / Clay Loam / Sandy Loam / Laterite / Black Cotton / Red / Alluvial",
    "ph_estimate": 6.5,
    "organic_matter": "Low / Medium / High",
    "moisture_level": "Dry / Moderate / Wet / Waterlogged",
    "drainage": "Poor / Moderate / Good / Excellent",
    "color_analysis": "Brief description of soil color and what it indicates",
    "texture_analysis": "Brief description of soil texture",
    "health_score": 7,
    "deficiencies": ["Nitrogen", "Phosphorus"],
    "recommendations": [
        "Apply 50kg/hectare of Urea for nitrogen supplementation",
        "Add organic compost at 2 tonnes/hectare"
    ],
    "suitable_crops": ["Rice", "Wheat", "Sugarcane"],
    "confidence": 0.75
}}

health_score should be 1-10 (10 = excellent).
If the image is not soil, return health_score=0 and appropriate error in color_analysis."""

    payload = {
        "contents": [{
            "parts": [
                {"text": system_prompt},
                {"inline_data": {"mime_type": mime_type, "data": image_base64}},
            ]
        }],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
    }

    try:
        resp = requests.post(
            GEMINI_URL, params={"key": GEMINI_API_KEY},
            json=payload, timeout=30,
        )
        if resp.status_code != 200:
            logger.error("Gemini soil vision error %s: %s", resp.status_code, resp.text)
            return {"error": f"AI service returned status {resp.status_code}"}

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return {"error": "No response from AI model."}

        parts = candidates[0].get("content", {}).get("parts", [])
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
        result.setdefault("soil_type", "Unknown")
        result.setdefault("ph_estimate", 7.0)
        result.setdefault("organic_matter", "Medium")
        result.setdefault("moisture_level", "Moderate")
        result.setdefault("drainage", "Moderate")
        result.setdefault("color_analysis", "")
        result.setdefault("texture_analysis", "")
        result.setdefault("health_score", 5)
        result.setdefault("deficiencies", [])
        result.setdefault("recommendations", [])
        result.setdefault("suitable_crops", [])
        result.setdefault("confidence", 0.5)
        result["analysis_method"] = "gemini_vision"
        return result

    except json.JSONDecodeError as e:
        logger.error("Soil analysis JSON parse error: %s", e)
        return {"error": "Failed to parse AI response."}
    except Exception as e:
        logger.error("Soil analysis error: %s", e)
        return {"error": f"Analysis failed: {e}"}


def analyze_soil_image(image_base64: str, language: str = "en") -> dict:
    """Analyze a soil image.

    Mode is controlled by SOIL_IMAGE_MODE env var (default: 'offline'):
      - 'offline': Color-based analysis (fast, free, works without API)
      - 'gemini':  Gemini Vision API (needs key + network)
      - 'hybrid':  Tries offline first; if confidence < 0.40, falls back to Gemini

    Args:
        image_base64: Base64-encoded soil image (JPEG/PNG/WEBP).
        language: Language code (en, hi, ta, ml).

    Returns:
        dict with soil analysis results or 'error' key.
    """
    if not image_base64:
        return {"error": "No image provided."}

    try:
        raw_bytes = base64.b64decode(image_base64)
        if len(raw_bytes) > MAX_IMAGE_SIZE:
            return {"error": "Image too large. Maximum 4MB allowed."}
    except Exception:
        return {"error": "Invalid base64 image data."}

    # --- Gemini-only mode ---
    if IMAGE_ANALYSIS_MODE == "gemini":
        return _analyze_soil_image_gemini(image_base64, language)

    # --- Offline color analysis ---
    from services.soil_image_analyzer import analyze_soil_from_image

    offline_result = analyze_soil_from_image(image_base64)
    if "error" in offline_result:
        logger.warning("Offline image analysis failed: %s", offline_result["error"])
        # Try Gemini as fallback if available
        if GEMINI_API_KEY:
            logger.info("Falling back to Gemini Vision")
            return _analyze_soil_image_gemini(image_base64, language)
        return offline_result

    # --- Hybrid mode: check confidence ---
    if IMAGE_ANALYSIS_MODE == "hybrid":
        confidence = offline_result.get("confidence", 0)
        if confidence < 0.40 and GEMINI_API_KEY:
            logger.info(
                "Offline confidence %.2f < 0.40 — upgrading to Gemini Vision",
                confidence,
            )
            gemini_result = _analyze_soil_image_gemini(image_base64, language)
            if "error" not in gemini_result:
                return gemini_result
            # If Gemini also fails, return offline result anyway
            logger.warning("Gemini fallback failed, using offline result")

    return offline_result


def analyze_soil_manual(soil_data: dict, language: str = "en") -> dict:
    """Analyze soil from manual test report values using ICAR rule-based engine.

    This replaces the previous Gemini API call with a deterministic,
    offline rule-based analysis based on ICAR standards.
    No API key or network connectivity required.

    Args:
        soil_data: dict with keys: ph, nitrogen, phosphorus, potassium,
                   organic_carbon, soil_type (all optional but at least one required).
        language: Language code (unused — rules return English; translation
                  can be added later if needed).

    Returns:
        dict with soil analysis results or 'error' key.
    """
    from services.soil_rules_engine import analyze_soil_rulebased

    if not soil_data:
        return {"error": "No soil data provided."}

    # Validate and convert numeric fields
    numeric_fields = ["ph", "nitrogen", "phosphorus", "potassium", "organic_carbon"]
    cleaned = {}
    for key in numeric_fields:
        if key in soil_data and soil_data[key] is not None:
            try:
                cleaned[key] = float(soil_data[key])
            except (ValueError, TypeError):
                return {"error": f"Invalid value for {key}: must be a number."}

    if "soil_type" in soil_data and soil_data["soil_type"]:
        cleaned["soil_type"] = str(soil_data["soil_type"])

    if not cleaned:
        return {"error": "At least one soil parameter is required."}

    return analyze_soil_rulebased(cleaned)
