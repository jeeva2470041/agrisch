"""
AgriScheme Backend — API routes.
Implements the eligibility matching engine and scheme management endpoints.
"""
import re
import logging
from flask import Blueprint, request, jsonify
from db import get_schemes_collection
from config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from weather_service import get_weather
from market_service import get_market_prices
from ai_service import ask_ai
from voice_nlp_service import parse_voice_input
from ranking_service import rank_schemes
from forecast_service import get_price_forecast
from disease_service import detect_disease
from yield_service import predict_yield

api_bp = Blueprint("api", __name__)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Input sanitisation helpers
# ---------------------------------------------------------------------------
_SAFE_STRING = re.compile(r"^[\w\s\-\.,()/&']+$", re.UNICODE)


def _sanitize_string(value, field_name, max_len=100):
    """Validate and sanitise a string input.

    Raises ValueError with a user-friendly message.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} is required")
    if len(value) > max_len:
        raise ValueError(f"{field_name} exceeds maximum length of {max_len}")
    if not _SAFE_STRING.match(value):
        raise ValueError(f"{field_name} contains invalid characters")
    # Prevent NoSQL injection — reject dict / operator-like values
    if value.startswith("$"):
        raise ValueError(f"{field_name} contains invalid characters")
    return value


def _sanitize_number(value, field_name, min_val=0, max_val=10000):
    """Validate and sanitise a numeric input."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number")
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    if value < min_val or value > max_val:
        raise ValueError(f"{field_name} must be between {min_val} and {max_val}")
    return float(value)


def _parse_benefit_amount(benefit_str):
    """Extract a numeric value from a benefit string for sorting.

    Examples:
        '₹6,000 per year'   → 6000
        'Up to ₹2,00,000'   → 200000
        'Comprehensive ...'  → 0
    """
    if not benefit_str:
        return 0
    nums = re.findall(r"[\d,]+", str(benefit_str).replace(",", ""))
    if nums:
        try:
            return float(nums[0].replace(",", ""))
        except ValueError:
            pass
    return 0


# ---------------------------------------------------------------------------
# POST /api/getEligibleSchemes  —  Eligibility Matching Engine
# ---------------------------------------------------------------------------
@api_bp.route("/getEligibleSchemes", methods=["POST"])
def get_eligible_schemes():
    """Rule-based eligibility matching.

    Rules:
        1. State must match OR scheme supports "All"
        2. Crop  must match OR scheme supports "All"
        3. land_size must be between min_land and max_land
        4. Season must match if applicable (or scheme has no season restriction)

    Returns eligible schemes sorted by benefit_amount (highest first).
    """
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        # --- Validate required fields ---
        try:
            state = _sanitize_string(data.get("state", ""), "state")
            crop = _sanitize_string(data.get("crop", ""), "crop")
            land_size = _sanitize_number(data.get("land_size"), "land_size")
        except (ValueError, TypeError) as e:
            return jsonify({"error": str(e)}), 400

        # --- Optional fields ---
        season = None
        if "season" in data and data["season"]:
            try:
                season = _sanitize_string(data["season"], "season")
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        # --- Build MongoDB query ---
        query = {
            "states": {"$in": [state, "All", "All India"]},
            "crops": {"$in": [crop, "All", "All Crops"]},
            "min_land": {"$lte": land_size},
            "max_land": {"$gte": land_size},
        }

        # Season filter: match if scheme season equals input OR scheme has no
        # season restriction (empty / "All" / missing)
        if season:
            query["$or"] = [
                {"season": season},
                {"season": "All"},
                {"season": ""},
                {"season": {"$exists": False}},
            ]

        # --- Projection (only necessary fields) ---
        projection = {
            "_id": 0,
            "scheme_name": 1,
            "type": 1,
            "benefit": 1,
            "benefit_amount": 1,
            "states": 1,
            "crops": 1,
            "season": 1,
            "min_land": 1,
            "max_land": 1,
            "documents_required": 1,
            "official_link": 1,
            "description": 1,
        }

        # --- Pagination ---
        page = max(1, int(request.args.get("page", 1)))
        limit = min(int(request.args.get("limit", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
        skip = (page - 1) * limit

        # --- Execute query (sorted by benefit_amount descending) ---
        schemes_collection = get_schemes_collection()
        cursor = (
            schemes_collection.find(query, projection)
            .sort("benefit_amount", -1)
            .skip(skip)
            .limit(limit)
        )
        schemes = list(cursor)

        # Total count for pagination metadata
        total = schemes_collection.count_documents(query)

        # --- Smart Ranking: TF-IDF + Cosine Similarity ---
        if len(schemes) > 1:
            try:
                schemes = rank_schemes(schemes, state, crop, land_size, season or "All")
            except Exception as rank_err:
                logger.warning("Ranking fallback: %s", rank_err)

        return jsonify({
            "success": True,
            "count": len(schemes),
            "total": total,
            "page": page,
            "limit": limit,
            "schemes": schemes,
        })

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# GET /api/schemes  —  List all schemes (paginated)
# ---------------------------------------------------------------------------
@api_bp.route("/schemes", methods=["GET"])
def list_schemes():
    """Return all schemes with optional type filter and pagination."""
    try:
        schemes_collection = get_schemes_collection()

        query = {}
        scheme_type = request.args.get("type")
        if scheme_type:
            try:
                scheme_type = _sanitize_string(scheme_type, "type")
                query["type"] = scheme_type
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        projection = {"_id": 0}

        page = max(1, int(request.args.get("page", 1)))
        limit = min(int(request.args.get("limit", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
        skip = (page - 1) * limit

        cursor = (
            schemes_collection.find(query, projection)
            .sort("benefit_amount", -1)
            .skip(skip)
            .limit(limit)
        )

        total = schemes_collection.count_documents(query)

        return jsonify({
            "success": True,
            "count": total,
            "page": page,
            "limit": limit,
            "schemes": list(cursor),
        })

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# POST /api/addScheme  —  Add a new scheme (admin)
# ---------------------------------------------------------------------------
@api_bp.route("/addScheme", methods=["POST"])
def add_scheme():
    """Insert a new scheme document (basic admin endpoint)."""
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        # Required fields
        required = ["scheme_name", "type", "states", "crops", "min_land", "max_land", "benefit"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # Sanitise key fields
        data["scheme_name"] = _sanitize_string(data["scheme_name"], "scheme_name", max_len=200)
        data["type"] = _sanitize_string(data["type"], "type")
        data["min_land"] = _sanitize_number(data["min_land"], "min_land")
        data["max_land"] = _sanitize_number(data["max_land"], "max_land")

        if not isinstance(data["states"], list):
            return jsonify({"error": "states must be a list"}), 400
        if not isinstance(data["crops"], list):
            return jsonify({"error": "crops must be a list"}), 400

        # Compute benefit_amount for sorting if not provided
        if "benefit_amount" not in data:
            data["benefit_amount"] = _parse_benefit_amount(data.get("benefit", ""))

        schemes_collection = get_schemes_collection()
        schemes_collection.insert_one(data)

        return jsonify({"message": "Scheme added successfully"}), 201

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# GET /api/weather  —  Weather forecast (Open-Meteo proxy)
# ---------------------------------------------------------------------------
@api_bp.route("/weather", methods=["GET"])
def weather():
    """Return current weather + 5-day forecast for given coordinates."""
    try:
        lat = request.args.get("lat")
        lon = request.args.get("lon")

        if not lat or not lon:
            return jsonify({"error": "lat and lon query parameters are required"}), 400

        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            return jsonify({"error": "lat and lon must be valid numbers"}), 400

        # Validate range
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({"error": "lat must be -90..90, lon must be -180..180"}), 400

        result = get_weather(lat, lon)
        if result is None:
            return jsonify({"error": "Failed to fetch weather data"}), 502

        return jsonify({"success": True, **result})

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# GET /api/market-prices  —  Crop market prices
# ---------------------------------------------------------------------------
@api_bp.route("/market-prices", methods=["GET"])
def market_prices():
    """Return market prices for crops in a given state."""
    try:
        state = request.args.get("state", "All")
        crop = request.args.get("crop")

        if len(state) > 100:
            return jsonify({"error": "state parameter too long"}), 400

        result = get_market_prices(state, crop)
        return jsonify({"success": True, **result})

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# POST /api/ask-ai  —  AI-powered scheme Q&A
# ---------------------------------------------------------------------------
@api_bp.route("/ask-ai", methods=["POST"])
def ask_ai_endpoint():
    """Answer a farmer's question about a specific scheme using AI.

    Expects JSON body:
        question       (str, required) — the farmer's question
        scheme_context (str, required) — stringified scheme info for context
        language       (str, optional) — locale code (en/hi/ta/ml), default en
    """
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        question = (data.get("question") or "").strip()
        scheme_context = (data.get("scheme_context") or "").strip()
        language = (data.get("language") or "en").strip()

        if not question:
            return jsonify({"error": "question is required"}), 400
        if len(question) > 500:
            return jsonify({"error": "question is too long (max 500 chars)"}), 400
        if not scheme_context:
            return jsonify({"error": "scheme_context is required"}), 400
        if len(scheme_context) > 5000:
            return jsonify({"error": "scheme_context is too long"}), 400

        result = ask_ai(question, scheme_context, language)

        if "error" in result:
            return jsonify({"success": False, **result}), 502

        return jsonify({"success": True, **result})

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# POST /api/parse-voice-input  —  Voice NLP (STT + Gemini)
# ---------------------------------------------------------------------------
@api_bp.route("/parse-voice-input", methods=["POST"])
def parse_voice():
    """Parse natural language voice input into structured farmer data.

    Expects JSON body:
        transcript  (str, required) — raw text from speech-to-text
        language    (str, optional) — locale code (en/hi/ta/ml), default en
    """
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        transcript = (data.get("transcript") or "").strip()
        language = (data.get("language") or "en").strip()

        if not transcript:
            return jsonify({"error": "transcript is required"}), 400
        if len(transcript) > 1000:
            return jsonify({"error": "transcript is too long (max 1000 chars)"}), 400

        result = parse_voice_input(transcript, language)

        if "error" in result:
            return jsonify({"success": False, **result}), 400

        return jsonify({"success": True, **result})

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# GET /api/price-forecast  —  Market Price Forecasting (Prophet)
# ---------------------------------------------------------------------------
@api_bp.route("/price-forecast", methods=["GET"])
def price_forecast():
    """Return 7-day price forecast for a crop.

    Query params:
        crop (str, required) — crop name
    """
    try:
        crop = request.args.get("crop", "").strip()
        if not crop:
            return jsonify({"error": "crop query parameter is required"}), 400
        if len(crop) > 50:
            return jsonify({"error": "crop parameter too long"}), 400

        result = get_price_forecast(crop)

        if "error" in result:
            return jsonify({"success": False, **result}), 400

        return jsonify({"success": True, **result})

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# POST /api/detect-disease  —  Crop Disease Detection (Vision AI)
# ---------------------------------------------------------------------------
@api_bp.route("/detect-disease", methods=["POST"])
def detect_disease_endpoint():
    """Analyze a plant image to detect diseases.

    Expects JSON body:
        image      (str, required) — base64-encoded image
        crop_hint  (str, optional) — crop name for context
        language   (str, optional) — locale code, default en
    """
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        image_b64 = (data.get("image") or "").strip()
        crop_hint = (data.get("crop_hint") or "").strip()
        language = (data.get("language") or "en").strip()

        if not image_b64:
            return jsonify({"error": "image is required (base64 encoded)"}), 400

        # Limit image size (~4MB base64 ≈ ~5.3M chars)
        if len(image_b64) > 6_000_000:
            return jsonify({"error": "Image too large. Maximum 4MB."}), 400

        result = detect_disease(image_b64, crop_hint, language)

        if "error" in result:
            return jsonify({"success": False, **result}), 400

        return jsonify({"success": True, **result})

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500


# ---------------------------------------------------------------------------
# POST /api/predict-yield  —  Crop Yield Prediction (RandomForest)
# ---------------------------------------------------------------------------
@api_bp.route("/predict-yield", methods=["POST"])
def predict_yield_endpoint():
    """Predict crop yield based on inputs.

    Expects JSON body:
        crop      (str, required) — crop name
        state     (str, required) — state name
        season    (str, required) — Kharif/Rabi/Zaid
        rainfall  (float, optional) — expected rainfall in mm
    """
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        crop = (data.get("crop") or "").strip()
        state = (data.get("state") or "").strip()
        season = (data.get("season") or "").strip()

        if not crop:
            return jsonify({"error": "crop is required"}), 400
        if not state:
            return jsonify({"error": "state is required"}), 400
        if not season:
            return jsonify({"error": "season is required"}), 400

        rainfall = data.get("rainfall")
        if rainfall is not None:
            try:
                rainfall = float(rainfall)
                if rainfall < 0 or rainfall > 10000:
                    return jsonify({"error": "rainfall must be 0-10000 mm"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "rainfall must be a number"}), 400

        result = predict_yield(crop, state, season, rainfall)

        if "error" in result:
            return jsonify({"success": False, **result}), 400

        return jsonify({"success": True, **result})

    except Exception as exc:
        return jsonify({"error": f"Internal server error: {exc}"}), 500

