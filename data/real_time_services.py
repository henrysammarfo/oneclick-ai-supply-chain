"""Wrappers for real-time external services with caching."""

import os
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

_cache: Dict[str, Any] = {}


class RealTimeServices:
    """Cached wrappers for exchange rate and geocoding APIs."""

    def __init__(self):
        self.exchange_key = os.getenv("EXCHANGE_RATE_API_KEY", "")
        self.geocoding_key = os.getenv("GEOCODING_API_KEY", "")

    async def get_exchange_rate(self, from_cur: str, to_cur: str = "USD") -> float:
        """Get exchange rate with caching."""
        key = f"fx:{from_cur}:{to_cur}"
        if key in _cache:
            return _cache[key]
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    f"https://v6.exchangerate-api.com/v6/{self.exchange_key}/pair/{from_cur}/{to_cur}"
                )
                if resp.status_code == 200:
                    rate = resp.json().get("conversion_rate", 1.0)
                    _cache[key] = rate
                    return rate
        except Exception as e:
            logger.warning(f"Exchange rate API error: {e}")
        # Fallback rates
        fallbacks = {"EUR": 1.08, "GBP": 1.27, "JPY": 0.0067, "CNY": 0.14, "KRW": 0.00075, "INR": 0.012}
        return fallbacks.get(from_cur, 1.0)

    async def geocode(self, query: str) -> Optional[Dict[str, float]]:
        """Geocode a location string."""
        key = f"geo:{query}"
        if key in _cache:
            return _cache[key]
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    "https://api.opencagedata.com/geocode/v1/json",
                    params={"q": query, "key": self.geocoding_key, "limit": 1},
                )
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        geo = results[0]["geometry"]
                        result = {"lat": geo["lat"], "lng": geo["lng"]}
                        _cache[key] = result
                        return result
        except Exception as e:
            logger.warning(f"Geocoding API error: {e}")
        return None

    @staticmethod
    def get_current_timestamp() -> str:
        """UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()
