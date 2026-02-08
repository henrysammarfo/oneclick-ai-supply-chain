from pathlib import Path
from dotenv import load_dotenv
import asyncio
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from discovery.product_search import ProductSearchService
from discovery.supplier_finder import SupplierFinder
from discovery.company_enricher import CompanyEnricher


def main():
    load_dotenv(".env")

    async def run():
        ps = ProductSearchService()
        products = await ps.search_products("brake caliper")
        print(f"RapidAPI products: {len(products)}")

        if (os.getenv("ENABLE_GOOGLE_SEARCH", "").strip().lower() in {"1", "true", "yes", "on"}):
            sf = SupplierFinder()
            suppliers = await sf.find_suppliers("brake caliper", "brakes")
            print(f"Google suppliers: {len(suppliers)}")
        else:
            print("Google suppliers: SKIPPED (ENABLE_GOOGLE_SEARCH=0)")

        ce = CompanyEnricher()
        geo = await ce.geocode_company("Brembo", "Bergamo, Italy")
        print(f"Geocode ok: {bool(geo)}")

        rate = await ce.get_exchange_rate("EUR", "USD")
        print(f"FX EUR->USD: {rate}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
