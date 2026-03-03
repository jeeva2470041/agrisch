"""
AgriScheme Backend — Voice NLP Service.
Parses natural language voice input from farmers into structured form data
(state, crop, land_size, season) using offline regex + fuzzy matching.

Optional Gemini fallback available via VOICE_NLP_MODE env var.
"""
import os
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

# Mode: "offline" (default) | "gemini" | "hybrid"
# offline — regex + fuzzy (fast, free, no API)
# gemini  — Gemini API only
# hybrid  — offline first; Gemini fallback if < 2 fields extracted
VOICE_NLP_MODE = os.getenv("VOICE_NLP_MODE", "offline").lower()

# Valid values kept here for Gemini fallback prompt
VALID_CROPS = [
    "Rice", "Wheat", "Cotton", "Sugarcane", "Pulses", "Vegetables",
    "Coconut", "Maize", "Groundnut", "Soybean", "Jute", "Tea",
    "Coffee", "Spices", "Fruits", "Millets", "Oilseeds", "Tobacco",
]

VALID_SEASONS = ["Kharif", "Rabi", "Zaid"]

VALID_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]


def _parse_voice_gemini(transcript: str, language: str = "en") -> dict:
    """Parse voice input using Gemini API (fallback)."""
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured on the server."}

    lang_map = {"en": "English", "hi": "Hindi", "ta": "Tamil", "ml": "Malayalam"}
    lang_name = lang_map.get(language, "English")

    system_prompt = f"""You are an NLP parser for an Indian agriculture app. Extract structured data from the farmer's spoken input.

VALID CROPS: {json.dumps(VALID_CROPS)}
VALID SEASONS: {json.dumps(VALID_SEASONS)}
VALID STATES: {json.dumps(VALID_STATES)}

RULES:
1. Extract: state, crop, land_size (in hectares as a number), season
2. Match to the CLOSEST valid value from the lists above
3. For land_size: convert acres to hectares (1 acre = 0.4047 ha), bigha to hectares (1 bigha ≈ 0.25 ha)
4. If a field cannot be determined, set it to null
5. Return ONLY valid JSON, no markdown, no explanation

OUTPUT FORMAT (strict JSON):
{{"state": "string or null", "crop": "string or null", "land_size": number_or_null, "season": "string or null", "confidence": 0.0_to_1.0}}"""

    user_prompt = (
        f"The farmer spoke in {lang_name}. Parse the following:\n\n"
        f'"{transcript}"'
    )

    payload = {
        "contents": [
            {"parts": [{"text": system_prompt + "\n\n" + user_prompt}]}
        ],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
    }

    try:
        resp = requests.post(
            GEMINI_URL, params={"key": GEMINI_API_KEY},
            json=payload, timeout=15,
        )
        if resp.status_code != 200:
            logger.error("Gemini NLP error %s: %s", resp.status_code, resp.text)
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

        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        open_braces = cleaned.count("{") - cleaned.count("}")
        open_brackets = cleaned.count("[") - cleaned.count("]")
        cleaned += "]" * max(0, open_brackets)
        cleaned += "}" * max(0, open_braces)

        parsed = json.loads(cleaned)
        logger.info("Gemini voice NLP: %s", json.dumps(parsed, ensure_ascii=False))

        result = {
            "state": None, "crop": None, "land_size": None,
            "season": None, "confidence": 0.0,
        }
        if parsed.get("state") in VALID_STATES:
            result["state"] = parsed["state"]
        if parsed.get("crop") in VALID_CROPS:
            result["crop"] = parsed["crop"]
        if parsed.get("season") in VALID_SEASONS:
            result["season"] = parsed["season"]
        if parsed.get("land_size") is not None:
            try:
                ls = float(parsed["land_size"])
                if 0.1 <= ls <= 10000:
                    result["land_size"] = round(ls, 1)
            except (ValueError, TypeError):
                pass
        if parsed.get("confidence") is not None:
            try:
                result["confidence"] = min(1.0, max(0.0, float(parsed["confidence"])))
            except (ValueError, TypeError):
                result["confidence"] = 0.5

        filled = sum(1 for k in ["state", "crop", "land_size", "season"]
                     if result[k] is not None)
        if filled == 0:
            return {"error": "Could not extract any information from the input."}
        result["fields_extracted"] = filled
        result["analysis_method"] = "gemini"
        return result

    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s — raw: %s", e, raw_text[:200])
        return {"error": "Could not parse AI response."}
    except requests.RequestException as e:
        logger.error("Request error: %s", e)
        return {"error": "Failed to connect to AI service."}
    except Exception as e:
        logger.error("Voice NLP error: %s", e)
        return {"error": f"Internal error: {e}"}


def parse_voice_input(transcript: str, language: str = "en") -> dict:
    """Parse natural language voice input into structured farmer data.

    Mode controlled by VOICE_NLP_MODE env var (default: 'offline'):
      - 'offline': Regex + fuzzy matching (instant, free, works without API)
      - 'gemini':  Gemini API only (needs key + network)
      - 'hybrid':  Offline first; if < 2 fields extracted, tries Gemini

    Args:
        transcript: Raw text from speech-to-text.
        language: Language code (en, hi, ta, ml).

    Returns:
        dict with extracted fields: state, crop, land_size, season, confidence.
        On error, returns dict with 'error' key.
    """
    if not transcript or not transcript.strip():
        return {"error": "Empty transcript provided."}

    # --- Gemini-only mode ---
    if VOICE_NLP_MODE == "gemini":
        return _parse_voice_gemini(transcript, language)

    # --- Offline parsing ---
    from services.voice_nlp_parser import parse_voice_offline

    offline_result = parse_voice_offline(transcript, language)

    if "error" in offline_result and VOICE_NLP_MODE != "offline":
        # Offline failed entirely — try Gemini in hybrid mode
        if GEMINI_API_KEY:
            logger.info("Offline NLP failed, falling back to Gemini")
            return _parse_voice_gemini(transcript, language)
        return offline_result

    if "error" in offline_result:
        return offline_result

    # --- Hybrid mode: check if enough fields extracted ---
    if VOICE_NLP_MODE == "hybrid":
        filled = offline_result.get("fields_extracted", 0)
        if filled < 2 and GEMINI_API_KEY:
            logger.info(
                "Offline extracted only %d field(s) — trying Gemini for better results",
                filled,
            )
            gemini_result = _parse_voice_gemini(transcript, language)
            if "error" not in gemini_result:
                gemini_filled = gemini_result.get("fields_extracted", 0)
                if gemini_filled > filled:
                    return gemini_result
            # Gemini didn't do better, keep offline result
            logger.info("Gemini didn't improve extraction, keeping offline result")

    return offline_result
