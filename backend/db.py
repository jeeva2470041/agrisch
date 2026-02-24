"""
AgriScheme Backend — MongoDB connection and index management.
Uses a singleton MongoClient with connection pooling.
"""
from pymongo import MongoClient, ASCENDING
from config import MONGO_URI, DB_NAME

# ---------------------------------------------------------------------------
# Singleton client  (connection pooling handled by pymongo driver)
# ---------------------------------------------------------------------------
_client = None


def _get_client():
    """Return a singleton MongoClient instance."""
    global _client
    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            maxPoolSize=50,
            retryWrites=True,
            serverSelectionTimeoutMS=60000, 
            connectTimeoutMS=60000,
            socketTimeoutMS=60000,
        )
    return _client


def get_db():
    """Return the agrischeme database handle."""
    return _get_client()[DB_NAME]


def get_schemes_collection():
    """Convenience helper — returns the schemes collection directly."""
    return get_db()["schemes"]


# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------
def init_indexes():
    """Create indexes for query performance.

    Indexes created:
        - states     (multikey)  — eligibility filter
        - crops      (multikey)  — eligibility filter
        - max_land   (ascending) — range filter
        - min_land   (ascending) — range filter
        - season     (ascending) — optional filter
        - type       (ascending) — optional filter
        - benefit_amount (descending) — sorting
    """
    schemes = get_schemes_collection()

    schemes.create_index([("states", ASCENDING)])
    schemes.create_index([("crops", ASCENDING)])
    schemes.create_index([("min_land", ASCENDING)])
    schemes.create_index([("max_land", ASCENDING)])
    schemes.create_index([("season", ASCENDING)])
    schemes.create_index([("type", ASCENDING)])
    schemes.create_index([("benefit_amount", -1)])

    print("[OK] MongoDB indexes initialized.")
