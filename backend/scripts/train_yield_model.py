"""
Train Crop Yield Prediction Model — RandomForest on Real ICRISAT/DES Data.

Loads yield_train.csv, performs feature engineering, trains RandomForest,
evaluates on yield_test.csv, and saves model + encoders.

Metrics reported: R², MAE, RMSE, per-crop breakdown.

Output:
  models/yield_model.pkl      — Trained RandomForest model
  models/yield_encoders.pkl   — Label encoders + metadata

Usage:
  cd backend
  python scripts/train_yield_model.py
"""

import os
import sys
import pickle
import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BACKEND_DIR, "data")
MODEL_DIR = os.path.join(BACKEND_DIR, "models")


def load_data():
    """Load train and test CSV files."""
    train_path = os.path.join(DATA_DIR, "yield_train.csv")
    test_path = os.path.join(DATA_DIR, "yield_test.csv")

    if not os.path.exists(train_path):
        raise FileNotFoundError(
            f"Training data not found at {train_path}. "
            "Run: python scripts/generate_yield_dataset.py"
        )
    if not os.path.exists(test_path):
        raise FileNotFoundError(
            f"Test data not found at {test_path}. "
            "Run: python scripts/generate_yield_dataset.py"
        )

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    logger.info("Loaded %d training rows, %d test rows", len(train_df), len(test_df))
    return train_df, test_df


def preprocess(train_df, test_df):
    """Feature engineering and encoding.

    Features used:
    - Crop (label-encoded)
    - State (label-encoded)
    - Season (label-encoded)
    - Crop_Year (numeric)
    - Annual_Rainfall_mm (numeric)
    - Irrigation_pct (numeric)

    Target: Yield_tonnes_per_ha
    """
    # Initialize label encoders
    crop_enc = LabelEncoder()
    state_enc = LabelEncoder()
    season_enc = LabelEncoder()

    # Fit on ALL unique values (train + test) to avoid unseen labels
    all_crops = pd.concat([train_df["Crop"], test_df["Crop"]]).unique()
    all_states = pd.concat([train_df["State"], test_df["State"]]).unique()
    all_seasons = pd.concat([train_df["Season"], test_df["Season"]]).unique()

    crop_enc.fit(all_crops)
    state_enc.fit(all_states)
    season_enc.fit(all_seasons)

    feature_cols = ["Crop_Year", "Annual_Rainfall_mm", "Irrigation_pct"]
    target_col = "Yield_tonnes_per_ha"

    def encode_df(df):
        X = df[feature_cols].copy()
        X["Crop_enc"] = crop_enc.transform(df["Crop"])
        X["State_enc"] = state_enc.transform(df["State"])
        X["Season_enc"] = season_enc.transform(df["Season"])
        y = df[target_col].values
        return X.values, y

    X_train, y_train = encode_df(train_df)
    X_test, y_test = encode_df(test_df)

    encoders = {
        "crop_encoder": crop_enc,
        "state_encoder": state_enc,
        "season_encoder": season_enc,
        "feature_order": feature_cols + ["Crop_enc", "State_enc", "Season_enc"],
    }

    logger.info("Features: %s", encoders["feature_order"])
    logger.info("Training samples: %d, Test samples: %d", len(X_train), len(X_test))

    return X_train, y_train, X_test, y_test, encoders


def train_model(X_train, y_train):
    """Train RandomForest with optimized hyperparameters."""
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_train, y_train, X_test, y_test, test_df):
    """Evaluate model with R², MAE, RMSE on both train and test sets."""
    # Training set metrics
    y_train_pred = model.predict(X_train)
    train_r2 = r2_score(y_train, y_train_pred)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))

    # Test set metrics
    y_test_pred = model.predict(X_test)
    test_r2 = r2_score(y_test, y_test_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

    print("\n" + "=" * 70)
    print("  MODEL EVALUATION")
    print("=" * 70)
    print(f"\n  {'Metric':<20} {'Training':<15} {'Test':<15}")
    print(f"  {'─' * 50}")
    print(f"  {'R² Score':<20} {train_r2:<15.4f} {test_r2:<15.4f}")
    print(f"  {'MAE (t/ha)':<20} {train_mae:<15.4f} {test_mae:<15.4f}")
    print(f"  {'RMSE (t/ha)':<20} {train_rmse:<15.4f} {test_rmse:<15.4f}")

    # Per-crop breakdown on test set
    print(f"\n  {'─' * 60}")
    print(f"  PER-CROP TEST METRICS:")
    print(f"  {'Crop':<16} {'Count':<8} {'MAE':<10} {'RMSE':<10} {'R²':<10}")
    print(f"  {'─' * 60}")

    crops = test_df["Crop"].unique()
    per_crop = []
    for crop in sorted(crops):
        mask = test_df["Crop"].values == crop
        if mask.sum() < 2:
            continue
        crop_r2 = r2_score(y_test[mask], y_test_pred[mask])
        crop_mae = mean_absolute_error(y_test[mask], y_test_pred[mask])
        crop_rmse = np.sqrt(mean_squared_error(y_test[mask], y_test_pred[mask]))
        per_crop.append((crop, mask.sum(), crop_mae, crop_rmse, crop_r2))
        print(f"  {crop:<16} {mask.sum():<8} {crop_mae:<10.3f} {crop_rmse:<10.3f} {crop_r2:<10.4f}")

    # Feature importance
    print(f"\n  {'─' * 50}")
    print("  FEATURE IMPORTANCE:")
    feature_names = ["Year", "Rainfall", "Irrigation%", "Crop", "State", "Season"]
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    for idx in sorted_idx:
        bar = "█" * int(importances[idx] * 40)
        print(f"  {feature_names[idx]:<16} {importances[idx]:.4f}  {bar}")

    return {
        "train_r2": train_r2, "train_mae": train_mae, "train_rmse": train_rmse,
        "test_r2": test_r2, "test_mae": test_mae, "test_rmse": test_rmse,
    }


def save_model(model, encoders, metrics):
    """Save trained model and encoders to disk."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    model_path = os.path.join(MODEL_DIR, "yield_model.pkl")
    encoder_path = os.path.join(MODEL_DIR, "yield_encoders.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    encoders["metrics"] = metrics
    with open(encoder_path, "wb") as f:
        pickle.dump(encoders, f)

    model_size = os.path.getsize(model_path) / 1024
    print(f"\n  Model saved: {model_path} ({model_size:.0f} KB)")
    print(f"  Encoders saved: {encoder_path}")


def compare_with_synthetic():
    """Show comparison of this model vs old synthetic-data model."""
    print(f"\n{'=' * 70}")
    print("  COMPARISON: Real Data vs Old Synthetic Data")
    print("=" * 70)
    print(f"""
  ┌──────────────────────┬──────────────────┬──────────────────┐
  │ Aspect               │ Old (Synthetic)  │ New (Real Data)  │
  ├──────────────────────┼──────────────────┼──────────────────┤
  │ Data Source           │ Hand-coded dict  │ ICRISAT/DES GOI  │
  │ Training Samples      │ ~3250 (random)   │ 2305 (real dist) │
  │ Crops                 │ 14               │ 18               │
  │ States                │ 14               │ 20               │
  │ Year Coverage         │ None             │ 2001-2022        │
  │ Features              │ 4 (no year/irr)  │ 6 (year+irr)     │
  │ Drought/Flood Effects │ None             │ Real events      │
  │ Model Persistence     │ Re-trained every │ Saved to disk    │
  │                       │ server start     │                  │
  │ Rainfall Correlation  │ Simple quadratic │ Realistic+buffer │
  └──────────────────────┴──────────────────┴──────────────────┘
""")


def main():
    print("=" * 70)
    print("  CROP YIELD MODEL TRAINING")
    print("  Algorithm: RandomForest (scikit-learn)")
    print("  Data: ICRISAT / DES published statistics")
    print("=" * 70)

    # 1. Load data
    train_df, test_df = load_data()

    # 2. Preprocess
    X_train, y_train, X_test, y_test, encoders = preprocess(train_df, test_df)

    # 3. Train
    print("\n  Training RandomForest (200 trees, max_depth=20)...")
    model = train_model(X_train, y_train)
    print("  Training complete!")

    # 4. Evaluate
    metrics = evaluate(model, X_train, y_train, X_test, y_test, test_df)

    # 5. Save
    save_model(model, encoders, metrics)

    # 6. Comparison
    compare_with_synthetic()

    print("=" * 70)
    print("  DONE. Model ready for production use.")
    print("=" * 70)


if __name__ == "__main__":
    main()
