"""
AgriScheme Backend — Offline Soil Image Analyzer.

Analyzes soil images using color science and image processing (PIL + NumPy)
to estimate soil type, organic matter, moisture, and health — no API needed.

Based on:
  - Munsell Soil Color System (USDA-NRCS)
  - ICAR Soil Classification (Indian soils)
  - Pedological color–property correlations

Dependencies: Pillow, NumPy (no OpenCV required)
"""
import io
import base64
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ─── Soil Color Profiles (HSV dominant ranges) ────────────────────────────
# H = 0-360°, S = 0-100%, V = 0-100%
# Each profile has hue_range, min saturation, typical brightness descriptors
SOIL_COLOR_PROFILES = {
    "Laterite / Red": {
        "hue": (0, 30),         # Red-orange hues
        "min_sat": 25,
        "description": "Red to reddish-brown soil rich in iron and aluminium. "
                       "Common in tropical regions with heavy rainfall. "
                       "Well-weathered, typically acidic.",
        "soil_type": "Red / Laterite",
        "ph_estimate": 5.5,
        "organic_matter": "Low",
        "drainage": "Good",
        "iron_content": "High",
    },
    "Black Cotton (Regur)": {
        "hue": (0, 360),        # Any hue but very low saturation + low brightness
        "max_val": 35,
        "min_sat": 0,
        "max_sat": 25,
        "description": "Dark black soil, likely Black Cotton (Regur). "
                       "Rich in montmorillonite clay, high water retention. "
                       "Characteristic of Deccan Plateau — swells when wet, cracks when dry.",
        "soil_type": "Black Cotton",
        "ph_estimate": 7.8,
        "organic_matter": "Medium",
        "drainage": "Poor",
        "iron_content": "Medium",
    },
    "Alluvial (Dark)": {
        "hue": (15, 60),
        "max_val": 50,
        "min_sat": 10,
        "max_sat": 55,
        "description": "Dark brown alluvial soil with good organic content. "
                       "Transported by rivers, fertile and suitable for multiple crops.",
        "soil_type": "Alluvial",
        "ph_estimate": 7.0,
        "organic_matter": "High",
        "drainage": "Moderate",
        "iron_content": "Medium",
    },
    "Alluvial (Light)": {
        "hue": (25, 55),
        "min_val": 50,
        "min_sat": 15,
        "max_sat": 50,
        "description": "Light brown to yellowish-brown soil. Likely alluvial or "
                       "colluvial origin. Moderate fertility, good for irrigation-based farming.",
        "soil_type": "Alluvial",
        "ph_estimate": 7.2,
        "organic_matter": "Medium",
        "drainage": "Good",
        "iron_content": "Low",
    },
    "Sandy": {
        "hue": (30, 55),
        "min_val": 60,
        "min_sat": 10,
        "max_sat": 35,
        "description": "Light-colored, sandy soil with large particles. "
                       "Low water and nutrient retention. Common in arid and semi-arid regions.",
        "soil_type": "Sandy",
        "ph_estimate": 7.5,
        "organic_matter": "Low",
        "drainage": "Excellent",
        "iron_content": "Low",
    },
    "Clay (Brown)": {
        "hue": (10, 40),
        "min_sat": 20,
        "max_val": 55,
        "min_val": 25,
        "description": "Brown clay soil with fine particles. "
                       "Moderate to poor drainage, nutrient-rich.",
        "soil_type": "Clay",
        "ph_estimate": 6.8,
        "organic_matter": "Medium",
        "drainage": "Poor",
        "iron_content": "Medium",
    },
    "Loamy": {
        "hue": (15, 45),
        "min_val": 35,
        "max_val": 65,
        "min_sat": 20,
        "max_sat": 55,
        "description": "Medium brown loamy soil — balanced mix of sand, silt, and clay. "
                       "Ideal agricultural soil with good structure and fertility.",
        "soil_type": "Loamy",
        "ph_estimate": 6.5,
        "organic_matter": "Medium",
        "drainage": "Moderate",
        "iron_content": "Medium",
    },
    "Yellowish (Lateritic)": {
        "hue": (30, 55),
        "min_sat": 30,
        "min_val": 40,
        "description": "Yellow to yellowish-brown soil indicating moderate iron oxide. "
                       "Typically acidic, found in high-rainfall tropical areas.",
        "soil_type": "Laterite",
        "ph_estimate": 5.8,
        "organic_matter": "Low",
        "drainage": "Good",
        "iron_content": "Medium",
    },
}

# ─── Crop suggestions by detected soil type ───────────────────────────────
CROP_MAP = {
    "Red / Laterite": ["Groundnut", "Ragi", "Millets", "Cashew", "Tapioca", "Pulses"],
    "Black Cotton": ["Cotton", "Soybean", "Sunflower", "Sorghum", "Wheat", "Sugarcane"],
    "Alluvial": ["Rice", "Wheat", "Maize", "Sugarcane", "Vegetables", "Jute", "Pulses"],
    "Sandy": ["Groundnut", "Bajra", "Watermelon", "Dates", "Guar", "Sesame"],
    "Clay": ["Rice", "Wheat", "Sugarcane", "Cotton", "Jute"],
    "Loamy": ["Wheat", "Rice", "Maize", "Sugarcane", "Vegetables", "Fruits", "Pulses"],
    "Laterite": ["Rubber", "Tea", "Coffee", "Coconut", "Cashew", "Tapioca"],
}

# ────────────────────────────────────────────────────────────────────────────


def _decode_image(image_base64: str) -> Image.Image:
    """Decode base64 string to PIL Image, resize for fast processing."""
    raw = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    # Resize to max 256px on longest side for speed
    img.thumbnail((256, 256), Image.LANCZOS)
    return img


def _rgb_to_hsv_array(img: Image.Image) -> np.ndarray:
    """Convert PIL RGB image to HSV numpy array (H: 0-360, S: 0-100, V: 0-100)."""
    arr = np.array(img, dtype=np.float32) / 255.0
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    # Hue
    h = np.zeros_like(delta)
    mask_r = (cmax == r) & (delta > 0)
    mask_g = (cmax == g) & (delta > 0)
    mask_b = (cmax == b) & (delta > 0)
    h[mask_r] = 60.0 * (((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6)
    h[mask_g] = 60.0 * (((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2)
    h[mask_b] = 60.0 * (((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4)

    # Saturation (0-100)
    s = np.where(cmax > 0, (delta / cmax) * 100, 0)

    # Value (0-100)
    v = cmax * 100

    return np.stack([h, s, v], axis=-1)


def _center_crop_stats(hsv: np.ndarray, crop_frac: float = 0.5):
    """Get mean HSV from center portion of image (avoids background edges)."""
    h_img, w_img = hsv.shape[:2]
    margin_h = int(h_img * (1 - crop_frac) / 2)
    margin_w = int(w_img * (1 - crop_frac) / 2)
    center = hsv[margin_h:h_img - margin_h, margin_w:w_img - margin_w]

    mean_h = float(np.mean(center[:, :, 0]))
    mean_s = float(np.mean(center[:, :, 1]))
    mean_v = float(np.mean(center[:, :, 2]))
    std_v = float(np.std(center[:, :, 2]))
    std_s = float(np.std(center[:, :, 1]))

    return mean_h, mean_s, mean_v, std_v, std_s


def _estimate_moisture(mean_s: float, mean_v: float) -> str:
    """Estimate moisture level from saturation and brightness.

    Wet soil is darker (lower V) and more saturated (higher S).
    """
    if mean_v < 20 and mean_s > 30:
        return "Waterlogged"
    elif mean_v < 35 and mean_s > 20:
        return "Wet"
    elif mean_v < 55:
        return "Moderate"
    else:
        return "Dry"


def _match_soil_profile(mean_h, mean_s, mean_v):
    """Match mean HSV values to best soil color profile.

    Returns (profile_name, profile_dict, match_score).
    """
    # Priority check: very dark + low saturation → Black Cotton
    if mean_v < 35 and mean_s < 25:
        profile = SOIL_COLOR_PROFILES["Black Cotton (Regur)"]
        # Score higher if darker
        score = 4.0 + (35 - mean_v) / 35
        return ("Black Cotton (Regur)", profile, score)

    best_match = None
    best_score = -1

    for name, profile in SOIL_COLOR_PROFILES.items():
        if name == "Black Cotton (Regur)":
            continue  # Already handled above
        score = 0

        # Hue check
        h_lo, h_hi = profile.get("hue", (0, 360))
        if h_lo <= mean_h <= h_hi:
            # Closer to center of range → higher score
            h_center = (h_lo + h_hi) / 2
            h_range = (h_hi - h_lo) / 2
            h_dist = abs(mean_h - h_center) / max(h_range, 1)
            score += 3 * (1 - h_dist)
        else:
            continue  # Hue mismatch is disqualifying

        # Saturation checks
        min_sat = profile.get("min_sat", 0)
        max_sat = profile.get("max_sat", 100)
        if mean_s < min_sat or mean_s > max_sat:
            score -= 2
        else:
            score += 1

        # Brightness checks
        min_val = profile.get("min_val", 0)
        max_val = profile.get("max_val", 100)
        if mean_v < min_val or mean_v > max_val:
            score -= 2
        else:
            score += 1.5

        if score > best_score:
            best_score = score
            best_match = (name, profile, score)

    # Fallback: if nothing matched well, use brightness-based heuristic
    if best_match is None or best_score < 1:
        if mean_v < 30:
            key = "Black Cotton (Regur)"
        elif mean_v > 65:
            key = "Sandy"
        else:
            key = "Loamy"
        profile = SOIL_COLOR_PROFILES[key]
        best_match = (key, profile, 1.0)

    return best_match


def _compute_health_score(profile: dict, moisture: str, std_v: float) -> int:
    """Compute a 1-10 health score from detected properties."""
    score = 5  # baseline

    # Organic matter bonus
    om = profile.get("organic_matter", "Medium")
    if om == "High":
        score += 2
    elif om == "Low":
        score -= 1

    # Drainage
    drainage = profile.get("drainage", "Moderate")
    if drainage == "Good":
        score += 1
    elif drainage == "Excellent":
        score += 1
    elif drainage == "Poor":
        score -= 1

    # pH penalty for extremes
    ph = profile.get("ph_estimate", 7.0)
    if ph < 5.0 or ph > 9.0:
        score -= 2
    elif ph < 5.5 or ph > 8.5:
        score -= 1

    # Moisture penalty
    if moisture == "Waterlogged":
        score -= 2
    elif moisture == "Dry":
        score -= 1

    # Color uniformity bonus (low std = uniform = healthier topsoil)
    if std_v < 12:
        score += 1

    return max(1, min(10, score))


def _generate_recommendations(profile: dict, moisture: str, ph: float) -> list:
    """Generate fertilizer and management recommendations from detected properties."""
    recs = []
    om = profile.get("organic_matter", "Medium")
    drainage = profile.get("drainage", "Moderate")
    soil_type = profile.get("soil_type", "Unknown")

    # Organic matter
    if om == "Low":
        recs.append("Soil appears low in organic matter — add 5-10 tonnes/ha FYM or compost")
        recs.append("Practice green manuring with Dhaincha or Sunhemp")
        recs.append("Mulch with crop residues instead of burning")
    elif om == "High":
        recs.append("Organic matter appears good — maintain with crop residue incorporation")

    # pH corrections
    if ph < 5.5:
        recs.append(f"Soil appears acidic (est. pH {ph:.1f}) — apply agricultural lime 2-4 tonnes/ha")
    elif ph > 8.5:
        recs.append(f"Soil appears alkaline (est. pH {ph:.1f}) — apply Gypsum 2-5 tonnes/ha")

    # Moisture
    if moisture == "Waterlogged":
        recs.append("Soil appears waterlogged — improve drainage with raised beds or channels")
    elif moisture == "Dry":
        recs.append("Soil appears dry — consider mulching and drip irrigation")

    # Drainage-specific
    if drainage == "Poor":
        recs.append("Poor drainage expected — avoid waterlogging-sensitive crops or use raised beds")
    elif drainage == "Excellent":
        recs.append("Sandy/well-drained soil loses nutrients fast — apply fertilizers in split doses")

    # General NPK (since we can't measure from image)
    recs.append("Get a soil test report for precise NPK values and targeted fertilizer recommendations")

    # Soil-type specific
    if soil_type == "Black Cotton":
        recs.append("Avoid tillage when too wet — Black Cotton soil becomes very sticky")
    elif soil_type == "Sandy":
        recs.append("Sandy soil needs frequent but smaller irrigation intervals")
    elif soil_type in ("Red / Laterite", "Laterite"):
        recs.append("Laterite soils benefit from phosphorus application (SSP 50-60 kg/ha)")

    return recs


def _detect_deficiencies(profile: dict) -> list:
    """Estimate likely deficiencies from color-based properties."""
    deficiencies = []
    om = profile.get("organic_matter", "Medium")
    ph = profile.get("ph_estimate", 7.0)
    iron = profile.get("iron_content", "Medium")

    if om == "Low":
        deficiencies.append("Nitrogen (likely — low organic matter)")
        deficiencies.append("Organic Carbon (likely — pale/light soil)")

    if ph < 5.5:
        deficiencies.append("Calcium (likely — acidic soil)")
        deficiencies.append("Molybdenum (likely — acidic soil)")
    elif ph > 8.0:
        deficiencies.append("Iron (likely — alkaline soil locks iron)")
        deficiencies.append("Zinc (likely — alkaline soil)")
        deficiencies.append("Manganese (likely — alkaline soil)")

    if iron == "Low":
        deficiencies.append("Iron (visual — pale coloring)")

    return deficiencies


def _compute_confidence(match_score: float, std_v: float, std_s: float) -> float:
    """Compute overall confidence of the image analysis.

    Higher confidence when:
      - Color profile matched strongly
      - Low variance (uniform soil, not mixed objects)
    Lower confidence when:
      - Weak match
      - High variance (noisy image, non-soil areas)
    """
    # Base from match quality (score typically 1-5)
    conf = min(0.7, match_score * 0.14)

    # Uniformity bonus/penalty
    if std_v < 15 and std_s < 15:
        conf += 0.15  # Very uniform — likely a clean soil sample
    elif std_v > 30 or std_s > 30:
        conf -= 0.15  # Noisy — mixed content or poor photo

    return round(max(0.25, min(0.80, conf)), 2)


def analyze_soil_from_image(image_base64: str) -> dict:
    """Analyze a soil image using color science (no API required).

    Args:
        image_base64: Base64-encoded soil image (JPEG/PNG/WEBP).

    Returns:
        dict with soil analysis results matching the API schema, plus
        'analysis_method': 'image_color_analysis'.
    """
    try:
        img = _decode_image(image_base64)
    except Exception as e:
        logger.error("Failed to decode soil image: %s", e)
        return {"error": f"Invalid image data: {e}"}

    # Convert to HSV and get center-crop statistics
    hsv = _rgb_to_hsv_array(img)
    mean_h, mean_s, mean_v, std_v, std_s = _center_crop_stats(hsv)

    logger.info(
        "Soil image stats — H:%.1f S:%.1f V:%.1f stdV:%.1f stdS:%.1f",
        mean_h, mean_s, mean_v, std_v, std_s,
    )

    # Match to soil profile
    profile_name, profile, match_score = _match_soil_profile(mean_h, mean_s, mean_v)
    logger.info("Matched soil profile: %s (score=%.2f)", profile_name, match_score)

    soil_type = profile["soil_type"]
    ph = profile["ph_estimate"]
    moisture = _estimate_moisture(mean_s, mean_v)
    health = _compute_health_score(profile, moisture, std_v)
    confidence = _compute_confidence(match_score, std_v, std_s)

    # Build texture description from variance
    if std_v < 10:
        texture = "Very uniform fine texture — likely clay or silt dominant"
    elif std_v < 20:
        texture = "Moderately uniform texture — likely loam or clay-loam"
    elif std_v < 30:
        texture = "Mixed texture with visible particles — sandy loam or gravel mix"
    else:
        texture = "Highly varied texture — coarse particles or mixed debris visible"

    return {
        "soil_type": soil_type,
        "ph_estimate": ph,
        "organic_matter": profile.get("organic_matter", "Medium"),
        "moisture_level": moisture,
        "drainage": profile.get("drainage", "Moderate"),
        "color_analysis": profile.get("description", ""),
        "texture_analysis": texture,
        "health_score": health,
        "deficiencies": _detect_deficiencies(profile),
        "recommendations": _generate_recommendations(profile, moisture, ph),
        "suitable_crops": CROP_MAP.get(soil_type, ["Consult local agronomist"]),
        "confidence": confidence,
        "analysis_method": "image_color_analysis",
        "_debug": {
            "matched_profile": profile_name,
            "mean_hsv": [round(mean_h, 1), round(mean_s, 1), round(mean_v, 1)],
            "std_v": round(std_v, 1),
            "std_s": round(std_s, 1),
        },
    }
