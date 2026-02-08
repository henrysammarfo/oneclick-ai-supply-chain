"""
Universal Discovery Service - Orchestrates supplier discovery from all sources.
Finds REAL suppliers for ANY product using RapidAPI, Google Search, and enrichment.
"""

from typing import List, Dict, Any
from loguru import logger

from .product_search import ProductSearchService
from .supplier_finder import SupplierFinder
from .company_enricher import CompanyEnricher
from data.mock_data import get_mock_suppliers


class UniversalDiscoveryService:
    """
    Discovers real suppliers globally for any product.
    Pipeline: RapidAPI -> Google Search -> Geocode -> Deduplicate -> Rank
    """

    def __init__(self):
        self.product_search = ProductSearchService()
        self.supplier_finder = SupplierFinder()
        self.enricher = CompanyEnricher()

    async def discover_suppliers(
        self,
        product_name: str,
        components: List[Dict[str, Any]],
        region: str = "global",
    ) -> List[Dict[str, Any]]:
        """
        Main discovery pipeline.
        Returns real supplier companies for a product's components.
        """
        logger.info(f"Starting discovery for '{product_name}' ({len(components)} components)")
        suppliers: List[Dict[str, Any]] = []

        for comp in components[:15]:  # Cap for API rate limits
            name = comp.get("name", "")
            category = comp.get("category", "")

            # 1. Search product APIs
            products = await self.product_search.search_products(f"{name} {category}")
            for p in products[:3]:
                suppliers.append({
                    "company_name": p.get("supplier", p.get("name", "")[:50]),
                    "specialization": name,
                    "location": p.get("location", "Unknown"),
                    "source": p.get("source", "api"),
                    "component": name,
                    "estimated_price": self._parse_price(p.get("price", "")),
                })

            # 2. Search Google for specialist suppliers
            google_results = await self.supplier_finder.find_suppliers(name, category)
            ranked = self.supplier_finder.rank_suppliers(google_results)
            for g in ranked[:2]:
                suppliers.append({
                    "company_name": g.get("company_name", ""),
                    "specialization": name,
                    "location": "Global",
                    "website": g.get("website", ""),
                    "source": "google_search",
                    "component": name,
                    "relevance": g.get("relevance_score", 0.5),
                })

        # 3. Enrich with geocoding
        enriched = []
        for s in suppliers:
            try:
                e = await self.enricher.enrich_supplier(s)
                enriched.append(e)
            except Exception as ex:
                logger.warning(f"Enrichment failed: {ex}")
                enriched.append(s)

        # 4. Deduplicate
        unique = self._deduplicate(enriched)

        # 5. Fallback to mock if too few results
        if len(unique) < 5:
            logger.warning("Too few real suppliers, adding mock data")
            mocks = get_mock_suppliers(product_name, count=15 - len(unique))
            unique.extend(mocks)

        logger.info(f"Discovered {len(unique)} suppliers for {product_name}")
        return unique[:15]

    def _deduplicate(self, suppliers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate suppliers by name similarity."""
        seen: set = set()
        unique = []
        for s in suppliers:
            key = s.get("company_name", "").lower().strip()[:30]
            if key and key not in seen:
                seen.add(key)
                unique.append(s)
        return unique

    @staticmethod
    def _parse_price(price_str: str) -> float:
        """Extract numeric price from string."""
        if not price_str:
            return 0.0
        cleaned = "".join(c for c in str(price_str) if c.isdigit() or c == ".")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
