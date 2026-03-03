"""
AgriScheme Backend — Crop Disease Detection Service.
Uses Google Gemini Vision API to analyze plant images and detect
diseases, providing treatment recommendations.

Supports image analysis via base64-encoded images.
"""
import os
import base64
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

# Max image size: 4MB
MAX_IMAGE_SIZE = 4 * 1024 * 1024


def detect_disease(image_base64: str, crop_hint: str = "",
                   language: str = "en") -> dict:
    """Analyze a plant image to detect diseases.

    Args:
        image_base64: Base64-encoded image data (JPEG/PNG).
        crop_hint: Optional crop name to improve accuracy.
        language: Language code for the response (en, hi, ta, ml).

    Returns:
        dict with disease info, or 'error' key on failure.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured on the server."}

    if not image_base64:
        return {"error": "No image provided."}

    # Validate base64 size
    try:
        raw_bytes = base64.b64decode(image_base64)
        if len(raw_bytes) > MAX_IMAGE_SIZE:
            return {"error": "Image too large. Maximum 4MB allowed."}
    except Exception:
        return {"error": "Invalid base64 image data."}

    # Detect MIME type from header bytes
    mime_type = "image/jpeg"
    if raw_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        mime_type = "image/png"
    elif raw_bytes[:2] == b'\xff\xd8':
        mime_type = "image/jpeg"
    elif raw_bytes[:4] == b'RIFF' and raw_bytes[8:12] == b'WEBP':
        mime_type = "image/webp"

    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "ml": "Malayalam",
    }
    lang_name = lang_map.get(language, "English")

    crop_context = f"The farmer says this is a {crop_hint} plant. " if crop_hint else ""

    system_prompt = f"""You are an expert agricultural plant pathologist. Analyze the image of a plant/leaf and detect any diseases.

{crop_context}

Respond in {lang_name} with the following JSON structure ONLY (no markdown, no explanation outside JSON):
{{
    "is_healthy": true/false,
    "disease_name": "name of the disease or 'Healthy'",
    "confidence": 0.0 to 1.0,
    "description": "Brief description of the disease",
    "symptoms": ["symptom1", "symptom2", "symptom3"],
    "treatment": ["treatment step 1", "treatment step 2", "treatment step 3"],
    "prevention": ["prevention tip 1", "prevention tip 2"],
    "severity": "mild/moderate/severe",
    "crop_identified": "identified crop name"
}}

If the image is not a plant or is unclear, still return the JSON with is_healthy=null and appropriate error in description."""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_base64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        },
    }

    try:
        resp = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30,
        )

        if resp.status_code != 200:
            logger.error("Gemini Vision error %s: %s", resp.status_code, resp.text)
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

        # Clean markdown code fences if present
        import json
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        # Fix truncated JSON — balance braces/brackets and strip trailing garbage
        open_braces = cleaned.count("{") - cleaned.count("}")
        open_brackets = cleaned.count("[") - cleaned.count("]")
        # If truncated mid-string, close the string first
        if open_braces > 0 or open_brackets > 0:
            # Remove trailing incomplete key-value (after last comma or colon)
            import re
            # Strip incomplete trailing string/value
            cleaned = re.sub(r',\s*"[^"]*"?\s*:?\s*"?[^"{}\[\]]*$', '', cleaned)
            open_braces = cleaned.count("{") - cleaned.count("}")
            open_brackets = cleaned.count("[") - cleaned.count("]")
            cleaned += "]" * max(0, open_brackets)
            cleaned += "}" * max(0, open_braces)

        result = json.loads(cleaned)
        logger.info("Disease detection result: %s", json.dumps(result, ensure_ascii=False)[:500])

        # Ensure required fields
        result.setdefault("is_healthy", None)
        result.setdefault("disease_name", "Unknown")
        result.setdefault("confidence", 0.5)
        result.setdefault("description", "")
        result.setdefault("symptoms", [])
        result.setdefault("treatment", [])
        result.setdefault("prevention", [])
        result.setdefault("severity", "unknown")
        result.setdefault("crop_identified", crop_hint or "Unknown")

        return result

    except Exception as e:
        logger.error("Disease detection error: %s", e)
        return {"error": f"Analysis failed: {e}"}
