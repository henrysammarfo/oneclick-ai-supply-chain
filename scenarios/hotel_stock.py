"""200-Room Hotel demo scenario - hospitality sourcing."""

from typing import Dict, List, Any
from data.mock_data import get_mock_suppliers


HOTEL_COMPONENTS = [
    {"name": "King Size Beds", "category": "furniture", "quantity": 200, "specifications": "Serta Perfect Sleeper, pillow-top", "estimated_cost_usd": 1200, "priority": "critical", "lead_time_days": 30},
    {"name": "55-inch Smart TVs", "category": "electronics", "quantity": 200, "specifications": "Samsung HG55 Hospitality series", "estimated_cost_usd": 650, "priority": "important", "lead_time_days": 21},
    {"name": "Premium Sheet Sets", "category": "linens", "quantity": 600, "specifications": "400TC Egyptian cotton, white", "estimated_cost_usd": 85, "priority": "critical", "lead_time_days": 14},
    {"name": "Bath Towel Sets", "category": "linens", "quantity": 1200, "specifications": "700gsm Turkish cotton, 6-piece", "estimated_cost_usd": 45, "priority": "critical", "lead_time_days": 14},
    {"name": "Nightstands", "category": "furniture", "quantity": 400, "specifications": "Solid wood, USB charging, soft-close", "estimated_cost_usd": 280, "priority": "important", "lead_time_days": 45},
    {"name": "Work Desks", "category": "furniture", "quantity": 200, "specifications": "Executive desk with cable management", "estimated_cost_usd": 450, "priority": "important", "lead_time_days": 45},
    {"name": "Desk Chairs", "category": "furniture", "quantity": 200, "specifications": "Ergonomic, swivel, upholstered", "estimated_cost_usd": 320, "priority": "important", "lead_time_days": 30},
    {"name": "Wardrobes", "category": "furniture", "quantity": 200, "specifications": "Built-in with safe, ironing board", "estimated_cost_usd": 850, "priority": "important", "lead_time_days": 45},
    {"name": "Bathroom Vanities", "category": "bathroom", "quantity": 200, "specifications": "Marble top, undermount sink", "estimated_cost_usd": 680, "priority": "critical", "lead_time_days": 30},
    {"name": "Rain Showers", "category": "bathroom", "quantity": 200, "specifications": "Grohe thermostatic, 12-inch head", "estimated_cost_usd": 420, "priority": "important", "lead_time_days": 21},
    {"name": "Toilets", "category": "bathroom", "quantity": 200, "specifications": "TOTO Drake, elongated, soft-close", "estimated_cost_usd": 380, "priority": "critical", "lead_time_days": 21},
    {"name": "Mini Fridges", "category": "electronics", "quantity": 200, "specifications": "Dometic 40L, silent operation", "estimated_cost_usd": 350, "priority": "important", "lead_time_days": 21},
    {"name": "Room Key Card System", "category": "electronics", "quantity": 1, "specifications": "ASSA ABLOY Vingcard, 200-door", "estimated_cost_usd": 85000, "priority": "critical", "lead_time_days": 45},
    {"name": "POS System", "category": "electronics", "quantity": 5, "specifications": "Oracle Micros for F&B outlets", "estimated_cost_usd": 12000, "priority": "critical", "lead_time_days": 30},
    {"name": "Commercial Kitchen Equipment", "category": "kitchen", "quantity": 1, "specifications": "Rational combi oven, fryers, grills, prep tables", "estimated_cost_usd": 180000, "priority": "critical", "lead_time_days": 60},
    {"name": "Walk-in Refrigeration", "category": "kitchen", "quantity": 2, "specifications": "True Manufacturing, 10x12ft", "estimated_cost_usd": 25000, "priority": "critical", "lead_time_days": 30},
    {"name": "Duvets & Pillows", "category": "linens", "quantity": 600, "specifications": "Hypoallergenic, hotel-grade fill", "estimated_cost_usd": 95, "priority": "critical", "lead_time_days": 14},
    {"name": "Bathrobes", "category": "linens", "quantity": 400, "specifications": "Terry cloth, embroidered logo", "estimated_cost_usd": 35, "priority": "optional", "lead_time_days": 21},
    {"name": "Lobby Furniture", "category": "furniture", "quantity": 1, "specifications": "Custom reception desk, lounge seating", "estimated_cost_usd": 65000, "priority": "important", "lead_time_days": 60},
    {"name": "HVAC System", "category": "systems", "quantity": 1, "specifications": "VRF system, 200 fan coil units", "estimated_cost_usd": 450000, "priority": "critical", "lead_time_days": 60},
    {"name": "Laundry Equipment", "category": "systems", "quantity": 1, "specifications": "Commercial washers/dryers, 4 units each", "estimated_cost_usd": 85000, "priority": "important", "lead_time_days": 30},
    {"name": "Lighting Package", "category": "electrical", "quantity": 1, "specifications": "LED throughout, chandeliers, emergency", "estimated_cost_usd": 120000, "priority": "important", "lead_time_days": 30},
]


class HotelStockScenario:
    """Demo: Source all supplies for a 200-room hotel."""

    NAME = "200-Room Luxury Hotel"
    CATEGORY = "hospitality"
    EXPECTED_COST = 3200000
    EXPECTED_DAYS = 60
    EXPECTED_SUPPLIERS = 22

    @staticmethod
    def get_components() -> List[Dict[str, Any]]:
        return HOTEL_COMPONENTS

    @staticmethod
    def get_suppliers() -> List[Dict[str, Any]]:
        return get_mock_suppliers("hotel", count=22)

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
            f"{cls.NAME} - Hospitality Sourcing Demo\n"
            f"Components: {len(HOTEL_COMPONENTS)} items\n"
            f"Expected: ~${cls.EXPECTED_COST:,}, {cls.EXPECTED_DAYS} days, "
            f"{cls.EXPECTED_SUPPLIERS} suppliers"
        )
