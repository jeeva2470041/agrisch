# Soil Health Analysis — Feature Documentation

## Overview

The Soil Health Analysis feature provides farmers with comprehensive soil
assessments through **two input modes** — both working **fully offline** with
zero API costs:

| Mode | Input | Engine | Response Time |
|------|-------|--------|---------------|
| **Image Analysis** | Camera / gallery photo | Color science (PIL + NumPy) | < 100 ms |
| **Manual Analysis** | pH, N, P, K, OC, soil type | ICAR rule engine | < 1 ms |

Both modes return the **same JSON schema**, making them interchangeable in the
Flutter frontend.

---

## Architecture

```
Flutter App
    │
    ├── Camera/Gallery ──► POST /api/analyze-soil  { image: base64 }
    │                           │
    │                     soil_service.py
    │                     analyze_soil_image()
    │                           │
    │                ┌──────────┴──────────┐
    │                │                     │
    │       soil_image_analyzer.py    (Gemini Vision)
    │       Color-based analysis       Optional fallback
    │       PIL + NumPy                if SOIL_IMAGE_MODE=gemini
    │                │
    │                ▼
    │         Munsell Color Matching
    │         HSV → Soil Profile → Properties
    │
    └── Manual Entry ──► POST /api/analyze-soil  { ph, nitrogen, ... }
                              │
                        soil_service.py
                        analyze_soil_manual()
                              │
                     soil_rules_engine.py
                     ICAR rule-based engine
                     NPK thresholds + fertilizer tables
```

### Files

| File | Lines | Purpose |
|------|-------|---------|
| `services/soil_service.py` | ~275 | Routing layer — picks analysis method, validates input |
| `services/soil_image_analyzer.py` | ~330 | Offline image analysis using color science |
| `services/soil_rules_engine.py` | ~416 | ICAR rule-based manual soil analysis |

---

## Image Analysis — How It Works

### Step 1: Decode & Resize

```python
img = Image.open(BytesIO(base64.b64decode(image_base64))).convert("RGB")
img.thumbnail((256, 256))  # Fast processing, color info preserved
```

The farmer's camera photo arrives as a base64 string. We decode it and shrink
to 256×256 pixels — color statistics don't need high resolution.

### Step 2: RGB → HSV Conversion

Every pixel is converted from RGB to **HSV (Hue, Saturation, Value)**:

- **Hue (0–360°)** — the actual color: red = 0°, yellow = 60°, brown ≈ 20–40°
- **Saturation (0–100%)** — color vividness: gray = 0%, pure red = 100%
- **Value (0–100%)** — brightness: black = 0%, white = 100%

**Why HSV?** Soil science classifies by color name + darkness, which maps
directly to Hue + Value. RGB mixes color and brightness together, making
classification harder.

### Step 3: Center-Crop Statistics

We analyze only the **center 50%** of the image:

```
┌──────────────────┐
│     ignored      │  ← edges: hands, tools, shadows
│   ┌──────────┐   │
│   │  CENTER  │   │  ← actual soil sample
│   │   50%    │   │
│   └──────────┘   │
│     ignored      │
└──────────────────┘
```

From the center we compute:
- **Mean H, S, V** — average soil color
- **Std dev of V** — texture uniformity (low = fine clay, high = coarse gravel)
- **Std dev of S** — color consistency

### Step 4: Soil Profile Matching

Mean HSV values are compared against **8 Indian soil color profiles**:

| Profile | Hue Range | Brightness | Saturation | Soil Type |
|---------|-----------|------------|------------|-----------|
| Red / Laterite | 0–30° | any | > 25% | Red / Laterite |
| Black Cotton (Regur) | any | < 35% (very dark) | < 25% (grayish) | Black Cotton |
| Alluvial (Dark) | 15–60° | < 50% | 10–55% | Alluvial |
| Alluvial (Light) | 25–55° | > 50% | 15–50% | Alluvial |
| Sandy | 30–55° | > 60% (bright) | 10–35% | Sandy |
| Clay (Brown) | 10–40° | 25–55% | > 20% | Clay |
| Loamy | 15–45° | 35–65% | 20–55% | Loamy |
| Yellowish (Lateritic) | 30–55° | > 40% | > 30% | Laterite |

**Priority rule**: Very dark + low saturation → Black Cotton (checked first,
since Deccan Plateau soils are uniquely identifiable by darkness).

### Step 5: Derive Properties from Color

Once the soil profile is matched, **established pedological correlations** are
used to derive:

| Property | How It's Derived |
|----------|-----------------|
| **pH estimate** | From soil type (e.g., Laterite → acidic ~5.5, Black Cotton → alkaline ~7.8) |
| **Organic matter** | From brightness (dark = high OM, light = low OM) |
| **Moisture** | From saturation + brightness (wet soil is darker and more saturated) |
| **Drainage** | From soil type (clay = poor, sandy = excellent) |
| **Texture** | From brightness variance (low std = fine particles, high std = coarse) |
| **Deficiencies** | From pH + organic matter (acidic → Ca/Mo deficiency, low OM → N deficiency) |

### Step 6: Confidence Score

```
confidence = (match_quality × 0.14) + uniformity_bonus
```

- **Higher** when HSV closely matches a profile center + low image variance
- **Lower** when image is noisy, mixed objects, or weak color match
- Range: 0.25 – 0.80 (capped since image-only analysis has inherent limits)

---

## Manual Analysis — How It Works

### ICAR Rule Engine

Uses thresholds from **ICAR (Indian Council of Agricultural Research)** Soil
Health Card standards:

#### NPK Classification (kg/ha)

| Nutrient | Low | Medium | High |
|----------|-----|--------|------|
| Nitrogen (N) | < 280 | 280–560 | > 560 |
| Phosphorus (P₂O₅) | < 10 | 10–25 | > 25 |
| Potassium (K₂O) | < 110 | 110–280 | > 280 |

#### pH Classification

| Range | Category |
|-------|----------|
| 0 – 4.5 | Strongly acidic |
| 4.5 – 5.5 | Moderately acidic |
| 5.5 – 6.5 | Slightly acidic |
| 6.5 – 7.5 | Neutral (optimal) |
| 7.5 – 8.5 | Slightly alkaline |
| 8.5 – 9.5 | Moderately alkaline |
| 9.5+ | Strongly alkaline |

#### Organic Carbon (%)

| Level | Threshold |
|-------|-----------|
| Low | < 0.5% |
| Medium | 0.5 – 0.75% |
| High | > 0.75% |

### Fertilizer Recommendations

Each deficiency triggers **specific, quantitative** recommendations:

```
Nitrogen LOW  → "Apply 120-150 kg/ha Urea (46% N) in split doses"
                "Add 2-3 tonnes/ha FYM for sustained nitrogen"
                "Consider green manuring with Dhaincha or Sunhemp"

Phosphorus LOW → "Apply 50-60 kg/ha SSP or 20-25 kg/ha DAP as basal dose"
                 "Add Rock Phosphate (250 kg/ha) for long-term availability"

pH < 5.5 → "Apply agricultural lime 2-4 tonnes/ha"
pH > 8.5 → "Apply Gypsum 2-5 tonnes/ha for sodic soil reclamation"
```

### Crop Suitability

Determined by **two factors**:

1. **Soil type** → crop list (e.g., Black Cotton → Cotton, Soybean, Sunflower)
2. **pH preference** → 24 crops with optimal pH ranges (e.g., Rice: 5.0–6.5,
   Sugarcane: 6.0–7.5) cross-referenced against measured pH

### Health Score (1–10)

Computed from a scoring matrix:

| Factor | Points |
|--------|--------|
| All NPK Medium/High | +2 each |
| pH 6.5–7.5 (neutral) | +2 |
| Organic Carbon High | +2 |
| Any NPK Low | -1 each |
| pH extreme (< 5 or > 9) | -3 |
| Multiple deficiencies | -1 per extra |

### Confidence Score

Based on **number of parameters provided**:

| Params Provided | Confidence |
|-----------------|------------|
| 1 parameter | 0.40 |
| 2–3 parameters | 0.55–0.70 |
| 4–5 parameters | 0.80–0.90 |
| All 6 (pH, N, P, K, OC, type) | 0.95 |

---

## Why This Is Efficient

### vs. Gemini API (previous implementation)

| Metric | Gemini API | Rule Engine / Color Analysis |
|--------|-----------|------------------------------|
| **Response time** | 3–10 seconds | < 1 ms (manual) / < 100 ms (image) |
| **Cost** | ~$0.002 per call | Free |
| **Offline support** | No (needs internet) | Yes |
| **Consistency** | Non-deterministic (different answer each time) | Same input → same output |
| **Accuracy source** | LLM training data (may hallucinate) | ICAR standards (peer-reviewed) |
| **Transparency** | Black box | Every recommendation is traceable to a rule |
| **Availability** | API rate limits, outages | Always available |
| **Privacy** | Soil data sent to Google servers | Stays on local server |

### Why Rule-Based > ML for Soil Analysis

1. **Soil science is well-characterized** — NPK thresholds, pH effects, and
   fertilizer doses are established standards, not patterns to discover.

2. **No training data needed** — ICAR publishes exact thresholds; we encode
   them directly.

3. **Auditability** — If a farmer asks _"why did you recommend lime?"_, we can
   point to `pH < 5.5 → lime 2-4 tonnes/ha` from ICAR standards.

4. **No maintenance burden** — No model retraining, no dataset collection, no
   GPU requirements.

5. **Edge deployment ready** — The entire engine is ~400 lines of pure Python
   with zero dependencies. Could run on a Raspberry Pi or be compiled to WASM
   for in-browser analysis.

### Image Analysis Limitations (Honest Assessment)

- **Confidence capped at 0.80** — color alone can't determine exact NPK levels
- **Works best with clean soil samples** — mixed scenes reduce accuracy
- **Cannot detect** micronutrient deficiencies (Zn, Fe, B, Mn)
- **Lighting affects accuracy** — indoor vs outdoor can shift detected Hue

**Mitigation**: `SOIL_IMAGE_MODE=hybrid` tries offline first, falls back to
Gemini Vision when confidence is low (< 0.40).

---

## API Endpoint

### `POST /api/analyze-soil`

**Image mode** (send photo):
```json
{
  "image": "<base64-encoded JPEG/PNG>",
  "language": "en"
}
```

**Manual mode** (send test report values):
```json
{
  "ph": 6.5,
  "nitrogen": 300,
  "phosphorus": 15,
  "potassium": 200,
  "organic_carbon": 0.6,
  "soil_type": "Loamy",
  "language": "en"
}
```

**Response** (same schema for both modes):
```json
{
  "soil_type": "Loamy",
  "ph_estimate": 6.5,
  "organic_matter": "Medium",
  "moisture_level": "Moderate",
  "drainage": "Moderate",
  "color_analysis": "...",
  "texture_analysis": "...",
  "health_score": 7,
  "deficiencies": ["Nitrogen"],
  "recommendations": [
    "Apply 120-150 kg/ha Urea in split doses",
    "Add 2-3 tonnes/ha FYM"
  ],
  "suitable_crops": ["Wheat", "Rice", "Maize"],
  "confidence": 0.85,
  "npk_status": { "nitrogen": "Low", "phosphorus": "Medium", "potassium": "High" },
  "analysis_method": "rule_based"
}
```

`analysis_method` will be one of: `rule_based`, `image_color_analysis`, or
`gemini_vision`.

---

## Configuration

Set `SOIL_IMAGE_MODE` in `backend/.env`:

```bash
# Options: offline (default), gemini, hybrid
SOIL_IMAGE_MODE=offline
```

| Value | Behavior |
|-------|----------|
| `offline` | Color analysis only — no API calls |
| `gemini` | Gemini Vision only — requires `GEMINI_API_KEY` |
| `hybrid` | Offline first → Gemini fallback if confidence < 0.40 |
