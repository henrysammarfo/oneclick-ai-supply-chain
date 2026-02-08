"""Ferrari F8 Tributo demo scenario - automotive sourcing."""

from typing import Dict, List, Any
from data.mock_data import MOCK_COMPONENTS, get_mock_suppliers


class FerrariF8Scenario:
    """Demo: Source all components for a Ferrari F8 Tributo."""

    NAME = "Ferrari F8 Tributo"
    CATEGORY = "automotive"
    EXPECTED_COST = 847000
    EXPECTED_DAYS = 45
    EXPECTED_SUPPLIERS = 18

    @staticmethod
    def get_components() -> List[Dict[str, Any]]:
        return MOCK_COMPONENTS.get("ferrari", [])

    @staticmethod
    def get_suppliers() -> List[Dict[str, Any]]:
        return get_mock_suppliers("ferrari", count=18)

    @classmethod
    async def run(cls) -> Dict[str, Any]:
        return {
            "product": cls.NAME,
            "category": cls.CATEGORY,
            "components": cls.get_components(),
            "suppliers": cls.get_suppliers(),
            "expected_cost": cls.EXPECTED_COST,
            "expected_days": cls.EXPECTED_DAYS,
        }

    @classmethod
    def get_description(cls) -> str:
        return (
            f"{cls.NAME} - Automotive Sourcing Demo\n"
            f"Components: {len(cls.get_components())} parts\n"
            f"Expected: ~${cls.EXPECTED_COST:,}, {cls.EXPECTED_DAYS} days, "
            f"{cls.EXPECTED_SUPPLIERS} suppliers"
        )
