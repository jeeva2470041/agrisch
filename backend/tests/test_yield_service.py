"""
Unit Tests — Yield Prediction Service.

Tests the production yield predictor:
  1. Model loading from disk
  2. Prediction accuracy and output format
  3. Input validation (unknown crops/states/seasons)
  4. Confidence intervals
  5. Fallback mechanism
  6. Edge cases
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.yield_service import predict_yield, get_predictor, YieldPredictor


class TestModelLoading(unittest.TestCase):
    """Test model loading from disk."""

    def test_predictor_is_trained(self):
        predictor = get_predictor()
        self.assertTrue(predictor._is_trained)

    def test_model_loaded_or_fallback(self):
        predictor = get_predictor()
        self.assertIsNotNone(predictor.model)

    def test_encoders_loaded(self):
        predictor = get_predictor()
        self.assertIsNotNone(predictor.crop_encoder)
        self.assertIsNotNone(predictor.state_encoder)
        self.assertIsNotNone(predictor.season_encoder)

    def test_singleton_pattern(self):
        p1 = get_predictor()
        p2 = get_predictor()
        self.assertIs(p1, p2)


class TestPredictionOutput(unittest.TestCase):
    """Test prediction output format and values."""

    def test_valid_prediction_structure(self):
        result = predict_yield("Rice", "Tamil Nadu", "Kharif")
        self.assertIn("crop", result)
        self.assertIn("state", result)
        self.assertIn("season", result)
        self.assertIn("predicted_yield", result)
        self.assertIn("yield_unit", result)
        self.assertIn("lower_bound", result)
        self.assertIn("upper_bound", result)
        self.assertIn("category", result)
        self.assertIn("model", result)
        self.assertNotIn("error", result)

    def test_yield_is_positive(self):
        result = predict_yield("Wheat", "Punjab", "Rabi")
        self.assertGreater(result["predicted_yield"], 0)

    def test_confidence_interval(self):
        result = predict_yield("Rice", "Tamil Nadu", "Kharif")
        self.assertLessEqual(result["lower_bound"], result["predicted_yield"])
        self.assertGreaterEqual(result["upper_bound"], result["predicted_yield"])

    def test_category_values(self):
        result = predict_yield("Cotton", "Gujarat", "Kharif")
        self.assertIn(result["category"], ["above_average", "below_average", "average"])

    def test_model_type(self):
        result = predict_yield("Maize", "Karnataka", "Kharif")
        self.assertEqual(result["model"], "RandomForest")

    def test_custom_rainfall(self):
        result = predict_yield("Rice", "Punjab", "Kharif", rainfall=500)
        self.assertEqual(result["rainfall_mm"], 500)
        self.assertNotIn("error", result)


class TestPredictionReasonableness(unittest.TestCase):
    """Test that predictions are in reasonable ranges."""

    def test_rice_yield_range(self):
        result = predict_yield("Rice", "Punjab", "Kharif")
        # Punjab rice: should be 3-6 t/ha
        self.assertGreater(result["predicted_yield"], 2.0)
        self.assertLess(result["predicted_yield"], 7.0)

    def test_wheat_yield_range(self):
        result = predict_yield("Wheat", "Punjab", "Rabi")
        # Punjab wheat: should be 3.5-6.5 t/ha
        self.assertGreater(result["predicted_yield"], 2.5)
        self.assertLess(result["predicted_yield"], 8.0)

    def test_sugarcane_yield_range(self):
        result = predict_yield("Sugarcane", "Tamil Nadu", "Kharif")
        # Tamil Nadu sugarcane: should be 70-130 t/ha
        self.assertGreater(result["predicted_yield"], 50.0)
        self.assertLess(result["predicted_yield"], 150.0)

    def test_cotton_yield_range(self):
        result = predict_yield("Cotton", "Gujarat", "Kharif")
        # Gujarat cotton: should be 0.5-3.5 t/ha
        self.assertGreater(result["predicted_yield"], 0.3)
        self.assertLess(result["predicted_yield"], 5.0)

    def test_high_rainfall_doesnt_crash(self):
        result = predict_yield("Rice", "Tamil Nadu", "Kharif", rainfall=5000)
        self.assertNotIn("error", result)
        self.assertGreater(result["predicted_yield"], 0)

    def test_low_rainfall_doesnt_crash(self):
        result = predict_yield("Wheat", "Rajasthan", "Rabi", rainfall=10)
        self.assertNotIn("error", result)
        self.assertGreater(result["predicted_yield"], 0)


class TestInputValidation(unittest.TestCase):
    """Test error handling for invalid inputs."""

    def test_unknown_crop(self):
        result = predict_yield("Banana", "Tamil Nadu", "Kharif")
        self.assertIn("error", result)
        self.assertIn("Unknown crop", result["error"])

    def test_unknown_state(self):
        result = predict_yield("Rice", "Atlantis", "Kharif")
        self.assertIn("error", result)
        self.assertIn("Unknown state", result["error"])

    def test_unknown_season(self):
        result = predict_yield("Rice", "Tamil Nadu", "Winter")
        self.assertIn("error", result)
        self.assertIn("Unknown season", result["error"])

    def test_none_rainfall_uses_default(self):
        result = predict_yield("Rice", "Tamil Nadu", "Kharif", rainfall=None)
        self.assertNotIn("error", result)
        self.assertGreater(result["rainfall_mm"], 0)


class TestMultipleCrops(unittest.TestCase):
    """Test predictions across many crop-state combinations."""

    def test_all_major_crops(self):
        crops_states = [
            ("Rice", "Tamil Nadu", "Kharif"),
            ("Wheat", "Punjab", "Rabi"),
            ("Cotton", "Maharashtra", "Kharif"),
            ("Sugarcane", "Uttar Pradesh", "Kharif"),
            ("Maize", "Karnataka", "Kharif"),
            ("Soybean", "Madhya Pradesh", "Kharif"),
            ("Groundnut", "Gujarat", "Kharif"),
            ("Pulses", "Madhya Pradesh", "Rabi"),
            ("Millets", "Rajasthan", "Kharif"),
        ]
        for crop, state, season in crops_states:
            result = predict_yield(crop, state, season)
            self.assertNotIn("error", result, f"Failed for {crop}/{state}/{season}")
            self.assertGreater(result["predicted_yield"], 0,
                             f"Zero yield for {crop}/{state}/{season}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
