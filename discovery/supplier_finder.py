"""Google Custom Search for finding real supplier companies."""

import os
from typing import List, Dict, Any
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class SupplierFinder:
    """Finds real supplier companies via Google Custom Search."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "")
        self.cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
        self.timeout = 10.0

    async def find_suppliers(
        self, component_name: str, category: str = ""
    ) -> List[Dict[str, Any]]:
        """Search Google for suppliers of a specific component."""
        query = f"{component_name} manufacturer supplier wholesale {category}".strip()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": self.api_key,
                        "cx": self.cx,
                        "q": query,
                        "num": 5,
                    },
                )
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    return self.parse_search_results(items, component_name)
        except Exception as e:
            logger.warning(f"Google search failed for '{component_name}': {e}")
        return []

    def parse_search_results(
        self, results: List[Dict], component: str
    ) -> List[Dict[str, Any]]:
        """Extract supplier info from search results."""
        suppliers = []
        for item in results:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            company = title.split(" - ")[0].split(" | ")[0].strip()
            suppliers.append({
                "company_name": company,
                "description": snippet[:200],
                "website": link,
                "component": component,
                "source": "google_search",
            })
        return suppliers

    def rank_suppliers(self, suppliers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score suppliers by relevance."""
        for s in suppliers:
            score = 0.5
            desc = s.get("description", "").lower()
            if "manufacturer" in desc:
                score += 0.2
            if "wholesale" in desc or "bulk" in desc:
                score += 0.1
            if "iso" in desc or "certified" in desc:
                score += 0.1
            if "years" in desc or "established" in desc:
                score += 0.1
            s["relevance_score"] = round(min(score, 1.0), 2)
        suppliers.sort(key=lambda x: x["relevance_score"], reverse=True)
        return suppliers
