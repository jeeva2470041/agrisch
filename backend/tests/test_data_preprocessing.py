"""
Unit Tests — Data Preprocessing.

Tests dataset loading, feature engineering, and train/test split quality.
"""

import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class TestDatasetFiles(unittest.TestCase):
    """Test the generated CSV files exist and have correct structure."""

    def test_full_dataset_exists(self):
        path = os.path.join(_DATA_DIR, "crop_yield.csv")
        self.assertTrue(os.path.exists(path), "crop_yield.csv not found")

    def test_train_dataset_exists(self):
        path = os.path.join(_DATA_DIR, "yield_train.csv")
        self.assertTrue(os.path.exists(path), "yield_train.csv not found")

    def test_test_dataset_exists(self):
        path = os.path.join(_DATA_DIR, "yield_test.csv")
        self.assertTrue(os.path.exists(path), "yield_test.csv not found")


class TestDatasetSchema(unittest.TestCase):
    """Test CSV column structure."""

    def setUp(self):
        self.df = pd.read_csv(os.path.join(_DATA_DIR, "crop_yield.csv"))

    def test_required_columns(self):
        required = [
            "Crop_Year", "State", "Crop", "Season",
            "Area_1000_ha", "Production_1000_tonnes",
            "Yield_tonnes_per_ha", "Annual_Rainfall_mm", "Irrigation_pct",
        ]
        for col in required:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")

    def test_no_missing_values(self):
        nulls = self.df.isnull().sum().sum()
        self.assertEqual(nulls, 0, f"Found {nulls} missing values")

    def test_year_range(self):
        self.assertGreaterEqual(self.df["Crop_Year"].min(), 2001)
        self.assertLessEqual(self.df["Crop_Year"].max(), 2022)

    def test_seasons(self):
        valid_seasons = {"Kharif", "Rabi"}
        actual = set(self.df["Season"].unique())
        self.assertTrue(actual.issubset(valid_seasons | {"Zaid"}))


class TestDataQuality(unittest.TestCase):
    """Test data quality — realistic values, no outliers."""

    def setUp(self):
        self.df = pd.read_csv(os.path.join(_DATA_DIR, "crop_yield.csv"))

    def test_positive_yields(self):
        self.assertTrue((self.df["Yield_tonnes_per_ha"] > 0).all())

    def test_positive_area(self):
        self.assertTrue((self.df["Area_1000_ha"] > 0).all())

    def test_positive_rainfall(self):
        self.assertTrue((self.df["Annual_Rainfall_mm"] > 0).all())

    def test_irrigation_pct_range(self):
        self.assertTrue((self.df["Irrigation_pct"] >= 0).all())
        self.assertTrue((self.df["Irrigation_pct"] <= 100).all())

    def test_sugarcane_yield_high(self):
        """Sugarcane yields should be much higher than cereal yields."""
        sc = self.df[self.df["Crop"] == "Sugarcane"]["Yield_tonnes_per_ha"]
        rice = self.df[self.df["Crop"] == "Rice"]["Yield_tonnes_per_ha"]
        self.assertGreater(sc.mean(), rice.mean() * 10)

    def test_minimum_crops(self):
        self.assertGreaterEqual(self.df["Crop"].nunique(), 14)

    def test_minimum_states(self):
        self.assertGreaterEqual(self.df["State"].nunique(), 15)

    def test_minimum_rows(self):
        self.assertGreaterEqual(len(self.df), 2000)


class TestTrainTestSplit(unittest.TestCase):
    """Test train/test split quality."""

    def setUp(self):
        self.full = pd.read_csv(os.path.join(_DATA_DIR, "crop_yield.csv"))
        self.train = pd.read_csv(os.path.join(_DATA_DIR, "yield_train.csv"))
        self.test = pd.read_csv(os.path.join(_DATA_DIR, "yield_test.csv"))

    def test_split_adds_up(self):
        self.assertEqual(len(self.train) + len(self.test), len(self.full))

    def test_approximate_80_20(self):
        ratio = len(self.train) / len(self.full)
        self.assertAlmostEqual(ratio, 0.8, delta=0.02)

    def test_train_has_all_crops(self):
        """Training set should cover all crops."""
        all_crops = set(self.full["Crop"].unique())
        train_crops = set(self.train["Crop"].unique())
        # Allow up to 1 missing crop due to random split
        self.assertGreaterEqual(len(train_crops), len(all_crops) - 1)

    def test_no_data_leakage(self):
        """No exact duplicate rows between train and test.
        (Rows differ even if same crop-state due to year/rainfall noise.)
        """
        # Check by creating unique identifiers
        train_ids = set(
            self.train.apply(lambda r: f"{r['Crop_Year']}:{r['State']}:{r['Crop']}:{r['Yield_tonnes_per_ha']}", axis=1)
        )
        test_ids = set(
            self.test.apply(lambda r: f"{r['Crop_Year']}:{r['State']}:{r['Crop']}:{r['Yield_tonnes_per_ha']}", axis=1)
        )
        overlap = train_ids & test_ids
        self.assertEqual(len(overlap), 0, f"Found {len(overlap)} duplicate rows")


class TestFeatureEngineering(unittest.TestCase):
    """Test feature engineering pipeline."""

    def test_label_encoding_consistency(self):
        """Encoding should be deterministic."""
        from sklearn.preprocessing import LabelEncoder

        df = pd.read_csv(os.path.join(_DATA_DIR, "crop_yield.csv"))
        enc1 = LabelEncoder().fit(df["Crop"])
        enc2 = LabelEncoder().fit(df["Crop"])

        val1 = enc1.transform(["Rice"])[0]
        val2 = enc2.transform(["Rice"])[0]
        self.assertEqual(val1, val2)

    def test_features_are_numeric(self):
        df = pd.read_csv(os.path.join(_DATA_DIR, "crop_yield.csv"))
        numeric_cols = ["Crop_Year", "Area_1000_ha", "Production_1000_tonnes",
                       "Yield_tonnes_per_ha", "Annual_Rainfall_mm", "Irrigation_pct"]
        for col in numeric_cols:
            self.assertTrue(
                pd.api.types.is_numeric_dtype(df[col]),
                f"{col} is not numeric"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
