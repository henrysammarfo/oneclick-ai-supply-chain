"""
Dynamic Supplier Agent Factory.
Creates one agent per discovered supplier with unique negotiation strategies.
"""

import random
from typing import Dict, List, Optional, Any
from loguru import logger

from .base_agent import BaseAgent, AgentIdentity, Message


STRATEGIES = ["aggressive", "moderate", "conservative"]


class SupplierAgent(BaseAgent):
    """A supplier agent with bidding and negotiation capabilities."""

    def __init__(self, supplier_data: Dict[str, Any]):
        identity = AgentIdentity(
            role="supplier",
            capabilities=["bid", "negotiate", "fulfill"],
            endpoint=f"/agents/supplier/{supplier_data.get('company_name', 'unknown')}",
            jurisdiction=supplier_data.get("country", "global"),
            policy_attributes={"verified": supplier_data.get("verified", False)},
        )
        super().__init__(identity)
        self.company_name = supplier_data.get("company_name", "Unknown Supplier")
        self.specialization = supplier_data.get("specialization", "general")
        self.location = supplier_data.get("location", "Unknown")
        self.country = supplier_data.get("country", "Unknown")
        self.lat = supplier_data.get("lat", 0.0)
        self.lng = supplier_data.get("lng", 0.0)
        self.base_price_modifier = supplier_data.get("price_modifier", 1.0)
        self.quality_rating = supplier_data.get("quality_rating", 0.7)
        self.reliability = supplier_data.get("reliability", 0.8)
        self.strategy = supplier_data.get("strategy", random.choice(STRATEGIES))
        self.min_margin = {"aggressive": 0.05, "moderate": 0.12, "conservative": 0.20}

    async def process_message(self, message: Message) -> Optional[Message]:
        handlers = {
            "request_bid": self._handle_bid_request,
            "counter_offer": self._handle_counter,
            "award_contract": self._handle_award,
        }
        handler = handlers.get(message.message_type)
        if handler:
            return await handler(message)
        return None

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        component = task.get("component", "")
        requirements = task.get("requirements", {})
        bid = self.generate_bid(component, requirements)
        return {"bid": bid, "supplier": self.company_name}

    def generate_bid(
        self, component: str, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a competitive bid for a component."""
        base_cost = requirements.get("estimated_cost_usd", 1000)
        quantity = requirements.get("quantity", 1)

        # Apply strategy-based pricing
        margin = self.min_margin[self.strategy]
        noise = random.uniform(-0.08, 0.08)
        unit_price = base_cost * self.base_price_modifier * (1 + margin + noise)
        total_price = unit_price * quantity

        # Delivery estimate
        base_lead = requirements.get("lead_time_days", 14)
        delivery_days = max(3, int(base_lead * random.uniform(0.7, 1.3)))

        bid = {
            "supplier_id": self.agent_id,
            "supplier_name": self.company_name,
            "component": component,
            "unit_price": round(unit_price, 2),
            "total_price": round(total_price, 2),
            "quantity": quantity,
            "delivery_days": delivery_days,
            "quality_score": round(self.quality_rating + random.uniform(-0.05, 0.05), 2),
            "reliability": round(self.reliability, 2),
            "location": self.location,
            "country": self.country,
            "strategy": self.strategy,
            "warranty_months": random.choice([6, 12, 18, 24]),
        }
        self.log_action("bid_generated", {"component": component, "price": bid["total_price"]})
        return bid

    def negotiate(
        self, current_bid: Dict[str, Any], counter_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Respond to a counter-offer based on strategy."""
        target_price = counter_offer.get("target_price", current_bid["total_price"])
        floor = current_bid["total_price"] * (1 - self.min_margin[self.strategy])

        if target_price >= floor:
            new_price = target_price * random.uniform(1.0, 1.03)
        elif self.strategy == "aggressive":
            new_price = floor
        else:
            # Meet halfway
            new_price = (current_bid["total_price"] + target_price) / 2

        return {
            **current_bid,
            "total_price": round(max(new_price, floor), 2),
            "unit_price": round(max(new_price, floor) / current_bid["quantity"], 2),
            "round": counter_offer.get("round", 2),
            "negotiated": True,
        }

    async def _handle_bid_request(self, message: Message) -> Message:
        bid = self.generate_bid(
            message.payload.get("component", ""),
            message.payload.get("requirements", {}),
        )
        return await self.send_message(
            message.from_agent, "supplier_bid",
            {"component": message.payload["component"], "bid": bid},
        )

    async def _handle_counter(self, message: Message) -> Message:
        new_bid = self.negotiate(
            message.payload.get("current_bid", {}),
            message.payload.get("counter", {}),
        )
        return await self.send_message(
            message.from_agent, "supplier_bid",
            {"component": message.payload.get("component", ""), "bid": new_bid},
        )

    async def _handle_award(self, message: Message) -> Message:
        self.log_action("contract_awarded", message.payload)
        return await self.send_message(
            message.from_agent, "award_accepted",
            {"supplier": self.company_name, "accepted": True},
        )


class SupplierFactory:
    """Creates supplier agents dynamically from discovery results."""

    @staticmethod
    def create_supplier_agent(supplier_data: Dict[str, Any]) -> "SupplierAgent":
        agent = SupplierAgent(supplier_data)
        logger.info(f"Created supplier agent: {agent.company_name} ({agent.location})")
        return agent

    @staticmethod
    def create_fleet(suppliers_data: List[Dict[str, Any]]) -> List["SupplierAgent"]:
        fleet = [SupplierFactory.create_supplier_agent(s) for s in suppliers_data]
        logger.info(f"Created fleet of {len(fleet)} supplier agents")
        return fleet
