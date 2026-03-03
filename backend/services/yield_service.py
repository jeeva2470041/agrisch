"""
AgriScheme Backend — Crop Yield Prediction Service.
Uses Random Forest (scikit-learn) to predict expected crop yield
(tonnes/hectare) based on crop, state, season, and rainfall.

Trained on synthetic data modeled after Indian agricultural statistics.
"""
import logging
import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

# ─── Synthetic Training Data ───
# Based on approximate Indian agricultural yield statistics (tonnes/hectare)
_YIELD_DATA = {
    # (crop, state, season): (avg_yield, yield_std)
    ("Rice", "Tamil Nadu", "Kharif"):       (3.8, 0.6),
    ("Rice", "Tamil Nadu", "Rabi"):         (3.5, 0.5),
    ("Rice", "West Bengal", "Kharif"):      (2.9, 0.5),
    ("Rice", "Punjab", "Kharif"):           (4.2, 0.4),
    ("Rice", "Andhra Pradesh", "Kharif"):   (3.5, 0.5),
    ("Rice", "Uttar Pradesh", "Kharif"):    (2.5, 0.6),
    ("Rice", "Bihar", "Kharif"):            (2.1, 0.5),
    ("Rice", "Karnataka", "Kharif"):        (3.0, 0.6),
    ("Rice", "Kerala", "Kharif"):           (2.8, 0.5),
    ("Rice", "Odisha", "Kharif"):           (2.2, 0.6),

    ("Wheat", "Punjab", "Rabi"):            (5.1, 0.4),
    ("Wheat", "Haryana", "Rabi"):           (4.8, 0.5),
    ("Wheat", "Uttar Pradesh", "Rabi"):     (3.4, 0.6),
    ("Wheat", "Madhya Pradesh", "Rabi"):    (3.0, 0.5),
    ("Wheat", "Rajasthan", "Rabi"):         (3.2, 0.6),
    ("Wheat", "Bihar", "Rabi"):             (2.8, 0.5),
    ("Wheat", "Gujarat", "Rabi"):           (3.0, 0.5),

    ("Maize", "Karnataka", "Kharif"):       (3.5, 0.7),
    ("Maize", "Andhra Pradesh", "Kharif"):  (4.0, 0.6),
    ("Maize", "Bihar", "Kharif"):           (3.0, 0.6),
    ("Maize", "Madhya Pradesh", "Kharif"):  (2.5, 0.5),
    ("Maize", "Rajasthan", "Kharif"):       (2.0, 0.6),
    ("Maize", "Uttar Pradesh", "Kharif"):   (2.5, 0.5),

    ("Cotton", "Gujarat", "Kharif"):        (1.8, 0.4),
    ("Cotton", "Maharashtra", "Kharif"):    (1.5, 0.4),
    ("Cotton", "Telangana", "Kharif"):      (1.7, 0.4),
    ("Cotton", "Punjab", "Kharif"):         (2.0, 0.3),
    ("Cotton", "Haryana", "Kharif"):        (1.9, 0.4),
    ("Cotton", "Rajasthan", "Kharif"):      (1.4, 0.4),

    ("Sugarcane", "Uttar Pradesh", "Kharif"): (70.0, 10.0),
    ("Sugarcane", "Maharashtra", "Kharif"):   (80.0, 12.0),
    ("Sugarcane", "Karnataka", "Kharif"):     (85.0, 10.0),
    ("Sugarcane", "Tamil Nadu", "Kharif"):    (105.0, 8.0),
    ("Sugarcane", "Gujarat", "Kharif"):       (72.0, 10.0),

    ("Soybean", "Madhya Pradesh", "Kharif"): (1.2, 0.3),
    ("Soybean", "Maharashtra", "Kharif"):    (1.0, 0.3),
    ("Soybean", "Rajasthan", "Kharif"):      (1.1, 0.3),

    ("Groundnut", "Gujarat", "Kharif"):      (1.8, 0.4),
    ("Groundnut", "Rajasthan", "Kharif"):    (1.5, 0.4),
    ("Groundnut", "Tamil Nadu", "Kharif"):   (2.0, 0.3),
    ("Groundnut", "Andhra Pradesh", "Kharif"): (1.7, 0.3),

    ("Mustard", "Rajasthan", "Rabi"):        (1.3, 0.3),
    ("Mustard", "Madhya Pradesh", "Rabi"):   (1.1, 0.3),
    ("Mustard", "Uttar Pradesh", "Rabi"):    (1.2, 0.3),
    ("Mustard", "Haryana", "Rabi"):          (1.5, 0.3),

    ("Pulses", "Madhya Pradesh", "Rabi"):    (0.9, 0.2),
    ("Pulses", "Rajasthan", "Rabi"):         (0.7, 0.2),
    ("Pulses", "Maharashtra", "Kharif"):     (0.8, 0.2),
    ("Pulses", "Uttar Pradesh", "Rabi"):     (0.9, 0.2),
    ("Pulses", "Karnataka", "Rabi"):         (0.7, 0.2),

    ("Coconut", "Kerala", "Kharif"):         (10.5, 2.0),
    ("Coconut", "Tamil Nadu", "Kharif"):     (11.0, 2.0),
    ("Coconut", "Karnataka", "Kharif"):      (9.0, 2.0),

    ("Tea", "Assam", "Kharif"):              (2.0, 0.3),
    ("Tea", "West Bengal", "Kharif"):        (1.8, 0.3),
    ("Tea", "Kerala", "Kharif"):             (1.7, 0.3),
    ("Tea", "Tamil Nadu", "Kharif"):         (1.9, 0.3),

    ("Coffee", "Karnataka", "Kharif"):       (1.0, 0.2),
    ("Coffee", "Kerala", "Kharif"):          (0.9, 0.2),
    ("Coffee", "Tamil Nadu", "Kharif"):      (0.8, 0.2),

    ("Millets", "Rajasthan", "Kharif"):      (1.2, 0.3),
    ("Millets", "Maharashtra", "Kharif"):    (1.0, 0.3),
    ("Millets", "Karnataka", "Kharif"):      (1.5, 0.3),
    ("Millets", "Tamil Nadu", "Kharif"):     (1.8, 0.4),

    ("Jute", "West Bengal", "Kharif"):       (2.5, 0.4),
    ("Jute", "Bihar", "Kharif"):             (2.2, 0.4),
    ("Jute", "Assam", "Kharif"):             (2.0, 0.4),

    ("Spices", "Kerala", "Kharif"):          (2.5, 0.5),
    ("Spices", "Tamil Nadu", "Kharif"):      (2.0, 0.5),
    ("Spices", "Karnataka", "Kharif"):       (1.8, 0.4),
}

# Typical rainfall by state and season (mm)
_TYPICAL_RAINFALL = {
    ("Tamil Nadu", "Kharif"):     900,
    ("Tamil Nadu", "Rabi"):       400,
    ("Kerala", "Kharif"):         2500,
    ("Karnataka", "Kharif"):      1200,
    ("Maharashtra", "Kharif"):    1100,
    ("Punjab", "Kharif"):         700,
    ("Punjab", "Rabi"):           250,
    ("Haryana", "Kharif"):        600,
    ("Haryana", "Rabi"):          200,
    ("Uttar Pradesh", "Kharif"):  900,
    ("Uttar Pradesh", "Rabi"):    300,
    ("Madhya Pradesh", "Kharif"): 1100,
    ("Madhya Pradesh", "Rabi"):   200,
    ("Rajasthan", "Kharif"):      500,
    ("Rajasthan", "Rabi"):        100,
    ("Gujarat", "Kharif"):        850,
    ("Gujarat", "Rabi"):          150,
    ("West Bengal", "Kharif"):     1600,
    ("Bihar", "Kharif"):          1100,
    ("Bihar", "Rabi"):            200,
    ("Andhra Pradesh", "Kharif"):  900,
    ("Telangana", "Kharif"):      900,
    ("Odisha", "Kharif"):         1400,
    ("Assam", "Kharif"):          2200,
    ("Jharkhand", "Kharif"):      1200,
    ("Chhattisgarh", "Kharif"):   1300,
}


class YieldPredictor:
    """Random Forest-based crop yield predictor."""

    def __init__(self):
        self.model = None
        self.crop_encoder = LabelEncoder()
        self.state_encoder = LabelEncoder()
        self.season_encoder = LabelEncoder()
        self._is_trained = False
        self._train()

    def _generate_training_data(self, n_samples_per_entry: int = 50):
        """Generate synthetic training dataset."""
        X_data = []
        y_data = []

        all_crops = list(set(k[0] for k in _YIELD_DATA.keys()))
        all_states = list(set(k[1] for k in _YIELD_DATA.keys()))
        all_seasons = list(set(k[2] for k in _YIELD_DATA.keys()))

        self.crop_encoder.fit(all_crops)
        self.state_encoder.fit(all_states)
        self.season_encoder.fit(all_seasons)

        for (crop, state, season), (avg_yield, yield_std) in _YIELD_DATA.items():
            typical_rain = _TYPICAL_RAINFALL.get((state, season), 800)

            for _ in range(n_samples_per_entry):
                # Vary rainfall ±30%
                rainfall = typical_rain * np.random.uniform(0.7, 1.3)

                # Yield varies with rainfall (positive correlation up to a point)
                rain_ratio = rainfall / typical_rain
                # Quadratic effect: too much rain also hurts
                rain_effect = -0.5 * (rain_ratio - 1.0) ** 2 + 1.0

                actual_yield = avg_yield * rain_effect + np.random.normal(0, yield_std * 0.5)
                actual_yield = max(0.1, actual_yield)

                crop_enc = self.crop_encoder.transform([crop])[0]
                state_enc = self.state_encoder.transform([state])[0]
                season_enc = self.season_encoder.transform([season])[0]

                X_data.append([crop_enc, state_enc, season_enc, rainfall])
                y_data.append(actual_yield)

        return np.array(X_data), np.array(y_data)

    def _train(self):
        """Train the Random Forest model."""
        try:
            X, y = self._generate_training_data()

            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )
            self.model.fit(X, y)
            self._is_trained = True

            # Log model accuracy
            score = self.model.score(X, y)
            logger.info("Yield model trained. R² score: %.4f", score)

        except Exception as e:
            logger.error("Failed to train yield model: %s", e)
            self._is_trained = False

    def predict(self, crop: str, state: str, season: str,
                rainfall: float = None) -> dict:
        """Predict crop yield.

        Args:
            crop: Crop name.
            state: State name.
            season: Season (Kharif/Rabi/Zaid).
            rainfall: Expected rainfall in mm (optional, uses typical if None).

        Returns:
            dict with prediction results.
        """
        if not self._is_trained:
            return {"error": "Model not trained. Please restart the server."}

        # Validate inputs
        try:
            crop_enc = self.crop_encoder.transform([crop])[0]
        except ValueError:
            known_crops = list(self.crop_encoder.classes_)
            return {"error": f"Unknown crop '{crop}'. Known: {known_crops}"}

        try:
            state_enc = self.state_encoder.transform([state])[0]
        except ValueError:
            known_states = list(self.state_encoder.classes_)
            return {"error": f"Unknown state '{state}'. Known: {known_states}"}

        try:
            season_enc = self.season_encoder.transform([season])[0]
        except ValueError:
            return {"error": f"Unknown season '{season}'. Must be Kharif, Rabi, or Zaid."}

        # Default rainfall
        if rainfall is None:
            rainfall = _TYPICAL_RAINFALL.get((state, season), 800)

        X_input = np.array([[crop_enc, state_enc, season_enc, rainfall]])
        predicted_yield = float(self.model.predict(X_input)[0])

        # Get confidence interval using individual tree predictions
        tree_predictions = [
            tree.predict(X_input)[0] for tree in self.model.estimators_
        ]
        lower = float(np.percentile(tree_predictions, 10))
        upper = float(np.percentile(tree_predictions, 90))

        # Category
        key = (crop, state, season)
        avg_yield = _YIELD_DATA.get(key, (predicted_yield, 0.5))[0]
        if predicted_yield > avg_yield * 1.1:
            category = "above_average"
        elif predicted_yield < avg_yield * 0.9:
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
            "average_yield": round(avg_yield, 2),
            "model": "RandomForest",
            "n_estimators": 100,
        }


# Singleton instance — trained once on import
_predictor = None


def get_predictor() -> YieldPredictor:
    """Get or create the singleton YieldPredictor."""
    global _predictor
    if _predictor is None:
        _predictor = YieldPredictor()
    return _predictor


def predict_yield(crop: str, state: str, season: str,
                  rainfall: float = None) -> dict:
    """Convenience function to predict yield."""
    return get_predictor().predict(crop, state, season, rainfall)
