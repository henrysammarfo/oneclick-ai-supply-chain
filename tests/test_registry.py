"""Tests for registry modules."""

import pytest
from registry.agent_registry import AgentRegistry
from registry.agent_facts import AgentFact, RegistryEntry


@pytest.fixture
def registry(tmp_path):
    db_path = str(tmp_path / "test.db")
    return AgentRegistry(db_url=f"sqlite:///{db_path}")


def test_agent_fact():
    fact = AgentFact(agent_id="test-123", role="buyer")
    assert fact.status == "active"
    assert fact.performance_score == 1.0


@pytest.mark.asyncio
async def test_register(registry):
    result = await registry.register_agent({"agent_id": "a1", "role": "buyer", "capabilities": ["decompose"]})
    assert result is True


@pytest.mark.asyncio
async def test_discover(registry):
    await registry.register_agent({"agent_id": "a2", "role": "supplier"})
    await registry.register_agent({"agent_id": "a3", "role": "supplier"})
    await registry.register_agent({"agent_id": "a4", "role": "buyer"})
    suppliers = await registry.discover_agents(role="supplier")
    assert len(suppliers) == 2


@pytest.mark.asyncio
async def test_get_agent(registry):
    await registry.register_agent({"agent_id": "a5", "role": "logistics"})
    agent = await registry.get_agent("a5")
    assert agent is not None
    assert agent["role"] == "logistics"


@pytest.mark.asyncio
async def test_stats(registry):
    await registry.register_agent({"agent_id": "b1", "role": "buyer"})
    await registry.register_agent({"agent_id": "b2", "role": "supplier"})
    stats = await registry.get_statistics()
    assert stats["total_agents"] == 2
