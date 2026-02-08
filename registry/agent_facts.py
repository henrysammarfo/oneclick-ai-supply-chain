"""Metadata schema for agent registry entries."""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentFact(BaseModel):
    """Core identity and performance data for a registered agent."""
    agent_id: str
    role: str
    capabilities: List[str] = Field(default_factory=list)
    endpoint: str = ""
    jurisdiction: str = "global"
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"
    performance_score: float = 1.0
    total_transactions: int = 0


class RegistryEntry(BaseModel):
    """Full registry entry with fact + metadata."""
    fact: AgentFact
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    last_seen: Optional[datetime] = None
