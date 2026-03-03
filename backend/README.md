# AgriScheme Backend (Production Upgrade)

Flask backend for AgriScheme with:
- real mandi market integration (data.gov.in AGMARKNET + cache + fallback),
- yield prediction from a trained RandomForest model,
- scheme eligibility APIs,
- weather, AI assistant, alerts, and supporting agronomy endpoints.

## What was upgraded

### Real market data integration
- `services/market_service.py` now uses a 3-tier strategy:
  1. local cache (`data/market_cache.json`),
  2. live data.gov.in API,
  3. MSP-based fallback.
- Added config controls:
  - `DATA_GOV_API_KEY`
  - `MARKET_MODE` (`api` or `msp_only`)
  - `MARKET_CACHE_TTL`

### Yield model upgrade
- Added dataset generation script: `scripts/generate_yield_dataset.py`
- Added model training script: `scripts/train_yield_model.py`
- Trained model artifacts are loaded from disk by `services/yield_service.py`:
  - `models/yield_model.pkl`
  - `models/yield_encoders.pkl`
- Dataset files:
  - `data/crop_yield.csv` (2882 rows)
  - `data/yield_train.csv` (2305 rows)
  - `data/yield_test.csv` (577 rows)

### Evaluation (current trained model)
- Test R²: **0.9828**
- MAE: **0.93 t/ha**
- RMSE: **2.22 t/ha**

## Project structure (backend)

- `app.py` — Flask app entrypoint
- `routes.py` — API routes
- `config.py` — env-based settings
- `services/` — market, yield, weather, AI, alerts, etc.
- `scripts/` — dataset generation + model training
- `models/` — saved model files
- `data/` — datasets, cache, and data-source notes
- `tests/` — unit/integration test files

## Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- Optional API keys:
  - data.gov.in key (for live market data)
  - Gemini key (for AI-related endpoints)

## Setup

From `backend/`:

1. Create and activate virtual environment

Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies
```powershell
pip install -r requirements.txt
```

3. Create `.env` from example
```powershell
copy .env.example .env
```

4. Edit `.env` with real values (at minimum `MONGO_URI` and optional API keys)

## Run backend

```powershell
python app.py
```

Server starts on `http://127.0.0.1:5000` (or `FLASK_PORT`).

## Regenerate dataset and retrain model

```powershell
python scripts/generate_yield_dataset.py
python scripts/train_yield_model.py
```

This updates CSVs in `data/` and model artifacts in `models/`.
## Model Retraining, Cache TTL, and Backend Startup Behavior

### How to retrain the yield model
- To retrain the crop yield prediction model with new data:
  1. (Optional) Regenerate the training/test datasets:
     ```powershell
     python scripts/generate_yield_dataset.py
     ```
  2. Train and save the model:
     ```powershell
     python scripts/train_yield_model.py
     ```
  This updates CSVs in `data/` and model artifacts in `models/`.

### How cache TTL works
- Market price data is cached in `data/market_cache.json` for the duration set by `MARKET_CACHE_TTL` (in seconds).
- With `MARKET_CACHE_TTL=86400` (24 hours), cached prices are reused for 24 hours before refreshing from the API or fallback.
- This reduces API calls and speeds up repeated requests.

### What happens every time you run the backend
- On startup, environment variables are loaded from `.env` (see `config.py` for defaults).
- The yield model is **not retrained automatically**; instead, the backend loads the latest trained model from `models/yield_model.pkl` and `models/yield_encoders.pkl` when `/api/predict-yield` is first called.
- If model files are missing or corrupt, a fallback in-memory model is trained for basic predictions until you retrain.
- Market price cache is checked for validity (based on TTL) before fetching new data.
- If `SOIL_IMAGE_MODE` or `VOICE_NLP_MODE` are missing from `.env`, they default to `offline` mode automatically.
- Restart the backend after changing `.env` variables for changes to take effect.

### Quick validation after retraining
- Run tests to confirm model and API health:
  ```powershell
  python -m pytest tests/test_yield_service.py -v
  ```

---

## Run tests

Run all backend tests:
```powershell
python -m pytest tests/ -v
```

Current status after upgrade: **62 passed**.

## Key API endpoints

- `GET /` — health check
- `GET /api/` — API health check
- `POST /api/getEligibleSchemes` — eligibility engine
- `GET /api/schemes` — list schemes
- `GET /api/weather?state=...` — weather summary
- `GET /api/market-prices?state=...&crop=...` — market prices (API/cache/fallback)
- `POST /api/predict-yield` — yield prediction
- `GET /api/price-forecast?crop=...&state=...` — forecast
- `POST /api/ask-ai` — AI assistant
- `POST /api/parse-voice-input` — voice NLP parser
- `POST /api/detect-disease` — disease detection (current implementation)
- `POST /api/analyze-soil` — soil analysis
- `POST /api/recommend-crop` — crop recommendations
- `GET /api/weather-alerts?state=...` — weather alerts
- `POST /api/price-alerts` — price alert checks
- `GET /api/crop-calendar?crop=...&state=...` — crop calendar

## Configuration reference

Configured via environment variables in `config.py`:

- `MONGO_URI`, `DB_NAME`
- `FLASK_ENV`, `FLASK_PORT`, `FLASK_DEBUG`
- `DATA_GOV_API_KEY`
- `MARKET_MODE` (`api` | `msp_only`)
- `MARKET_CACHE_TTL` (seconds)
- `YIELD_MODEL_DIR` (default: `models`)

## Data sources

See detailed notes in:
- `data/DATA_SOURCES.md`

## Notes

- If data.gov.in is unavailable/rate-limited, market service automatically falls back to MSP mode.
- If model files are missing, yield service has a fallback training path to stay operational.
- For production deployment, run with Gunicorn and set `FLASK_DEBUG=0`.
