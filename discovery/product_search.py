"""RapidAPI product search - Amazon, Alibaba, and general product APIs."""

import os
from typing import List, Dict, Any
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class ProductSearchService:
    """Searches RapidAPI product databases for real supplier products."""

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY", "")
        self.timeout = 10.0

    async def search_amazon(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Amazon product data via RapidAPI."""
        if not self.api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://real-time-amazon-data.p.rapidapi.com/search",
                    params={"query": query, "country": "US", "page": "1"},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    products = data.get("data", {}).get("products", [])[:max_results]
                    return [
                        {
                            "name": p.get("product_title", ""),
                            "price": p.get("product_price", ""),
                            "rating": p.get("product_star_rating", ""),
                            "url": p.get("product_url", ""),
                            "source": "amazon",
                        }
                        for p in products
                    ]
        except Exception as e:
            logger.warning(f"Amazon search failed for '{query}': {e}")
        return []

    async def search_alibaba(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Alibaba via RapidAPI."""
        if not self.api_key:
            return []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://alibaba-1688-taobao-pinduoduo-data.p.rapidapi.com/alibaba/searchItems",
                    params={"keyword": query, "page": "1"},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "alibaba-1688-taobao-pinduoduo-data.p.rapidapi.com",
                    },
                )
                if resp.status_code == 200:
                    items = resp.json().get("result", [])[:max_results]
                    return [
                        {
                            "name": item.get("title", ""),
                            "price": item.get("price", ""),
                            "supplier": item.get("sellerName", ""),
                            "location": item.get("sellerProvince", "China"),
                            "source": "alibaba",
                        }
                        for item in items
                    ]
        except Exception as e:
            logger.warning(f"Alibaba search failed for '{query}': {e}")
        return []

    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Aggregate search across all product APIs."""
        amazon = await self.search_amazon(query)
        alibaba = await self.search_alibaba(query)
        all_products = amazon + alibaba
        logger.info(f"Product search '{query}': {len(all_products)} results")
        return all_products
