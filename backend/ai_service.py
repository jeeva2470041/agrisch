"""
AgriScheme Backend — AI service.
Uses Google Gemini API (free tier) to answer farmer questions about schemes.
"""
import os
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


def _build_system_prompt(scheme_context: str) -> str:
    """Build the system-level instruction for the AI."""
    return (
        "You are an expert agricultural advisor for Indian farmers. "
        "You answer questions about Indian government agriculture schemes "
        "clearly and helpfully. Keep answers concise (3-5 sentences). "
        "Use simple language a farmer can understand. "
        "If the question is unrelated to the scheme or agriculture, "
        "politely redirect. Always mention concrete numbers (amounts, "
        "dates, percentages) when available.\n\n"
        f"--- SCHEME DETAILS ---\n{scheme_context}\n--- END ---"
    )


def ask_ai(question: str, scheme_context: str, language: str = "en") -> dict:
    """Send a question about a scheme to Gemini and return the answer.

    Args:
        question: The farmer's question.
        scheme_context: Stringified scheme data for context.
        language: Language code (en, hi, ta, ml).

    Returns:
        dict with 'answer' key on success, or 'error' key on failure.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured on the server."}

    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "ml": "Malayalam",
    }
    lang_name = lang_map.get(language, "English")

    system_prompt = _build_system_prompt(scheme_context)

    user_prompt = (
        f"Answer the following question in {lang_name}.\n\n"
        f"Question: {question}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt + "\n\n" + user_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
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
            logger.error("Gemini API error %s: %s", resp.status_code, resp.text)
            return {"error": f"AI service returned status {resp.status_code}"}

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return {"error": "No response from AI model."}

        parts = candidates[0].get("content", {}).get("parts", [])
        answer = parts[0].get("text", "") if parts else ""

        if not answer:
            return {"error": "Empty response from AI model."}

        return {"answer": answer.strip()}

    except requests.Timeout:
        logger.error("Gemini API timed out")
        return {"error": "AI service timed out. Please try again."}
    except Exception as exc:
        logger.error("Gemini API exception: %s", exc)
        return {"error": f"AI service error: {exc}"}
