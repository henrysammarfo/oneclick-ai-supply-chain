"""
NANDA-style agent registry.
Agents publish capabilities, discover partners, coordinate.
"""

from typing import List, Dict, Optional, Any
from loguru import logger

from .database import DatabaseManager


class AgentRegistry:
    """Decentralized agent registry for discovery and coordination."""

    def __init__(self, db_url: str = "sqlite:///agent_registry.db"):
        self.db = DatabaseManager(db_url)
        self.db.init_db()
        self._live_agents: Dict[str, Any] = {}
        logger.info("Agent Registry initialized")

    async def register_agent(self, agent_identity: Dict[str, Any]) -> bool:
        """Register an agent in the registry."""
        agent_id = agent_identity.get("agent_id", "")
        self.db.insert_agent(agent_identity)
        self._live_agents[agent_id] = agent_identity
        logger.info(f"Registered: {agent_identity.get('role')} [{agent_id[:8]}]")
        return True

    async def discover_agents(
        self,
        role: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        jurisdiction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic discovery of agents by criteria."""
        results = self.db.query_agents(role, capabilities, jurisdiction)
        logger.info(f"Discovery: found {len(results)} agents (role={role})")
        return results

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        if agent_id in self._live_agents:
            return self._live_agents[agent_id]
        return self.db.get_agent(agent_id)

    async def update_performance(self, agent_id: str, score: float) -> bool:
        current = self.db.get_agent(agent_id) or {}
        return self.db.update_agent(agent_id, {
            "performance_score": score,
            "total_transactions": current.get("total_transactions", 0) + 1,
        })

    async def deregister_agent(self, agent_id: str) -> bool:
        self._live_agents.pop(agent_id, None)
        return self.db.update_agent(agent_id, {"status": "inactive"})

    async def get_statistics(self) -> Dict[str, Any]:
        all_agents = self.db.get_all_agents()
        roles: Dict[str, int] = {}
        total_score = 0.0
        for a in all_agents:
            r = a.get("role", "unknown")
            roles[r] = roles.get(r, 0) + 1
            total_score += a.get("performance_score", 0)
        return {
            "total_agents": len(all_agents),
            "by_role": roles,
            "avg_performance": round(total_score / max(len(all_agents), 1), 2),
        }
