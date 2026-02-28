"""
AgriScheme Backend — Smart Alerts Service.
Checks weather conditions and market prices to generate alerts for farmers.
Provides weather disaster warnings and price trigger notifications.
"""
import logging
from datetime import datetime
from weather_service import get_weather
from market_service import get_market_prices

logger = logging.getLogger(__name__)

# WMO codes that constitute severe weather
_SEVERE_WEATHER_CODES = {
    65: ("Heavy rain", "high", "Protect crops from waterlogging. Ensure drainage channels are clear."),
    66: ("Freezing rain", "high", "Cover sensitive crops. Avoid irrigation."),
    67: ("Heavy freezing rain", "critical", "Move harvested crops to shelter immediately."),
    75: ("Heavy snow", "critical", "Protect crops with mulching. Avoid field work."),
    82: ("Violent showers", "critical", "Stay indoors. Secure loose farm equipment."),
    86: ("Heavy snow showers", "critical", "Protect livestock and crops from extreme cold."),
    95: ("Thunderstorm", "high", "Avoid open fields. Disconnect electrical equipment."),
    96: ("Thunderstorm with hail", "critical", "Take immediate shelter. Hail can destroy standing crops."),
    99: ("Thunderstorm with heavy hail", "critical", "EMERGENCY: Severe hail warning. Protect all exposed crops and animals."),
}

# Moderate weather alerts
_MODERATE_WEATHER_CODES = {
    55: ("Dense drizzle", "medium", "Monitor soil moisture. Delay fertilizer application."),
    57: ("Dense freezing drizzle", "medium", "Watch for frost damage on crops."),
    63: ("Moderate rain", "low", "Good moisture for crops. Delay spraying if planned."),
    81: ("Moderate showers", "medium", "Check field drainage. Delay harvesting."),
}

# Temperature thresholds for alerts
_TEMP_THRESHOLDS = {
    "extreme_heat": 42.0,   # °C
    "heat_warning": 38.0,
    "frost_warning": 4.0,
    "frost_severe": 0.0,
}


def check_weather_alerts(lat: float, lon: float) -> dict:
    """Check current and forecasted weather for alert conditions.

    Args:
        lat: Latitude.
        lon: Longitude.

    Returns:
        dict with 'alerts' list and 'summary'.
    """
    alerts = []

    try:
        weather = get_weather(lat, lon)
        if not weather:
            return {"alerts": [], "summary": "Could not fetch weather data."}

        current = weather.get("current", {})
        daily = weather.get("daily", [])

        # ── Current weather code alerts ──
        current_code = current.get("weather_code", 0)
        if current_code in _SEVERE_WEATHER_CODES:
            desc, severity, action = _SEVERE_WEATHER_CODES[current_code]
            alerts.append({
                "type": "weather_severe",
                "title": f"⚠️ {desc} - NOW",
                "severity": severity,
                "description": f"Current severe weather: {desc}",
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
            })
        elif current_code in _MODERATE_WEATHER_CODES:
            desc, severity, action = _MODERATE_WEATHER_CODES[current_code]
            alerts.append({
                "type": "weather_moderate",
                "title": f"🌧️ {desc} - NOW",
                "severity": severity,
                "description": f"Current weather condition: {desc}",
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
            })

        # ── Temperature alerts ──
        temp = current.get("temperature", 25)
        if temp >= _TEMP_THRESHOLDS["extreme_heat"]:
            alerts.append({
                "type": "temperature",
                "title": f"🔥 Extreme Heat: {temp}°C",
                "severity": "critical",
                "description": f"Temperature has reached {temp}°C. Extreme heat stress on crops.",
                "action": "Irrigate immediately. Provide shade for nurseries. Avoid fieldwork during 11am-3pm.",
                "timestamp": datetime.utcnow().isoformat(),
            })
        elif temp >= _TEMP_THRESHOLDS["heat_warning"]:
            alerts.append({
                "type": "temperature",
                "title": f"☀️ Heat Warning: {temp}°C",
                "severity": "high",
                "description": f"High temperature of {temp}°C detected.",
                "action": "Increase irrigation frequency. Use mulching to retain moisture.",
                "timestamp": datetime.utcnow().isoformat(),
            })
        elif temp <= _TEMP_THRESHOLDS["frost_severe"]:
            alerts.append({
                "type": "temperature",
                "title": f"❄️ Severe Frost: {temp}°C",
                "severity": "critical",
                "description": f"Temperature has dropped to {temp}°C. Frost damage likely.",
                "action": "Cover crops with plastic/cloth. Light irrigation can prevent frost damage. Smoke/heat near nurseries.",
                "timestamp": datetime.utcnow().isoformat(),
            })
        elif temp <= _TEMP_THRESHOLDS["frost_warning"]:
            alerts.append({
                "type": "temperature",
                "title": f"🥶 Frost Warning: {temp}°C",
                "severity": "high",
                "description": f"Low temperature of {temp}°C. Frost risk tonight.",
                "action": "Cover sensitive crops before sunset. Avoid early morning irrigation.",
                "timestamp": datetime.utcnow().isoformat(),
            })

        # ── Forecast-based alerts (next 5 days) ──
        for day in daily:
            day_code = day.get("weather_code", 0) if isinstance(day, dict) else 0
            day_date = day.get("date", "upcoming") if isinstance(day, dict) else "upcoming"
            precip = day.get("precipitation", 0) if isinstance(day, dict) else 0
            temp_max = day.get("temp_max", 30) if isinstance(day, dict) else 30
            temp_min = day.get("temp_min", 20) if isinstance(day, dict) else 20

            if day_code in _SEVERE_WEATHER_CODES:
                desc, severity, action = _SEVERE_WEATHER_CODES[day_code]
                alerts.append({
                    "type": "weather_forecast",
                    "title": f"📅 {desc} expected on {day_date}",
                    "severity": severity,
                    "description": f"Forecast: {desc} on {day_date}",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat(),
                })

            # Heavy precipitation warning
            if precip > 50:
                alerts.append({
                    "type": "precipitation",
                    "title": f"🌊 Heavy Rain: {precip}mm on {day_date}",
                    "severity": "high" if precip > 100 else "medium",
                    "description": f"Expected {precip}mm rainfall on {day_date}.",
                    "action": "Clear drainage. Delay sowing/harvesting. Protect stored grains.",
                    "timestamp": datetime.utcnow().isoformat(),
                })

            # Extreme temperature forecast
            if temp_max >= _TEMP_THRESHOLDS["extreme_heat"]:
                alerts.append({
                    "type": "temperature_forecast",
                    "title": f"🔥 Extreme heat ({temp_max}°C) on {day_date}",
                    "severity": "high",
                    "description": f"Maximum temperature of {temp_max}°C expected.",
                    "action": "Plan additional irrigation. Avoid transplanting on this day.",
                    "timestamp": datetime.utcnow().isoformat(),
                })

        # ── Build summary ──
        critical_count = sum(1 for a in alerts if a["severity"] == "critical")
        high_count = sum(1 for a in alerts if a["severity"] == "high")

        if critical_count > 0:
            summary = f"🚨 {critical_count} CRITICAL alert(s)! Immediate action required."
        elif high_count > 0:
            summary = f"⚠️ {high_count} high-priority alert(s). Review recommended actions."
        elif alerts:
            summary = f"ℹ️ {len(alerts)} informational alert(s)."
        else:
            summary = "✅ No weather alerts. Conditions look good for farming."

        return {
            "alerts": alerts,
            "summary": summary,
            "checked_at": datetime.utcnow().isoformat(),
            "location": {"lat": lat, "lon": lon},
        }

    except Exception as e:
        logger.error("Weather alert check error: %s", e)
        return {"alerts": [], "summary": f"Alert check failed: {e}"}


def check_price_alerts(state: str, triggers: list) -> dict:
    """Check if any crop prices have crossed farmer-defined thresholds.

    Args:
        state: Indian state name.
        triggers: List of dicts with {crop, threshold_price, direction ('above'/'below')}.

    Returns:
        dict with 'triggered_alerts' list.
    """
    triggered = []

    try:
        market_data = get_market_prices(state)
        if not market_data or "prices" not in market_data:
            return {"triggered_alerts": [], "message": "Could not fetch market prices."}

        # Build a lookup from crop name to current price
        price_map = {}
        for p in market_data["prices"]:
            crop_name = p.get("crop", "").lower()
            price_map[crop_name] = p.get("price", 0)

        for trigger in triggers:
            crop = trigger.get("crop", "")
            threshold = trigger.get("threshold_price", 0)
            direction = trigger.get("direction", "above")

            current_price = price_map.get(crop.lower())
            if current_price is None:
                continue

            if direction == "above" and current_price >= threshold:
                triggered.append({
                    "type": "price_alert",
                    "crop": crop,
                    "current_price": current_price,
                    "threshold": threshold,
                    "direction": direction,
                    "title": f"📈 {crop}: ₹{current_price}/quintal (above ₹{threshold})",
                    "description": f"{crop} price has reached ₹{current_price}/quintal, crossing your threshold of ₹{threshold}.",
                    "action": f"Consider selling your {crop} stock at the current favourable price.",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif direction == "below" and current_price <= threshold:
                triggered.append({
                    "type": "price_alert",
                    "crop": crop,
                    "current_price": current_price,
                    "threshold": threshold,
                    "direction": direction,
                    "title": f"📉 {crop}: ₹{current_price}/quintal (below ₹{threshold})",
                    "description": f"{crop} price has dropped to ₹{current_price}/quintal, below your threshold of ₹{threshold}.",
                    "action": f"Consider holding your {crop} stock and waiting for prices to recover.",
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return {
            "triggered_alerts": triggered,
            "checked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("Price alert check error: %s", e)
        return {"triggered_alerts": [], "message": f"Price check failed: {e}"}
