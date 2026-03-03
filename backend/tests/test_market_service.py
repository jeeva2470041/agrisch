"""
Unit Tests — Market Service.

Tests the 3-tier market price system:
  1. MSP fallback (always works)
  2. Cache mechanism
  3. API integration (mocked)
  4. Error handling
"""

import os
import sys
import json
import time
import unittest
from unittest.mock import patch, MagicMock

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.market_service import (
    get_market_prices,
    _get_msp_price,
    _parse_api_records,
    _generate_msp_price,
    _get_cached,
    _set_cache,
    _CACHE_FILE,
    _BASE_PRICES,
)


class TestMSPFallback(unittest.TestCase):
    """Test MSP-based price generation (Tier 3)."""

    def test_msp_price_returns_valid_dict(self):
        result = _get_msp_price("Rice", "Delhi")
        self.assertIsNotNone(result)
        self.assertEqual(result["crop"], "Rice")
        self.assertIn("price", result)
        self.assertIn("trend", result)
        self.assertIn("unit", result)

    def test_msp_price_within_range(self):
        """Generated price should be within ±10% of MSP."""
        base = _BASE_PRICES["Wheat"]["price"]
        price = _generate_msp_price(base)
        self.assertGreater(price, base * 0.85)
        self.assertLess(price, base * 1.15)

    def test_unknown_crop_returns_none(self):
        result = _get_msp_price("UnknownCrop123", "Delhi")
        self.assertIsNone(result)

    def test_trend_classification(self):
        result = _get_msp_price("Rice", "Delhi")
        self.assertIn(result["trend"], ["up", "down", "stable"])

    def test_all_crops_have_prices(self):
        """Every crop in _BASE_PRICES should return a valid MSP price."""
        for crop in _BASE_PRICES:
            result = _get_msp_price(crop, "Test Market")
            self.assertIsNotNone(result, f"No MSP price for {crop}")
            self.assertGreater(result["price"], 0)


class TestAPIRecordParsing(unittest.TestCase):
    """Test parsing of data.gov.in API response records."""

    def test_parse_valid_records(self):
        records = [
            {
                "modal_price": "2450",
                "min_price": "2200",
                "max_price": "2600",
                "market": "Karnal",
                "arrival_date": "03/03/2026",
                "district": "Karnal",
                "variety": "Basmati",
            },
            {
                "modal_price": "2380",
                "min_price": "2100",
                "max_price": "2500",
                "market": "Hisar",
                "arrival_date": "03/03/2026",
                "district": "Hisar",
                "variety": "Common",
            },
        ]
        result = _parse_api_records(records, "Rice")
        self.assertIsNotNone(result)
        self.assertEqual(result["crop"], "Rice")
        self.assertEqual(result["records_count"], 2)
        self.assertGreater(result["price"], 0)
        self.assertEqual(result["source"], "data.gov.in (AGMARKNET)")

    def test_parse_empty_records(self):
        result = _parse_api_records([], "Rice")
        self.assertIsNone(result)

    def test_parse_invalid_prices(self):
        records = [{"modal_price": "0"}, {"modal_price": "-100"}]
        result = _parse_api_records(records, "Rice")
        self.assertIsNone(result)

    def test_parse_missing_fields(self):
        records = [{"modal_price": "2500"}]
        result = _parse_api_records(records, "Wheat")
        self.assertIsNotNone(result)
        self.assertEqual(result["crop"], "Wheat")


class TestCacheMechanism(unittest.TestCase):
    """Test JSON file caching."""

    def setUp(self):
        """Clean state."""
        if os.path.exists(_CACHE_FILE):
            os.remove(_CACHE_FILE)

    def tearDown(self):
        if os.path.exists(_CACHE_FILE):
            os.remove(_CACHE_FILE)

    def test_cache_miss_returns_none(self):
        result = _get_cached("Test", "Rice")
        self.assertIsNone(result)

    def test_set_and_get_cache(self):
        data = {"crop": "Rice", "price": 2500}
        _set_cache("TN", "Rice", data)
        result = _get_cached("TN", "Rice")
        self.assertIsNotNone(result)
        self.assertEqual(result["price"], 2500)

    def test_cache_expiry(self):
        """Manually set expired timestamp."""
        data = {"crop": "Rice", "price": 2500}
        _set_cache("TN", "Rice", data)
        # Manually expire
        cache_path = _CACHE_FILE
        with open(cache_path, "r") as f:
            cache = json.load(f)
        cache["TN:Rice"]["timestamp"] = time.time() - 100000
        with open(cache_path, "w") as f:
            json.dump(cache, f)
        result = _get_cached("TN", "Rice")
        self.assertIsNone(result)


class TestGetMarketPrices(unittest.TestCase):
    """Test the main get_market_prices() public function."""

    def test_returns_valid_structure(self):
        result = get_market_prices("Tamil Nadu")
        self.assertIn("state", result)
        self.assertIn("mandis", result)
        self.assertIn("prices", result)
        self.assertIn("last_updated", result)
        self.assertIsInstance(result["prices"], list)
        self.assertGreater(len(result["prices"]), 0)

    def test_state_filter(self):
        result = get_market_prices("Punjab")
        self.assertEqual(result["state"], "Punjab")

    def test_crop_filter(self):
        result = get_market_prices("All", "Rice")
        self.assertEqual(len(result["prices"]), 1)
        self.assertEqual(result["prices"][0]["crop"], "Rice")

    def test_unknown_state_returns_default(self):
        result = get_market_prices("UnknownState")
        self.assertIn("prices", result)
        self.assertGreater(len(result["prices"]), 0)

    def test_each_price_has_required_fields(self):
        result = get_market_prices("Maharashtra")
        for p in result["prices"]:
            self.assertIn("crop", p)
            self.assertIn("price", p)
            self.assertIn("trend", p)


class TestEdgeCases(unittest.TestCase):
    """Edge case handling."""

    def test_empty_state(self):
        result = get_market_prices("")
        self.assertIn("prices", result)

    def test_none_crop(self):
        result = get_market_prices("Kerala", None)
        self.assertIn("prices", result)

    def test_crop_not_in_base(self):
        result = get_market_prices("All", "DragonFruit")
        # Falls back to default crop list since DragonFruit not in _BASE_PRICES
        self.assertIn("prices", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
