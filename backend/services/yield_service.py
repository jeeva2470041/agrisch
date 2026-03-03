"""
AgriScheme Backend — Crop Yield Prediction Service (Production).

Loads a pre-trained RandomForest model from disk (models/yield_model.pkl)
and predicts crop yield based on crop, state, season, rainfall, and irrigation.

The model is trained on real ICRISAT/DES published statistics (2001-2022).
Run `python scripts/train_yield_model.py` to retrain.

Falls back to a lightweight in-memory model if the pre-trained model is missing.
"""

import os
import pickle
import logging

import numpy as np

logger = logging.getLogger(__name__)

# Paths
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BACKEND_DIR, "models", "yield_model.pkl")
_ENCODER_PATH = os.path.join(_BACKEND_DIR, "models", "yield_encoders.pkl")

# Typical rainfall by (state, season) — from IMD normals (mm)
_TYPICAL_RAINFALL = {
    ("Tamil Nadu", "Kharif"): 450, ("Tamil Nadu", "Rabi"): 400,
    ("Kerala", "Kharif"): 2200, ("Karnataka", "Kharif"): 750,
    ("Karnataka", "Rabi"): 150,
    ("Maharashtra", "Kharif"): 750, ("Maharashtra", "Rabi"): 50,
    ("Punjab", "Kharif"): 700, ("Punjab", "Rabi"): 150,
    ("Haryana", "Kharif"): 600, ("Haryana", "Rabi"): 120,
    ("Uttar Pradesh", "Kharif"): 900, ("Uttar Pradesh", "Rabi"): 200,
    ("Madhya Pradesh", "Kharif"): 950, ("Madhya Pradesh", "Rabi"): 100,
    ("Rajasthan", "Kharif"): 450, ("Rajasthan", "Rabi"): 35,
    ("Gujarat", "Kharif"): 650, ("Gujarat", "Rabi"): 30,
    ("West Bengal", "Kharif"): 1200, ("West Bengal", "Rabi"): 90,
    ("Bihar", "Kharif"): 1000, ("Bihar", "Rabi"): 80,
    ("Andhra Pradesh", "Kharif"): 600, ("Andhra Pradesh", "Rabi"): 200,
    ("Telangana", "Kharif"): 750, ("Telangana", "Rabi"): 120,
    ("Odisha", "Kharif"): 1300,
    ("Assam", "Kharif"): 1800,
    ("Jharkhand", "Kharif"): 1150,
    ("Chhattisgarh", "Kharif"): 1250,
    ("Uttarakhand", "Rabi"): 130,
    ("Goa", "Kharif"): 2500,
}

# Average irrigation % by (state, season) — DES estimates
_TYPICAL_IRRIGATION = {
    ("Punjab", "Kharif"): 99, ("Punjab", "Rabi"): 99,
    ("Haryana", "Kharif"): 98, ("Haryana", "Rabi"): 98,
    ("Tamil Nadu", "Kharif"): 95, ("Tamil Nadu", "Rabi"): 97,
    ("Andhra Pradesh", "Kharif"): 70, ("Andhra Pradesh", "Rabi"): 90,
    ("Uttar Pradesh", "Kharif"): 75, ("Uttar Pradesh", "Rabi"): 85,
    ("Karnataka", "Kharif"): 40, ("Karnataka", "Rabi"): 30,
    ("Maharashtra", "Kharif"): 20, ("Maharashtra", "Rabi"): 50,
    ("Gujarat", "Kharif"): 45, ("Gujarat", "Rabi"): 80,
    ("Madhya Pradesh", "Kharif"): 25, ("Madhya Pradesh", "Rabi"): 55,
    ("West Bengal", "Kharif"): 35, ("West Bengal", "Rabi"): 50,
    ("Bihar", "Kharif"): 55, ("Bihar", "Rabi"): 70,
    ("Rajasthan", "Kharif"): 25, ("Rajasthan", "Rabi"): 75,
    ("Telangana", "Kharif"): 60, ("Telangana", "Rabi"): 50,
    ("Kerala", "Kharif"): 30,
    ("Odisha", "Kharif"): 30,
    ("Chhattisgarh", "Kharif"): 25,
    ("Assam", "Kharif"): 10,
    ("Jharkhand", "Kharif"): 15,
    ("Uttarakhand", "Rabi"): 70,
    ("Goa", "Kharif"): 15,
}

# Average yield reference (for category classification)
_AVG_YIELDS = {
    "Rice": 2.8, "Wheat": 3.5, "Maize": 3.0, "Cotton": 1.5,
    "Sugarcane": 75.0, "Soybean": 1.1, "Groundnut": 1.6,
    "Oilseeds": 1.2, "Pulses": 0.75, "Coconut": 9.5,
    "Tea": 1.9, "Coffee": 0.9, "Jute": 2.4, "Millets": 1.2,
    "Spices": 1.9, "Fruits": 12.0, "Vegetables": 16.0, "Tobacco": 1.5,
}


class YieldPredictor:
    """Production-ready yield predictor using pre-trained RandomForest."""

    def __init__(self):
        self.model = None
        self.encoders = None
        self._is_trained = False
        self._load_model()

    def _load_model(self):
        """Load pre-trained model and encoders from disk."""
        if not os.path.exists(_MODEL_PATH) or not os.path.exists(_ENCODER_PATH):
            logger.warning(
                "Pre-trained model not found at %s. "
                "Run: python scripts/train_yield_model.py",
                _MODEL_PATH,
            )
            self._train_fallback()
            return

        try:
            with open(_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(_ENCODER_PATH, "rb") as f:
                self.encoders = pickle.load(f)

            self.crop_encoder = self.encoders["crop_encoder"]
            self.state_encoder = self.encoders["state_encoder"]
            self.season_encoder = self.encoders["season_encoder"]
            self._is_trained = True

            metrics = self.encoders.get("metrics", {})
            r2 = metrics.get("test_r2", "N/A")
            logger.info(
                "Yield model loaded from disk. Test R²=%.4f, Crops=%d, States=%d",
                r2 if isinstance(r2, float) else 0,
                len(self.crop_encoder.classes_),
                len(self.state_encoder.classes_),
            )
        except Exception as e:
            logger.error("Failed to load yield model: %s", e)
            self._train_fallback()

    def _train_fallback(self):
        """Train a lightweight in-memory model as fallback."""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import LabelEncoder

            logger.info("Training fallback yield model in memory...")

            # Minimal dataset — just enough for reasonable predictions
            data = [
                ("Rice", "Tamil Nadu", "Kharif", 450, 95, 3.9),
                ("Rice", "Punjab", "Kharif", 700, 99, 4.5),
                ("Rice", "West Bengal", "Kharif", 1200, 35, 2.9),
                ("Rice", "Bihar", "Kharif", 1000, 55, 2.3),
                ("Wheat", "Punjab", "Rabi", 150, 99, 5.2),
                ("Wheat", "Uttar Pradesh", "Rabi", 200, 88, 3.5),
                ("Wheat", "Madhya Pradesh", "Rabi", 100, 72, 2.9),
                ("Cotton", "Gujarat", "Kharif", 650, 50, 1.9),
                ("Cotton", "Maharashtra", "Kharif", 750, 10, 1.3),
                ("Sugarcane", "Tamil Nadu", "Kharif", 500, 99, 108.0),
                ("Sugarcane", "Maharashtra", "Kharif", 700, 92, 85.0),
                ("Maize", "Karnataka", "Kharif", 750, 30, 3.8),
                ("Groundnut", "Gujarat", "Kharif", 550, 40, 1.8),
                ("Soybean", "Madhya Pradesh", "Kharif", 950, 5, 1.2),
                ("Pulses", "Madhya Pradesh", "Rabi", 50, 20, 0.9),
                ("Millets", "Rajasthan", "Kharif", 380, 5, 1.2),
            ]

            import pandas as pd
            crops = [d[0] for d in data]
            states = [d[1] for d in data]
            seasons = [d[2] for d in data]

            self.crop_encoder = LabelEncoder().fit(list(set(crops)))
            self.state_encoder = LabelEncoder().fit(list(set(states)))
            self.season_encoder = LabelEncoder().fit(list(set(seasons)))

            X = []
            y = []
            for crop, state, season, rain, irr, yld in data:
                X.append([
                    2022,  # year
                    rain,
                    irr,
                    self.crop_encoder.transform([crop])[0],
                    self.state_encoder.transform([state])[0],
                    self.season_encoder.transform([season])[0],
                ])
                y.append(yld)

            self.model = RandomForestRegressor(
                n_estimators=50, max_depth=10, random_state=42
            )
            self.model.fit(np.array(X), np.array(y))
            self._is_trained = True
            self.encoders = {"feature_order": [
                "Crop_Year", "Annual_Rainfall_mm", "Irrigation_pct",
                "Crop_enc", "State_enc", "Season_enc",
            ]}
            logger.info("Fallback yield model trained (limited accuracy).")
        except Exception as e:
            logger.error("Fallback training also failed: %s", e)
            self._is_trained = False

    def predict(self, crop: str, state: str, season: str,
                rainfall: float = None) -> dict:
        """Predict crop yield.

        Args:
            crop: Crop name (e.g., "Rice", "Wheat").
            state: Indian state name.
            season: "Kharif", "Rabi", or "Zaid".
            rainfall: Expected rainfall in mm (uses typical if None).

        Returns:
            dict with predicted yield, confidence interval, and metadata.
        """
        if not self._is_trained:
            return {"error": "Model not trained. Run: python scripts/train_yield_model.py"}

        # Validate crop
        try:
            crop_enc = self.crop_encoder.transform([crop])[0]
        except ValueError:
            known = sorted(list(self.crop_encoder.classes_))
            return {"error": f"Unknown crop '{crop}'. Known: {known}"}

        # Validate state
        try:
            state_enc = self.state_encoder.transform([state])[0]
        except ValueError:
            known = sorted(list(self.state_encoder.classes_))
            return {"error": f"Unknown state '{state}'. Known: {known}"}

        # Validate season
        try:
            season_enc = self.season_encoder.transform([season])[0]
        except ValueError:
            return {"error": f"Unknown season '{season}'. Must be Kharif, Rabi, or Zaid."}

        # Default values
        if rainfall is None:
            rainfall = _TYPICAL_RAINFALL.get((state, season), 800)

        irrigation = _TYPICAL_IRRIGATION.get((state, season), 40)
        current_year = 2024  # Use recent year for prediction

        # Feature vector: [Year, Rainfall, Irrigation%, Crop, State, Season]
        X_input = np.array([[current_year, rainfall, irrigation,
                             crop_enc, state_enc, season_enc]])

        predicted_yield = float(self.model.predict(X_input)[0])
        predicted_yield = max(0.01, predicted_yield)  # Floor at 0.01

        # Confidence interval from tree predictions
        tree_predictions = [
            float(tree.predict(X_input)[0]) for tree in self.model.estimators_
        ]
        lower = max(0.01, float(np.percentile(tree_predictions, 10)))
        upper = float(np.percentile(tree_predictions, 90))

        # Ensure bounds always contain the prediction
        lower = min(lower, predicted_yield)
        upper = max(upper, predicted_yield)

        # Category vs national average
        avg = _AVG_YIELDS.get(crop, predicted_yield)
        if predicted_yield > avg * 1.1:
            category = "above_average"
        elif predicted_yield < avg * 0.9:
            category = "below_average"
        else:
            category = "average"

        return {
            "crop": crop,
            "state": state,
            "season": season,
            "rainfall_mm": round(rainfall, 0),
            "predicted_yield": round(predicted_yield, 2),
            "yield_unit": "tonnes/hectare",
            "lower_bound": round(lower, 2),
            "upper_bound": round(upper, 2),
            "category": category,
            "average_yield": round(avg, 2),
            "model": "RandomForest",
            "n_estimators": len(self.model.estimators_),
            "data_source": "ICRISAT/DES GOI Statistics (2001-2022)",
        }


# ─── Singleton ────────────────────────────────────────────────────────────

_predictor = None


def get_predictor() -> YieldPredictor:
    """Get or create the singleton YieldPredictor."""
    global _predictor
    if _predictor is None:
        _predictor = YieldPredictor()
    return _predictor


def predict_yield(crop: str, state: str, season: str,
                  rainfall: float = None) -> dict:
    """Convenience function — same API as before."""
    return get_predictor().predict(crop, state, season, rainfall)
