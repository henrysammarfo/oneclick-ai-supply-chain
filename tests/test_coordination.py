"""Tests for negotiation and coordination."""

import pytest
from agents.supplier_factory import SupplierFactory
from protocols.negotiation import NegotiationEngine
from protocols.coordination import CoordinationProtocol
from protocols.messaging import MessageBus
from agents.base_agent import Message


def _make_suppliers(n=5):
    return SupplierFactory.create_fleet([
        {"company_name": f"Supplier_{i}", "quality_rating": 0.7 + i * 0.05, "reliability": 0.8}
        for i in range(n)
    ])


@pytest.mark.asyncio
async def test_auction():
    engine = NegotiationEngine()
    suppliers = _make_suppliers(3)
    winner = await engine.run_auction("test_part", suppliers, {"estimated_cost_usd": 5000, "quantity": 1, "lead_time_days": 14}, rounds=2)
    assert "supplier_name" in winner
    assert "total_score" in winner


@pytest.mark.asyncio
async def test_multi_round():
    engine = NegotiationEngine()
    suppliers = _make_suppliers(5)
    winner = await engine.run_auction("engine", suppliers, {"estimated_cost_usd": 10000, "quantity": 2, "lead_time_days": 21}, rounds=3)
    assert winner.get("total_price", 0) > 0
    assert "engine" in engine.get_auction_results()


def test_supply_plan():
    coord = CoordinationProtocol()
    winners = {
        "engine": {"supplier_name": "MotorCo", "supplier_id": "s1", "total_price": 50000, "delivery_days": 30},
        "brakes": {"supplier_name": "BrakeCo", "supplier_id": "s2", "total_price": 8000, "delivery_days": 14},
    }
    plan = coord.create_supply_plan("Test Car", winners)
    assert plan["total_cost"] == 58000
    assert plan["estimated_completion_days"] == 30


@pytest.mark.asyncio
async def test_execute_cascade():
    coord = CoordinationProtocol()
    plan = coord.create_supply_plan("Widget", {
        "part": {"supplier_name": "A", "supplier_id": "s1", "total_price": 1000, "delivery_days": 7},
    })
    result = await coord.execute_cascade(plan)
    assert result["orders_placed"] == 1


@pytest.mark.asyncio
async def test_message_bus():
    bus = MessageBus()
    received = []
    async def handler(msg):
        received.append(msg)
        return None
    bus.register_handler("target", handler)
    await bus.send_message(Message(from_agent="src", to_agent="target", message_type="test", payload={"x": 1}))
    assert len(received) == 1
    assert bus.message_count == 1
