import pytest
from protocols.messaging import MessageBus
from protocols.negotiation import NegotiationEngine
from agents.supplier_factory import SupplierAgent


@pytest.mark.asyncio
async def test_negotiation_uses_bus():
    bus = MessageBus()
    suppliers = [SupplierAgent({"company_name": "S1"}), SupplierAgent({"company_name": "S2"})]
    for s in suppliers:
        bus.register_handler(s.agent_id, s.process_message)

    engine = NegotiationEngine()
    winner = await engine.run_auction(
        "engine",
        suppliers,
        {"estimated_cost_usd": 1000, "quantity": 1, "lead_time_days": 7},
        rounds=1,
        bus=bus,
    )
    assert winner
    assert bus.message_count > 0
