"""Order cascade coordination protocol."""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from loguru import logger


class CoordinationProtocol:
    """Coordinates order execution across all winning suppliers."""

    def __init__(self):
        self.supply_plan: Dict[str, Any] = {}
        self.execution_status: Dict[str, str] = {}

    def create_supply_plan(
        self, product: str, winners: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build execution plan from auction winners."""
        orders = []
        total_cost = 0.0
        max_delivery = 0

        for component, winner in winners.items():
            cost = winner.get("total_price", 0)
            days = winner.get("delivery_days", 14)
            total_cost += cost
            max_delivery = max(max_delivery, days)
            orders.append({
                "component": component,
                "supplier": winner.get("supplier_name", "Unknown"),
                "supplier_id": winner.get("supplier_id", ""),
                "cost": cost,
                "delivery_days": days,
                "status": "pending",
                "order_date": str(datetime.utcnow()),
                "expected_delivery": str(datetime.utcnow() + timedelta(days=days)),
            })
            self.execution_status[component] = "pending"

        self.supply_plan = {
            "product": product,
            "orders": orders,
            "total_cost": round(total_cost, 2),
            "total_components": len(orders),
            "estimated_completion_days": max_delivery,
            "created_at": str(datetime.utcnow()),
        }
        logger.info(f"Supply plan: {len(orders)} orders, ${total_cost:,.2f}, {max_delivery} days")
        return self.supply_plan

    async def validate_plan(
        self, plan: Dict[str, Any], logistics_agent=None, compliance_agent=None
    ) -> Dict[str, Any]:
        """Run logistics and compliance checks."""
        validation: Dict[str, Any] = {"logistics": None, "compliance": None, "valid": True, "issues": []}

        if logistics_agent:
            suppliers = [
                {"company_name": o["supplier"], "lat": 0, "lng": 0, "country": ""}
                for o in plan.get("orders", [])
            ]
            validation["logistics"] = await logistics_agent.execute_task({
                "suppliers": suppliers,
                "destination": {"lat": 40.68, "lng": -74.04, "country": "US"},
            })

        if compliance_agent:
            suppliers = [
                {"company_name": o["supplier"], "country": "", "reliability": 0.8}
                for o in plan.get("orders", [])
            ]
            result = await compliance_agent.execute_task({"suppliers": suppliers, "product_type": "general"})
            validation["compliance"] = result
            if result.get("cleared_count", 0) < len(suppliers):
                validation["issues"].append("Some suppliers failed compliance")

        validation["valid"] = len(validation["issues"]) == 0
        return validation

    async def execute_cascade(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate order placement."""
        results = []
        for order in plan.get("orders", []):
            self.execution_status[order["component"]] = "ordered"
            results.append({"component": order["component"], "supplier": order["supplier"], "status": "ordered", "cost": order["cost"]})
            logger.info(f"Order placed: {order['component']} -> {order['supplier']}")
        return {"orders_placed": len(results), "results": results, "total_cost": plan.get("total_cost", 0)}

    def get_execution_status(self) -> Dict[str, str]:
        return dict(self.execution_status)
