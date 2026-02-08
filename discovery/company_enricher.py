"""Company enrichment - geocoding and real-time data."""

import os
from typing import Dict, Any, Optional, Tuple
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

_geo_cache: Dict[str, Tuple[float, float]] = {}
_fx_cache: Dict[str, float] = {}


class CompanyEnricher:
    """Enriches supplier data with geocoding and currency info."""

    def __init__(self):
        self.geocoding_key = os.getenv("GEOCODING_API_KEY", "")
        self.exchange_key = os.getenv("EXCHANGE_RATE_API_KEY", "")
        self.timeout = 8.0

    @staticmethod
    def _offline_mode() -> bool:
        flag = os.getenv("OFFLINE_MODE", "").strip().lower()
        return flag in {"1", "true", "yes", "on"}

    async def geocode_company(
        self, company_name: str, location_hint: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Get real lat/lng for a company location."""
        query = f"{company_name} {location_hint}".strip()
        if query in _geo_cache:
            lat, lng = _geo_cache[query]
            return {"lat": lat, "lng": lng}
        if self._offline_mode() or not self.geocoding_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://api.opencagedata.com/geocode/v1/json",
                    params={"q": location_hint or company_name, "key": self.geocoding_key, "limit": 1},
                )
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        geo = results[0]["geometry"]
                        _geo_cache[query] = (geo["lat"], geo["lng"])
                        return {"lat": geo["lat"], "lng": geo["lng"]}
        except Exception as e:
            logger.warning(f"Geocoding failed for '{query}': {e}")
        return None

    async def get_exchange_rate(
        self, from_currency: str, to_currency: str = "USD"
    ) -> float:
        """Get real-time exchange rate."""
        key = f"{from_currency}_{to_currency}"
        if key in _fx_cache:
            return _fx_cache[key]
        if self._offline_mode() or not self.exchange_key:
            return 1.0
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"https://v6.exchangerate-api.com/v6/{self.exchange_key}/pair/{from_currency}/{to_currency}",
                )
                if resp.status_code == 200:
                    rate = resp.json().get("conversion_rate", 1.0)
                    _fx_cache[key] = rate
                    return rate
        except Exception as e:
            logger.warning(f"Exchange rate failed {from_currency}->{to_currency}: {e}")
        return 1.0

    async def enrich_supplier(self, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add geocoding and currency data to a supplier."""
        enriched = {**supplier_data}
        location = supplier_data.get("location", "")
        geo = await self.geocode_company(
            supplier_data.get("company_name", ""), location
        )
        if geo:
            enriched["lat"] = geo["lat"]
            enriched["lng"] = geo["lng"]
        else:
            enriched.setdefault("lat", 0.0)
            enriched.setdefault("lng", 0.0)

        currency = supplier_data.get("currency", "USD")
        if currency != "USD":
            enriched["usd_rate"] = await self.get_exchange_rate(currency, "USD")
        return enriched
