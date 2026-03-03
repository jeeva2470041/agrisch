"""
AgriScheme Backend — Offline Voice NLP Parser.

Replaces Gemini API for parsing farmer voice transcripts into structured
form data (state, crop, land_size, season) using regex patterns, fuzzy
string matching, and unit-conversion rules.

Supports: English, Hindi (transliterated), Tamil, Malayalam keywords.
No API key, no network, no cost — instant response.

Dependencies: None beyond stdlib (re, difflib).
"""
import re
import logging
from difflib import get_close_matches

logger = logging.getLogger(__name__)

# ─── Valid Entities ────────────────────────────────────────────────────────

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

# ─── Multilingual Aliases (Hindi transliteration, Tamil, Malayalam) ────────
# Maps alias → canonical name (case-insensitive lookup)

CROP_ALIASES = {
    # Hindi / transliterated
    "chawal": "Rice", "dhan": "Rice", "dhaan": "Rice", "paddy": "Rice",
    "gehun": "Wheat", "gehu": "Wheat", "gandum": "Wheat",
    "kapas": "Cotton", "kapaas": "Cotton", "rui": "Cotton",
    "ganna": "Sugarcane", "ganne": "Sugarcane", "ikh": "Sugarcane",
    "dal": "Pulses", "daal": "Pulses", "moong": "Pulses",
    "chana": "Pulses", "arhar": "Pulses", "tur": "Pulses",
    "urad": "Pulses", "masoor": "Pulses", "lentil": "Pulses",
    "lentils": "Pulses",
    "sabzi": "Vegetables", "sabzee": "Vegetables", "tarkari": "Vegetables",
    "nariyal": "Coconut", "nariyel": "Coconut",
    "makka": "Maize", "makki": "Maize", "corn": "Maize", "bhutta": "Maize",
    "mungfali": "Groundnut", "moongfali": "Groundnut", "peanut": "Groundnut",
    "peanuts": "Groundnut",
    "soyabean": "Soybean", "soya": "Soybean",
    "paat": "Jute", "pat": "Jute",
    "chai": "Tea", "chay": "Tea",
    "masala": "Spices", "masale": "Spices",
    "phal": "Fruits", "phul": "Fruits", "fruit": "Fruits",
    "bajra": "Millets", "jowar": "Millets", "ragi": "Millets",
    "millet": "Millets", "bajri": "Millets", "nachni": "Millets",
    "til": "Oilseeds", "sarso": "Oilseeds", "sarson": "Oilseeds",
    "mustard": "Oilseeds", "sunflower": "Oilseeds", "sesame": "Oilseeds",
    "tambaku": "Tobacco", "tambaaku": "Tobacco",
    # Tamil
    "nel": "Rice", "arisi": "Rice",
    "gothumai": "Wheat", "kodumai": "Wheat",
    "paruthi": "Cotton",
    "karumbu": "Sugarcane",
    "karamani": "Pulses", "paruppu": "Pulses",
    "kaaikari": "Vegetables", "kaikari": "Vegetables",
    "thengai": "Coconut", "thenkai": "Coconut",
    "makka cholam": "Maize", "cholam": "Millets",
    "nilakadalai": "Groundnut", "verkadalai": "Groundnut",
    "thenai": "Millets", "kambu": "Millets", "varagu": "Millets",
    "ellu": "Oilseeds",
    "pazham": "Fruits",
    # Malayalam
    "ari": "Rice", "nellu": "Rice",
    "gothambu": "Wheat",
    "parutthi": "Cotton",
    "karimbu": "Sugarcane",
    "payar": "Pulses",
    "pachakkari": "Vegetables",
    "thenga": "Coconut",
    "kappalandi": "Groundnut",
    "raaagi": "Millets",
    "elluh": "Oilseeds",
    "palam": "Fruits",
}

STATE_ALIASES = {
    # Short / common names
    "ap": "Andhra Pradesh", "andhra": "Andhra Pradesh",
    "arunachal": "Arunachal Pradesh",
    "mp": "Madhya Pradesh", "madhya": "Madhya Pradesh",
    "up": "Uttar Pradesh", "uttar": "Uttar Pradesh",
    "hp": "Himachal Pradesh", "himachal": "Himachal Pradesh",
    "wb": "West Bengal", "bengal": "West Bengal", "bangla": "West Bengal",
    "tn": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "thamizhnadu": "Tamil Nadu",
    "tamilnad": "Tamil Nadu",
    "jk": "Jammu and Kashmir", "jammu": "Jammu and Kashmir",
    "kashmir": "Jammu and Kashmir",
    "cg": "Chhattisgarh", "chattisgarh": "Chhattisgarh",
    "uk": "Uttarakhand", "uttrakhand": "Uttarakhand",
    "ts": "Telangana",
    "rj": "Rajasthan",
    "mh": "Maharashtra",
    "ka": "Karnataka",
    "kl": "Kerala",
    "ga": "Goa",
    "hr": "Haryana",
    "pb": "Punjab", "panjab": "Punjab",
    "or": "Odisha", "orissa": "Odisha",
    "br": "Bihar",
    "jh": "Jharkhand", "jarkhand": "Jharkhand",
    "sk": "Sikkim",
    "tr": "Tripura",
    "mn": "Manipur",
    "ml": "Meghalaya",
    "mz": "Mizoram",
    "nl": "Nagaland",
    "dl": "Delhi",
    "pondy": "Puducherry", "pondicherry": "Puducherry",
    "daman": "Dadra and Nagar Haveli and Daman and Diu",
    "diu": "Dadra and Nagar Haveli and Daman and Diu",
    # Hindi / regional
    "tamilnaadu": "Tamil Nadu",
    "keralam": "Kerala", "kerela": "Kerala",
    "karnatak": "Karnataka",
    "maharashtr": "Maharashtra",
    "rajsthan": "Rajasthan",
    "gujrat": "Gujarat",
    "hariyana": "Haryana",
    "mahdya pradesh": "Madhya Pradesh",
}

SEASON_ALIASES = {
    # Hindi / regional
    "kharif": "Kharif", "khariff": "Kharif", "kharip": "Kharif",
    "monsoon": "Kharif", "sawan": "Kharif", "baarish": "Kharif",
    "varsha": "Kharif",
    "rabi": "Rabi", "rabbi": "Rabi", "ravi": "Rabi",
    "winter": "Rabi", "sardi": "Rabi", "thand": "Rabi",
    "zaid": "Zaid", "jayad": "Zaid", "zayad": "Zaid",
    "summer": "Zaid", "garmi": "Zaid", "grishma": "Zaid",
}

# ─── Land Size Patterns & Conversion ──────────────────────────────────────

# Unit → hectare multiplier
UNIT_TO_HECTARE = {
    "hectare": 1.0, "hectares": 1.0, "ha": 1.0,
    "acre": 0.4047, "acres": 0.4047, "acer": 0.4047, "aker": 0.4047,
    "bigha": 0.25, "bighas": 0.25, "beegha": 0.25,
    "gunta": 0.01012, "guntas": 0.01012, "guntha": 0.01012,
    "cent": 0.004047, "cents": 0.004047,
    "kanal": 0.0505, "kanals": 0.0505,
    "marla": 0.00505, "marlas": 0.00505,
    "katha": 0.0338, "kathas": 0.0338, "kattah": 0.0338,
    # Hindi
    "hektar": 1.0, "ekad": 0.4047, "ekad": 0.4047,
    "beegha": 0.25,
}

# Regex to capture number + optional unit
_LAND_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*'                          # number (int or float)
    r'(hectares?|ha|acres?|acer|aker|bighas?|'      # unit word
    r'beegha|guntas?|guntha|cents?|kanals?|marlas?|'
    r'kathas?|kattah|hektar|ekad'
    r')',
    re.IGNORECASE,
)

# Fallback: bare number after keywords like "land", "farm", "jamin"
_LAND_KEYWORD_PATTERN = re.compile(
    r'(?:land|farm|jamin|zamin|zameen|bhoomi|nilam|bhumi|khet|kheti)\s+'
    r'(?:is\s+|of\s+|size\s+|area\s+)?'
    r'(\d+(?:\.\d+)?)',
    re.IGNORECASE,
)

# ─── Main Parser ──────────────────────────────────────────────────────────


def _fuzzy_match(text: str, valid_list: list, cutoff: float = 0.6) -> str | None:
    """Find the closest match from valid_list using difflib."""
    matches = get_close_matches(text, valid_list, n=1, cutoff=cutoff)
    return matches[0] if matches else None


def _extract_state(text: str) -> tuple[str | None, float]:
    """Extract Indian state name from text.

    Returns (state_name, confidence).
    """
    text_lower = text.lower()

    # 1. Check exact matches (case-insensitive)
    for state in VALID_STATES:
        if state.lower() in text_lower:
            return state, 1.0

    # 2. Check aliases
    for alias, state in STATE_ALIASES.items():
        # Word boundary match to avoid partial matches
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text_lower):
            return state, 0.9

    # 3. Fuzzy match on individual words and word pairs
    words = text.split()
    # Try 2-word and 3-word combos (most states are 2 words)
    for size in (3, 2, 1):
        for i in range(len(words) - size + 1):
            chunk = " ".join(words[i:i + size])
            match = _fuzzy_match(chunk, VALID_STATES, cutoff=0.7)
            if match:
                return match, 0.7

    return None, 0.0


def _extract_crop(text: str) -> tuple[str | None, float]:
    """Extract crop name from text.

    Returns (crop_name, confidence).
    """
    text_lower = text.lower()

    # 1. Check exact matches
    for crop in VALID_CROPS:
        if crop.lower() in text_lower:
            return crop, 1.0

    # 2. Check aliases
    for alias, crop in CROP_ALIASES.items():
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text_lower):
            return crop, 0.9

    # 3. Fuzzy match
    words = text_lower.split()
    for word in words:
        if len(word) < 3:
            continue
        match = _fuzzy_match(word, [c.lower() for c in VALID_CROPS], cutoff=0.7)
        if match:
            # Map back to original casing
            idx = [c.lower() for c in VALID_CROPS].index(match)
            return VALID_CROPS[idx], 0.7

    return None, 0.0


def _extract_season(text: str) -> tuple[str | None, float]:
    """Extract growing season from text.

    Returns (season_name, confidence).
    """
    text_lower = text.lower()

    # 1. Check exact matches
    for season in VALID_SEASONS:
        if season.lower() in text_lower:
            return season, 1.0

    # 2. Check aliases
    for alias, season in SEASON_ALIASES.items():
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text_lower):
            return season, 0.9

    # 3. Month-based inference
    month_to_season = {
        "june": "Kharif", "july": "Kharif", "august": "Kharif",
        "september": "Kharif", "october": "Kharif",
        "november": "Rabi", "december": "Rabi", "january": "Rabi",
        "february": "Rabi", "march": "Rabi",
        "april": "Zaid", "may": "Zaid",
    }
    for month, season in month_to_season.items():
        if month in text_lower:
            return season, 0.8

    return None, 0.0


def _extract_land_size(text: str) -> tuple[float | None, float]:
    """Extract land size in hectares from text.

    Handles acres, bigha, gunta, cent, kanal, marla, katha conversions.
    Returns (hectares, confidence).
    """
    # 1. Number + unit pattern
    match = _LAND_PATTERN.search(text)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()
        multiplier = UNIT_TO_HECTARE.get(unit, 1.0)
        hectares = round(value * multiplier, 2)
        if 0.01 <= hectares <= 50000:
            return hectares, 1.0

    # 2. Keyword + number pattern (no unit — assume acres in Indian context)
    match2 = _LAND_KEYWORD_PATTERN.search(text)
    if match2:
        value = float(match2.group(1))
        # Default assumption: acres (most common in Indian farmer speech)
        hectares = round(value * 0.4047, 2)
        if 0.01 <= hectares <= 50000:
            return hectares, 0.7

    # 3. Look for standalone number near context words
    # Pattern: "I have 5 acres" or "5 acre khet"
    simple_match = re.search(
        r'(?:have|got|own|mere\s+pas|paas)\s+(\d+(?:\.\d+)?)',
        text, re.IGNORECASE,
    )
    if simple_match:
        value = float(simple_match.group(1))
        if 0.1 <= value <= 10000:
            # Assume acres
            return round(value * 0.4047, 2), 0.5

    return None, 0.0


def parse_voice_offline(transcript: str, language: str = "en") -> dict:
    """Parse farmer's voice transcript into structured data using local NLP.

    No API calls. Uses regex, aliases, and fuzzy matching.

    Args:
        transcript: Raw text from speech-to-text.
        language: Language code (en, hi, ta, ml) — used for confidence
                  adjustment (regional aliases are always checked).

    Returns:
        dict with: state, crop, land_size, season, confidence,
                   fields_extracted, analysis_method.
    """
    if not transcript or not transcript.strip():
        return {"error": "Empty transcript provided."}

    text = transcript.strip()
    logger.info("Voice NLP parsing (offline): '%s'", text[:200])

    state, state_conf = _extract_state(text)
    crop, crop_conf = _extract_crop(text)
    season, season_conf = _extract_season(text)
    land_size, land_conf = _extract_land_size(text)

    # Count extracted fields
    fields = {"state": state, "crop": crop, "land_size": land_size, "season": season}
    filled = sum(1 for v in fields.values() if v is not None)

    if filled == 0:
        return {"error": "Could not extract any information from the input."}

    # Overall confidence = weighted average of extracted field confidences
    confidences = []
    if state is not None:
        confidences.append(state_conf)
    if crop is not None:
        confidences.append(crop_conf)
    if season is not None:
        confidences.append(season_conf)
    if land_size is not None:
        confidences.append(land_conf)

    overall_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0

    result = {
        "state": state,
        "crop": crop,
        "land_size": land_size,
        "season": season,
        "confidence": overall_conf,
        "fields_extracted": filled,
        "analysis_method": "offline_nlp",
    }

    logger.info("Voice NLP result: %s", result)
    return result
