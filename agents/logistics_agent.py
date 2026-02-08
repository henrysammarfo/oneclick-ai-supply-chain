"""
Logistics Agent - Route optimization and shipping cost estimation.
Uses great-circle distance for realistic shipping calculations.
"""

import math
from typing import Dict, List, Optional, Any
from loguru import logger

from .base_agent import BaseAgent, AgentIdentity, Message


# Major port/hub coordinates for estimation
HUBS = {
    "Shanghai": (31.23, 121.47), "Rotterdam": (51.92, 4.48),
    "Singapore": (1.35, 103.82), "Los Angeles": (33.94, -118.41),
    "Dubai": (25.28, 55.30), "Hamburg": (53.55, 9.99),
    "Tokyo": (35.65, 139.84), "New York": (40.68, -74.04),
    "Mumbai": (19.08, 72.88), "Sydney": (-33.87, 151.21),
    "Maranello": (44.53, 10.86), "Detroit": (42.33, -83.05),
    "Stuttgart": (48.78, 9.18), "Seoul": (37.57, 126.98),
}

SHIPPING_COST_PER_KM = {
    "air": 4.50,
    "sea": 0.12,
    "ground": 0.85,
}

CUSTOMS_DAYS = {
    ("CN", "US"): 7, ("CN", "EU"): 5, ("JP", "US"): 4,
    ("DE", "US"): 3, ("IT", "US"): 3, ("KR", "US"): 4,
    ("IN", "US"): 6, ("default",): 5,
}


class LogisticsAgent(BaseAgent):
    """Route optimization and shipping estimation agent."""

    def __init__(self):
        identity = AgentIdentity(
            role="logistics",
            capabilities=["route_optimization", "cost_estimation", "customs"],
            endpoint="/agents/logistics",
        )
        super().__init__(identity)
        self.routes: List[Dict[str, Any]] = []

    async def process_message(self, message: Message) -> Optional[Message]:
        if message.message_type == "optimize_request":
            result = await self.execute_task(message.payload)
            return await self.send_message(
                message.from_agent, "logistics_result", result
            )
        return None

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        suppliers = task.get("suppliers", [])
        destination = task.get("destination", {"lat": 40.68, "lng": -74.04})
        plan = self.optimize_shipping(suppliers, destination)
        return plan

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in km."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat1))
             * math.cos(math.radians(lat2))
             * math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def calculate_route(
        self, origin: Dict[str, float], destination: Dict[str, float]
    ) -> Dict[str, Any]:
        """Estimate shipping between two points."""
        dist = self._haversine(
            origin.get("lat", 0), origin.get("lng", 0),
            destination.get("lat", 0), destination.get("lng", 0),
        )
        # Choose mode based on distance
        if dist > 5000:
            mode = "sea"
            days = max(5, int(dist / 800))
        elif dist > 1000:
            mode = "air"
            days = max(2, int(dist / 3000) + 1)
        else:
            mode = "ground"
            days = max(1, int(dist / 500) + 1)

        cost = dist * SHIPPING_COST_PER_KM[mode]
        return {
            "distance_km": round(dist, 1),
            "mode": mode,
            "estimated_days": days,
            "estimated_cost_usd": round(cost, 2),
        }

    def optimize_shipping(
        self, suppliers: List[Dict[str, Any]], destination: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build optimized shipping plan for all suppliers."""
        routes = []
        total_cost = 0.0
        max_days = 0

        for supplier in suppliers:
            origin = {"lat": supplier.get("lat", 0), "lng": supplier.get("lng", 0)}
            route = self.calculate_route(origin, destination)
            customs = self.estimate_customs_delay(
                supplier.get("country", ""), destination.get("country", "US")
            )
            route["customs_days"] = customs
            route["total_days"] = route["estimated_days"] + customs
            route["supplier"] = supplier.get("company_name", "Unknown")
            route["origin"] = supplier.get("location", "Unknown")
            routes.append(route)
            total_cost += route["estimated_cost_usd"]
            max_days = max(max_days, route["total_days"])

        self.routes = routes
        plan = {
            "routes": routes,
            "total_shipping_cost": round(total_cost, 2),
            "longest_route_days": max_days,
            "route_count": len(routes),
        }
        logger.info(
            f"Shipping plan: {len(routes)} routes, "
            f"${total_cost:,.2f}, {max_days} days max"
        )
        return plan

    @staticmethod
    def estimate_customs_delay(origin_country: str, dest_country: str) -> int:
        key = (origin_country[:2].upper(), dest_country[:2].upper())
        return CUSTOMS_DAYS.get(key, CUSTOMS_DAYS[("default",)])
