"""
AgriScheme Backend — Configuration module.
Loads all settings from environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "agrischeme_db")

# ---------------------------------------------------------------------------
# Flask
# ---------------------------------------------------------------------------
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

# ---------------------------------------------------------------------------
# Market Data (data.gov.in)
# ---------------------------------------------------------------------------
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")
MARKET_CACHE_TTL = int(os.getenv("MARKET_CACHE_TTL", "21600"))  # 6 hours
MARKET_MODE = os.getenv("MARKET_MODE", "api")  # api | msp_only

# ---------------------------------------------------------------------------
# Yield Model
# ---------------------------------------------------------------------------
YIELD_MODEL_DIR = os.getenv("YIELD_MODEL_DIR", "models")

# ---------------------------------------------------------------------------
# Pagination defaults
# ---------------------------------------------------------------------------
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
