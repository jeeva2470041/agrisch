"""
AgriScheme Backend — Rule-Based Soil Analysis Engine.
Replaces Gemini API for manual soil test analysis with deterministic
rules based on ICAR (Indian Council of Agricultural Research) standards.

References:
  - ICAR Soil Health Card parameters
  - Indian Fertiliser Recommendation Standards
  - Standard NPK classification thresholds (kg/ha)
"""
import logging

logger = logging.getLogger(__name__)

# ─── ICAR Standard Thresholds (kg/ha) ─────────────────────────────────────
# Source: Soil Health Card scheme, Government of India
NPK_THRESHOLDS = {
    "nitrogen": {"low": 280, "high": 560},      # kg/ha
    "phosphorus": {"low": 10, "high": 25},       # kg/ha (available P₂O₅)
    "potassium": {"low": 110, "high": 280},      # kg/ha (available K₂O)
}

# pH classification (ICAR)
PH_RANGES = {
    "strongly_acidic": (0, 4.5),
    "moderately_acidic": (4.5, 5.5),
    "slightly_acidic": (5.5, 6.5),
    "neutral": (6.5, 7.5),
    "slightly_alkaline": (7.5, 8.5),
    "moderately_alkaline": (8.5, 9.5),
    "strongly_alkaline": (9.5, 14),
}

# Organic carbon classification (%)
OC_THRESHOLDS = {"low": 0.5, "high": 0.75}

# ─── Fertilizer Recommendations (per hectare) ─────────────────────────────
FERTILIZER_RECS = {
    "nitrogen": {
        "Low": [
            "Apply 120-150 kg/ha Urea (46% N) in split doses",
            "Add 2-3 tonnes/ha Farm Yard Manure (FYM) for sustained nitrogen",
            "Consider green manuring with Dhaincha or Sunhemp before sowing",
        ],
        "Medium": [
            "Apply 80-100 kg/ha Urea in 2 split doses",
            "Maintain organic matter through crop residue incorporation",
        ],
        "High": [
            "Nitrogen is adequate — reduce urea application to 40-60 kg/ha",
            "Excess nitrogen can cause lodging and pest susceptibility",
        ],
    },
    "phosphorus": {
        "Low": [
            "Apply 50-60 kg/ha Single Super Phosphate (SSP) or 20-25 kg/ha DAP as basal dose",
            "Add Rock Phosphate (250 kg/ha) for long-term phosphorus availability in acidic soils",
        ],
        "Medium": [
            "Apply 30-40 kg/ha SSP as basal dose",
            "Phosphorus is moderately available — maintain through balanced fertilization",
        ],
        "High": [
            "Phosphorus is adequate — skip P fertilizer this season",
            "Excess phosphorus can reduce zinc availability",
        ],
    },
    "potassium": {
        "Low": [
            "Apply 60-80 kg/ha Muriate of Potash (MOP) as basal dose",
            "Apply potash in 2 splits for sandy soils to reduce leaching",
        ],
        "Medium": [
            "Apply 40-50 kg/ha MOP as basal dose",
        ],
        "High": [
            "Potassium is adequate — no additional K fertilizer needed",
        ],
    },
}

# pH-based recommendations
PH_RECOMMENDATIONS = {
    "strongly_acidic": [
        "Apply 4-6 tonnes/ha Agricultural Lime (CaCO₃) to raise pH",
        "Use dolomite lime if magnesium is also deficient",
        "Avoid ammonium-based fertilizers that further acidify soil",
    ],
    "moderately_acidic": [
        "Apply 2-3 tonnes/ha Agricultural Lime to correct acidity",
        "Add wood ash (1-2 tonnes/ha) as a natural liming agent",
    ],
    "slightly_acidic": [
        "pH is near optimal — minor liming (1 tonne/ha) may help sensitive crops",
    ],
    "neutral": [
        "pH is optimal for most crops — no correction needed",
    ],
    "slightly_alkaline": [
        "Add organic matter (FYM 5 tonnes/ha) to gradually lower pH",
        "Apply Gypsum (2-3 tonnes/ha) for sodic soils",
    ],
    "moderately_alkaline": [
        "Apply Gypsum 3-5 tonnes/ha to reduce alkalinity",
        "Use acidifying fertilizers like Ammonium Sulphate instead of Urea",
        "Add Sulphur (200-400 kg/ha) for gradual pH reduction",
    ],
    "strongly_alkaline": [
        "Apply Gypsum 5-8 tonnes/ha — soil reclamation needed",
        "Deep ploughing + organic matter (10 tonnes/ha FYM) essential",
        "Install drainage to leach excess salts",
        "Consider Pyrites (5 tonnes/ha) as an alternative amendment",
    ],
}

# Organic carbon recommendations
OC_RECOMMENDATIONS = {
    "Low": [
        "Add 5-10 tonnes/ha FYM or compost to improve organic matter",
        "Practice green manuring — grow and plough in legume crops",
        "Mulch with crop residues instead of burning them",
        "Apply Vermicompost (2-3 tonnes/ha) for quick organic boost",
    ],
    "Medium": [
        "Maintain organic carbon by adding 3-5 tonnes/ha FYM annually",
        "Incorporate crop residues after harvest",
    ],
    "High": [
        "Organic matter is excellent — continue current practices",
    ],
}

# Crop suitability by soil type (common Indian crops)
CROP_SUITABILITY = {
    "Alluvial": ["Rice", "Wheat", "Sugarcane", "Maize", "Pulses", "Vegetables", "Oilseeds"],
    "Black Cotton": ["Cotton", "Soybean", "Sugarcane", "Wheat", "Groundnut", "Sunflower"],
    "Red": ["Groundnut", "Millets", "Pulses", "Cotton", "Tobacco", "Rice"],
    "Laterite": ["Cashew", "Coconut", "Tea", "Coffee", "Rubber", "Rice", "Tapioca"],
    "Sandy": ["Groundnut", "Millets", "Watermelon", "Carrot", "Potato", "Pulses"],
    "Sandy Loam": ["Groundnut", "Vegetables", "Millets", "Potato", "Maize", "Pulses"],
    "Clay": ["Rice", "Wheat", "Sugarcane", "Cotton", "Jute"],
    "Clay Loam": ["Rice", "Wheat", "Cotton", "Sugarcane", "Maize", "Soybean"],
    "Loam": ["Wheat", "Rice", "Maize", "Sugarcane", "Vegetables", "Fruits", "Pulses"],
    "Silt": ["Rice", "Wheat", "Vegetables", "Sugarcane"],
}

# Crop suitability adjustments by pH range
CROP_PH_PREFERENCE = {
    "Rice": (5.0, 8.0),
    "Wheat": (6.0, 8.5),
    "Maize": (5.5, 7.5),
    "Cotton": (6.0, 8.0),
    "Sugarcane": (6.0, 8.0),
    "Groundnut": (5.5, 7.0),
    "Soybean": (6.0, 7.5),
    "Pulses": (6.0, 7.5),
    "Millets": (5.5, 8.0),
    "Vegetables": (6.0, 7.5),
    "Tea": (4.5, 6.0),
    "Coffee": (5.0, 6.5),
    "Coconut": (5.5, 8.0),
    "Potato": (4.8, 6.5),
    "Tobacco": (5.5, 7.5),
    "Fruits": (5.5, 7.5),
    "Oilseeds": (6.0, 7.5),
    "Jute": (6.0, 7.5),
    "Sunflower": (6.0, 7.5),
    "Cashew": (5.0, 6.5),
    "Rubber": (4.5, 6.0),
    "Tapioca": (5.5, 7.0),
    "Watermelon": (6.0, 7.0),
    "Carrot": (6.0, 6.8),
}

# Soil type descriptions
SOIL_DESCRIPTIONS = {
    "Alluvial": "Fertile deposit soil found in river plains. Good water retention and nutrient content. Ideal for intensive agriculture.",
    "Black Cotton": "Deep dark soil with high clay content and water-holding capacity. Cracks when dry. Rich in calcium, magnesium and iron.",
    "Red": "Iron oxide rich soil with low nitrogen and phosphorus. Good drainage but poor water retention.",
    "Laterite": "Weathered soil high in iron and aluminium. Acidic, low in nutrients but good for plantation crops.",
    "Sandy": "Loose, well-drained soil. Low water and nutrient retention. Needs frequent irrigation and fertilization.",
    "Sandy Loam": "Mix of sand and finer particles. Better nutrient retention than pure sand. Good for root vegetables.",
    "Clay": "Heavy, dense soil with high water retention. Can become waterlogged. Rich in nutrients but poor aeration.",
    "Clay Loam": "Balanced mix of clay and loam. Good structure, water retention and nutrient availability.",
    "Loam": "Ideal balanced soil with good drainage, aeration and nutrient retention. Best for most crops.",
    "Silt": "Fine-grained, smooth soil. Good water retention. Prone to compaction and erosion.",
}


def _classify_npk(value: float, nutrient: str) -> str:
    """Classify N/P/K level as Low/Medium/High based on ICAR thresholds."""
    thresholds = NPK_THRESHOLDS.get(nutrient, {"low": 0, "high": 0})
    if value < thresholds["low"]:
        return "Low"
    elif value > thresholds["high"]:
        return "High"
    return "Medium"


def _classify_oc(oc_pct: float) -> str:
    """Classify organic carbon as Low/Medium/High."""
    if oc_pct < OC_THRESHOLDS["low"]:
        return "Low"
    elif oc_pct > OC_THRESHOLDS["high"]:
        return "High"
    return "Medium"


def _classify_ph(ph: float) -> str:
    """Classify pH into ICAR category."""
    for name, (lo, hi) in PH_RANGES.items():
        if lo <= ph < hi:
            return name
    return "neutral"


def _get_drainage_from_soil_type(soil_type: str) -> str:
    """Estimate drainage from soil type."""
    drainage_map = {
        "Sandy": "Excellent",
        "Sandy Loam": "Good",
        "Loam": "Good",
        "Silt": "Moderate",
        "Clay Loam": "Moderate",
        "Alluvial": "Moderate",
        "Red": "Good",
        "Laterite": "Good",
        "Black Cotton": "Poor",
        "Clay": "Poor",
    }
    return drainage_map.get(soil_type, "Moderate")


def _compute_health_score(n_level: str, p_level: str, k_level: str,
                           oc_level: str, ph_class: str) -> int:
    """Compute an overall soil health score (1-10) from nutrient/pH levels."""
    score = 5  # base

    # NPK scoring (+/- per nutrient)
    level_scores = {"Low": -1, "Medium": 0, "High": 0.5}
    score += level_scores.get(n_level, 0)
    score += level_scores.get(p_level, 0)
    score += level_scores.get(k_level, 0)

    # OC scoring
    oc_scores = {"Low": -1.5, "Medium": 0, "High": 1}
    score += oc_scores.get(oc_level, 0)

    # pH scoring
    ph_scores = {
        "strongly_acidic": -2,
        "moderately_acidic": -1,
        "slightly_acidic": 0,
        "neutral": 1,
        "slightly_alkaline": 0,
        "moderately_alkaline": -1,
        "strongly_alkaline": -2,
    }
    score += ph_scores.get(ph_class, 0)

    return max(1, min(10, round(score)))


def _get_suitable_crops(soil_type: str, ph: float) -> list:
    """Get suitable crops based on soil type and pH."""
    base_crops = CROP_SUITABILITY.get(soil_type, CROP_SUITABILITY.get("Loam", []))

    if ph is None:
        return base_crops[:8]

    # Filter crops by pH tolerance
    suitable = []
    for crop in base_crops:
        ph_range = CROP_PH_PREFERENCE.get(crop)
        if ph_range is None:
            suitable.append(crop)
        elif ph_range[0] <= ph <= ph_range[1]:
            suitable.append(crop)

    # If too few crops after pH filter, add some back with a note
    if len(suitable) < 3:
        for crop in base_crops:
            if crop not in suitable:
                suitable.append(crop)
            if len(suitable) >= 5:
                break

    return suitable[:8]


def analyze_soil_rulebased(soil_data: dict) -> dict:
    """Analyze soil from manual test report values using ICAR rules.

    Args:
        soil_data: dict with optional keys:
            ph (float), nitrogen (float, kg/ha), phosphorus (float, kg/ha),
            potassium (float, kg/ha), organic_carbon (float, %),
            soil_type (str).

    Returns:
        dict matching the same schema as Gemini-based analysis.
    """
    ph = soil_data.get("ph")
    nitrogen = soil_data.get("nitrogen")
    phosphorus = soil_data.get("phosphorus")
    potassium = soil_data.get("potassium")
    organic_carbon = soil_data.get("organic_carbon")
    soil_type = soil_data.get("soil_type", "Loam")

    # Validate that at least one parameter is provided
    provided = [v for v in [ph, nitrogen, phosphorus, potassium, organic_carbon]
                if v is not None]
    if not provided and not soil_type:
        return {"error": "At least one soil parameter is required."}

    # ── Classify each parameter ──
    n_level = _classify_npk(nitrogen, "nitrogen") if nitrogen is not None else "Medium"
    p_level = _classify_npk(phosphorus, "phosphorus") if phosphorus is not None else "Medium"
    k_level = _classify_npk(potassium, "potassium") if potassium is not None else "Medium"
    oc_level = _classify_oc(organic_carbon) if organic_carbon is not None else "Medium"
    ph_class = _classify_ph(ph) if ph is not None else "neutral"

    # ── Identify deficiencies ──
    deficiencies = []
    if n_level == "Low":
        deficiencies.append("Nitrogen")
    if p_level == "Low":
        deficiencies.append("Phosphorus")
    if k_level == "Low":
        deficiencies.append("Potassium")
    if oc_level == "Low":
        deficiencies.append("Organic Carbon")
    if ph is not None and (ph < 5.5 or ph > 8.5):
        deficiencies.append("pH Imbalance")

    # ── Build recommendations ──
    recommendations = []

    # NPK recommendations
    if nitrogen is not None:
        recommendations.extend(FERTILIZER_RECS["nitrogen"].get(n_level, []))
    if phosphorus is not None:
        recommendations.extend(FERTILIZER_RECS["phosphorus"].get(p_level, []))
    if potassium is not None:
        recommendations.extend(FERTILIZER_RECS["potassium"].get(k_level, []))

    # pH recommendations
    if ph is not None:
        recommendations.extend(PH_RECOMMENDATIONS.get(ph_class, []))

    # Organic carbon recommendations
    if organic_carbon is not None:
        recommendations.extend(OC_RECOMMENDATIONS.get(oc_level, []))

    # General recommendation if few specific ones
    if len(recommendations) < 2:
        recommendations.append("Get a comprehensive soil test from your nearest Krishi Vigyan Kendra (KVK)")
        recommendations.append("Follow balanced fertilization (NPK) based on crop requirement")

    # ── Compute health score ──
    health_score = _compute_health_score(n_level, p_level, k_level, oc_level, ph_class)

    # ── Determine organic matter level ──
    if organic_carbon is not None:
        # Organic matter ≈ OC × 1.724 (Van Bemmelen factor)
        om_pct = organic_carbon * 1.724
        if om_pct < 1.0:
            organic_matter = "Low"
        elif om_pct > 2.0:
            organic_matter = "High"
        else:
            organic_matter = "Medium"
    else:
        organic_matter = "Medium"

    # ── Get suitable crops ──
    suitable_crops = _get_suitable_crops(soil_type, ph)

    # ── Confidence based on how many parameters were provided ──
    total_params = 6  # ph, N, P, K, OC, soil_type
    provided_count = sum(1 for v in [ph, nitrogen, phosphorus, potassium, organic_carbon]
                         if v is not None)
    if soil_type and soil_type != "Loam":
        provided_count += 1
    confidence = min(0.95, 0.4 + (provided_count / total_params) * 0.55)

    # ── Build color and texture analysis from soil type ──
    color_analysis = SOIL_DESCRIPTIONS.get(soil_type, f"{soil_type} soil — standard agricultural soil.")
    texture_analysis = _get_drainage_from_soil_type(soil_type) + " drainage typical of " + soil_type.lower() + " soils."

    result = {
        "soil_type": soil_type,
        "ph_estimate": ph if ph is not None else 7.0,
        "organic_matter": organic_matter,
        "moisture_level": "Cannot determine from test data",
        "drainage": _get_drainage_from_soil_type(soil_type),
        "color_analysis": color_analysis,
        "texture_analysis": texture_analysis,
        "health_score": health_score,
        "deficiencies": deficiencies,
        "recommendations": recommendations,
        "suitable_crops": suitable_crops,
        "confidence": round(confidence, 2),
        "npk_status": {
            "nitrogen": n_level,
            "phosphorus": p_level,
            "potassium": k_level,
        },
        "analysis_method": "rule_based",  # flag so frontend knows
    }

    logger.info("Rule-based soil analysis: health_score=%d, deficiencies=%s",
                health_score, deficiencies)

    return result
