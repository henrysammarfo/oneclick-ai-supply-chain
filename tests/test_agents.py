"""Tests for agent modules."""

import pytest
from agents.base_agent import AgentIdentity, Message
from agents.buyer_agent import BuyerAgent
from agents.supplier_factory import SupplierFactory, SupplierAgent
from agents.logistics_agent import LogisticsAgent
from agents.compliance_agent import ComplianceAgent


def test_agent_identity_creation():
    identity = AgentIdentity(role="buyer", capabilities=["decompose"])
    assert identity.role == "buyer"
    assert len(identity.agent_id) > 0
    assert identity.status == "active"


def test_message_creation():
    msg = Message(from_agent="a1", to_agent="a2", message_type="test", payload={"key": "val"})
    assert msg.from_agent == "a1"
    assert msg.message_type == "test"


def test_buyer_agent_creation():
    buyer = BuyerAgent("Ferrari F8")
    assert buyer.role == "buyer"
    assert buyer.product_name == "Ferrari F8"


def test_buyer_evaluate_bids():
    buyer = BuyerAgent("Test")
    bids = [
        {"supplier_name": "A", "price": 1000, "quality_score": 0.9, "delivery_days": 10, "reliability": 0.9, "total_price": 1000},
        {"supplier_name": "B", "price": 800, "quality_score": 0.7, "delivery_days": 20, "reliability": 0.8, "total_price": 800},
    ]
    winner = buyer.evaluate_bids("engine", bids)
    assert "total_score" in winner


def test_supplier_generate_bid():
    data = {"company_name": "TestCo", "quality_rating": 0.9, "reliability": 0.85}
    agent = SupplierAgent(data)
    bid = agent.generate_bid("engine", {"estimated_cost_usd": 10000, "quantity": 1, "lead_time_days": 14})
    assert "total_price" in bid
    assert bid["supplier_name"] == "TestCo"


def test_supplier_negotiate():
    data = {"company_name": "TestCo", "quality_rating": 0.9, "reliability": 0.85}
    agent = SupplierAgent(data)
    bid = agent.generate_bid("engine", {"estimated_cost_usd": 10000, "quantity": 1})
    counter = {"target_price": bid["total_price"] * 0.9, "round": 2}
    new_bid = agent.negotiate(bid, counter)
    assert new_bid["negotiated"] is True


def test_supplier_fleet():
    fleet = SupplierFactory.create_fleet([
        {"company_name": f"S{i}", "quality_rating": 0.8, "reliability": 0.8} for i in range(5)
    ])
    assert len(fleet) == 5


def test_logistics_haversine():
    dist = LogisticsAgent._haversine(48.78, 9.18, 40.68, -74.04)
    assert 6000 < dist < 7000


def test_logistics_route():
    agent = LogisticsAgent()
    route = agent.calculate_route({"lat": 48.78, "lng": 9.18}, {"lat": 40.68, "lng": -74.04})
    assert route["mode"] in ("air", "sea")
    assert route["estimated_days"] > 0


def test_compliance_clean():
    agent = ComplianceAgent()
    assert agent.validate_supplier({"country": "DE"})["passed"] is True


def test_compliance_restricted():
    agent = ComplianceAgent()
    assert agent.validate_supplier({"country": "KP"})["passed"] is False


def test_compliance_risk():
    agent = ComplianceAgent()
    score = agent.assess_risk({"country": "DE", "reliability": 0.9, "verified": True, "years_in_business": 15})
    assert 0 <= score <= 100
