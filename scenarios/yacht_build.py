"""60ft Luxury Yacht demo scenario - marine sourcing."""

from typing import Dict, List, Any
from data.mock_data import get_mock_suppliers


YACHT_COMPONENTS = [
    {"name": "Fiberglass Hull (60ft)", "category": "hull", "quantity": 1, "specifications": "Hand-laid fiberglass with Kevlar reinforcement", "estimated_cost_usd": 280000, "priority": "critical", "lead_time_days": 90},
    {"name": "Twin Volvo D13 Diesel Engines", "category": "propulsion", "quantity": 2, "specifications": "800hp each, IPS pod drives", "estimated_cost_usd": 165000, "priority": "critical", "lead_time_days": 60},
    {"name": "Teak Deck Planking", "category": "deck", "quantity": 1, "specifications": "Premium Burma teak, 200 sqm", "estimated_cost_usd": 85000, "priority": "important", "lead_time_days": 45},
    {"name": "Navigation Radar System", "category": "navigation", "quantity": 1, "specifications": "Raymarine Quantum 2 with 48nm range", "estimated_cost_usd": 28000, "priority": "critical", "lead_time_days": 21},
    {"name": "GPS Chartplotter", "category": "navigation", "quantity": 2, "specifications": "Garmin GPSMAP 8617, dual helm", "estimated_cost_usd": 12000, "priority": "critical", "lead_time_days": 14},
    {"name": "Marine Generator", "category": "electrical", "quantity": 2, "specifications": "Onan 17.5kW, super silent", "estimated_cost_usd": 32000, "priority": "critical", "lead_time_days": 30},
    {"name": "Watermaker", "category": "systems", "quantity": 1, "specifications": "Sea Recovery 1800 GPD", "estimated_cost_usd": 22000, "priority": "important", "lead_time_days": 21},
    {"name": "Air Conditioning System", "category": "systems", "quantity": 1, "specifications": "Marine AC 60,000 BTU", "estimated_cost_usd": 18000, "priority": "important", "lead_time_days": 21},
    {"name": "Stainless Steel Hardware", "category": "deck", "quantity": 1, "specifications": "316 SS cleats, rails, fittings", "estimated_cost_usd": 45000, "priority": "important", "lead_time_days": 30},
    {"name": "Life Raft System", "category": "safety", "quantity": 1, "specifications": "Viking 12-person, SOLAS approved", "estimated_cost_usd": 8500, "priority": "critical", "lead_time_days": 14},
    {"name": "Anchor Windlass", "category": "deck", "quantity": 1, "specifications": "Lewmar V5 with 100m chain", "estimated_cost_usd": 15000, "priority": "important", "lead_time_days": 21},
    {"name": "Marine Electronics Package", "category": "electronics", "quantity": 1, "specifications": "VHF, AIS, depth sounder, wind instruments", "estimated_cost_usd": 25000, "priority": "critical", "lead_time_days": 14},
    {"name": "Interior Cabinetry", "category": "interior", "quantity": 1, "specifications": "Custom mahogany, 4 cabins", "estimated_cost_usd": 120000, "priority": "important", "lead_time_days": 60},
    {"name": "Marine Upholstery", "category": "interior", "quantity": 1, "specifications": "Sunbrella exterior, leather interior", "estimated_cost_usd": 55000, "priority": "important", "lead_time_days": 30},
    {"name": "Propeller Shafts", "category": "propulsion", "quantity": 2, "specifications": "Aquamet 22 stainless, 2.5 inch", "estimated_cost_usd": 18000, "priority": "critical", "lead_time_days": 30},
    {"name": "Fuel Tanks", "category": "systems", "quantity": 2, "specifications": "Aluminum, 1500L each", "estimated_cost_usd": 12000, "priority": "critical", "lead_time_days": 21},
    {"name": "Paint & Antifouling", "category": "hull", "quantity": 1, "specifications": "Awlgrip topcoat + Interlux bottom paint", "estimated_cost_usd": 35000, "priority": "important", "lead_time_days": 14},
    {"name": "Fire Suppression System", "category": "safety", "quantity": 1, "specifications": "FM200 engine room + portable", "estimated_cost_usd": 8000, "priority": "critical", "lead_time_days": 14},
]


class YachtBuildScenario:
    """Demo: Source all components for a 60ft luxury yacht."""

    NAME = "60ft Luxury Yacht"
    CATEGORY = "marine"
    EXPECTED_COST = 2100000
    EXPECTED_DAYS = 90
    EXPECTED_SUPPLIERS = 15

    @staticmethod
    def get_components() -> List[Dict[str, Any]]:
        return YACHT_COMPONENTS

    @staticmethod
    def get_suppliers() -> List[Dict[str, Any]]:
        return get_mock_suppliers("yacht", count=15)

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
            f"{cls.NAME} - Marine Sourcing Demo\n"
            f"Components: {len(YACHT_COMPONENTS)} parts\n"
            f"Expected: ~${cls.EXPECTED_COST:,}, {cls.EXPECTED_DAYS} days, "
            f"{cls.EXPECTED_SUPPLIERS} suppliers"
        )
