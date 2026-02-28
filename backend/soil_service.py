"""
AgriScheme Backend — Soil Health Analysis Service.
Uses Google Gemini Vision API to analyze soil images and manual soil test data
to provide health assessments, deficiency detection, and fertilizer recommendations.
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


def analyze_soil_image(image_base64: str, language: str = "en") -> dict:
    """Analyze a soil image using Gemini Vision.

    Args:
        image_base64: Base64-encoded soil image (JPEG/PNG).
        language: Language code (en, hi, ta, ml).

    Returns:
        dict with soil analysis results or 'error' key.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured on the server."}
    if not image_base64:
        return {"error": "No image provided."}

    try:
        raw_bytes = base64.b64decode(image_base64)
        if len(raw_bytes) > MAX_IMAGE_SIZE:
            return {"error": "Image too large. Maximum 4MB allowed."}
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
        # Gemini 2.5 Flash may return "thought" parts before actual text.
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

        # Ensure required fields
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

        return result

    except json.JSONDecodeError as e:
        logger.error("Soil analysis JSON parse error: %s", e)
        return {"error": "Failed to parse AI response."}
    except Exception as e:
        logger.error("Soil analysis error: %s", e)
        return {"error": f"Analysis failed: {e}"}


def analyze_soil_manual(soil_data: dict, language: str = "en") -> dict:
    """Analyze soil from manual test report values using Gemini.

    Args:
        soil_data: dict with keys: ph, nitrogen, phosphorus, potassium,
                   organic_carbon, soil_type (all optional but at least one required).
        language: Language code.

    Returns:
        dict with soil analysis results or 'error' key.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured on the server."}

    lang_map = {"en": "English", "hi": "Hindi", "ta": "Tamil", "ml": "Malayalam"}
    lang_name = lang_map.get(language, "English")

    # Build context from provided values
    context_parts = []
    if "ph" in soil_data:
        context_parts.append(f"pH: {soil_data['ph']}")
    if "nitrogen" in soil_data:
        context_parts.append(f"Nitrogen (N): {soil_data['nitrogen']} kg/hectare")
    if "phosphorus" in soil_data:
        context_parts.append(f"Phosphorus (P): {soil_data['phosphorus']} kg/hectare")
    if "potassium" in soil_data:
        context_parts.append(f"Potassium (K): {soil_data['potassium']} kg/hectare")
    if "organic_carbon" in soil_data:
        context_parts.append(f"Organic Carbon: {soil_data['organic_carbon']}%")
    if "soil_type" in soil_data:
        context_parts.append(f"Soil Type: {soil_data['soil_type']}")

    if not context_parts:
        return {"error": "At least one soil parameter is required."}

    soil_context = "\n".join(context_parts)

    prompt = f"""You are an expert soil scientist and agronomist. A farmer has provided the following soil test report values:

{soil_context}

Based on these values, provide a comprehensive soil health analysis.

Respond in {lang_name} with the following JSON structure ONLY (no markdown, no explanation outside JSON):
{{
    "soil_type": "identified or confirmed soil type",
    "ph_estimate": {soil_data.get('ph', 7.0)},
    "organic_matter": "Low / Medium / High",
    "moisture_level": "Cannot determine from test data",
    "drainage": "estimated based on soil type",
    "color_analysis": "Description based on soil type and nutrient levels",
    "texture_analysis": "Description based on soil type",
    "health_score": 7,
    "deficiencies": ["list of nutrient deficiencies identified"],
    "recommendations": [
        "specific fertilizer recommendation with quantity per hectare",
        "soil amendment suggestions"
    ],
    "suitable_crops": ["crops suitable for this soil"],
    "confidence": 0.85,
    "npk_status": {{
        "nitrogen": "Low / Medium / High",
        "phosphorus": "Low / Medium / High",
        "potassium": "Low / Medium / High"
    }}
}}

health_score: 1-10 (10 = excellent). Be specific with fertilizer quantities."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
    }

    try:
        resp = requests.post(
            GEMINI_URL, params={"key": GEMINI_API_KEY},
            json=payload, timeout=30,
        )
        if resp.status_code != 200:
            logger.error("Gemini soil manual error %s: %s", resp.status_code, resp.text)
            return {"error": f"AI service returned status {resp.status_code}"}

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return {"error": "No response from AI model."}

        parts = candidates[0].get("content", {}).get("parts", [])
        # Gemini 2.5 Flash may return "thought" parts before actual text.
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

        result.setdefault("soil_type", soil_data.get("soil_type", "Unknown"))
        result.setdefault("ph_estimate", soil_data.get("ph", 7.0))
        result.setdefault("organic_matter", "Medium")
        result.setdefault("health_score", 5)
        result.setdefault("deficiencies", [])
        result.setdefault("recommendations", [])
        result.setdefault("suitable_crops", [])
        result.setdefault("confidence", 0.7)

        return result

    except json.JSONDecodeError as e:
        logger.error("Soil manual analysis JSON parse error: %s", e)
        return {"error": "Failed to parse AI response."}
    except Exception as e:
        logger.error("Soil manual analysis error: %s", e)
        return {"error": f"Analysis failed: {e}"}
