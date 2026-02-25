"""
AgriScheme Backend — Market Price Forecasting Service.
Uses Facebook Prophet for time-series forecasting of crop market prices.
Generates synthetic historical data from base MSP prices and forecasts
7 days ahead to help farmers identify the best selling window.

Falls back to simple statistical forecasting if Prophet is unavailable.
"""
import logging
import math
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try importing Prophet; fall back gracefully
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
    logger.info("Prophet is available for forecasting.")
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not installed. Using statistical fallback for forecasting.")

# Base prices (same as market_service.py)
_BASE_PRICES = {
    "Rice":       2320,
    "Wheat":      2275,
    "Maize":      2090,
    "Cotton":     7121,
    "Sugarcane":  315,
    "Soybean":    4892,
    "Groundnut":  6783,
    "Mustard":    5650,
    "Jowar":      3371,
    "Bajra":      2625,
    "Ragi":       4290,
    "Tur":        7550,
    "Moong":      8682,
    "Urad":       7400,
    "Coconut":    3400,
    "Tea":        22000,
    "Coffee":     29400,
    "Jute":       5050,
    "Tobacco":    7600,
    "Rubber":     17200,
    "Millets":    2625,
    "Pulses":     7400,
    "Sunflower":  7280,
    "Spices":     32000,
}


def _generate_historical_prices(base_price: float, days: int = 60) -> list:
    """Generate synthetic but realistic historical daily prices.

    Creates a time series with:
    - Weekly seasonality (±3%)
    - Random daily noise (±2%)
    - Slow trend drift (±5% over period)
    """
    import pandas as pd

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    history = []
    trend = random.uniform(-0.03, 0.03)  # Overall trend

    for i in range(days):
        date = start_date + timedelta(days=i)

        # Trend component
        trend_factor = 1 + (trend * i / days)

        # Weekly seasonality (markets are busier mid-week)
        day_of_week = date.weekday()
        weekly_factor = 1 + 0.03 * math.sin(2 * math.pi * day_of_week / 7)

        # Random noise
        random.seed(date.year * 10000 + date.month * 100 + date.day + hash(str(base_price)) % 1000)
        noise = random.uniform(-0.02, 0.02)
        random.seed()

        price = base_price * trend_factor * weekly_factor * (1 + noise)
        history.append({
            "ds": date.strftime("%Y-%m-%d"),
            "y": round(price, 0),
        })

    return history


def _forecast_with_prophet(history: list, periods: int = 7) -> list:
    """Forecast using Facebook Prophet."""
    import pandas as pd

    df = pd.DataFrame(history)
    df["ds"] = pd.to_datetime(df["ds"])

    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False,
        changepoint_prior_scale=0.05,
    )
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # Extract only the forecast period
    forecast_rows = forecast.tail(periods)

    results = []
    for _, row in forecast_rows.iterrows():
        results.append({
            "date": row["ds"].strftime("%Y-%m-%d"),
            "predicted_price": round(row["yhat"], 0),
            "lower_bound": round(row["yhat_lower"], 0),
            "upper_bound": round(row["yhat_upper"], 0),
        })

    return results


def _forecast_simple(history: list, periods: int = 7) -> list:
    """Simple statistical forecast using moving average + trend.

    Fallback when Prophet is not available.
    """
    # Use last 14 days for trend calculation
    recent = history[-14:]
    prices = [h["y"] for h in recent]

    # Moving average
    ma = sum(prices) / len(prices)

    # Simple linear trend (slope)
    n = len(prices)
    if n > 1:
        x_mean = (n - 1) / 2
        y_mean = ma
        numerator = sum((i - x_mean) * (prices[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
    else:
        slope = 0

    last_date = datetime.strptime(history[-1]["ds"], "%Y-%m-%d")
    last_price = prices[-1]

    results = []
    for d in range(1, periods + 1):
        date = last_date + timedelta(days=d)
        predicted = last_price + slope * d

        # Add uncertainty bounds (±3% widening)
        margin = predicted * 0.03 * (d ** 0.5)
        results.append({
            "date": date.strftime("%Y-%m-%d"),
            "predicted_price": round(predicted, 0),
            "lower_bound": round(predicted - margin, 0),
            "upper_bound": round(predicted + margin, 0),
        })

    return results


def get_price_forecast(crop: str, days_history: int = 60,
                       forecast_days: int = 7) -> dict:
    """Get price forecast for a crop.

    Args:
        crop: Crop name (must be in _BASE_PRICES).
        days_history: Number of historical days to generate.
        forecast_days: Number of days to forecast.

    Returns:
        dict with historical prices, forecast, and metadata.
    """
    if crop not in _BASE_PRICES:
        return {"error": f"Unknown crop: {crop}. Available: {list(_BASE_PRICES.keys())}"}

    base_price = _BASE_PRICES[crop]

    try:
        # Generate historical data
        history = _generate_historical_prices(base_price, days_history)

        # Forecast
        if PROPHET_AVAILABLE:
            forecast = _forecast_with_prophet(history, forecast_days)
            method = "prophet"
        else:
            forecast = _forecast_simple(history, forecast_days)
            method = "statistical"

        # Calculate trend
        first_price = history[0]["y"]
        last_price = history[-1]["y"]
        trend_pct = round((last_price - first_price) / first_price * 100, 1)

        # Best selling day recommendation
        best_day = max(forecast, key=lambda x: x["predicted_price"])

        return {
            "crop": crop,
            "base_msp": base_price,
            "unit": "₹/quintal",
            "method": method,
            "historical": history[-14:],  # Last 14 days only for response
            "forecast": forecast,
            "trend_pct": trend_pct,
            "trend": "up" if trend_pct > 1 else ("down" if trend_pct < -1 else "stable"),
            "best_selling_day": best_day["date"],
            "best_predicted_price": best_day["predicted_price"],
        }

    except Exception as e:
        logger.error("Forecast error for %s: %s", crop, e)
        return {"error": f"Forecasting failed: {e}"}
