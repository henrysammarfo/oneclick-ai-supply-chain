"""
Base agent class for NANDA-native supply chain agents.
All agents inherit from this for registry compatibility and unified messaging.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio
from loguru import logger


class AgentIdentity(BaseModel):
    """NANDA-style agent identity card."""
    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    role: str  # buyer, supplier, logistics, compliance
    capabilities: List[str] = Field(default_factory=list)
    endpoint: str = ""
    policy_attributes: Dict[str, Any] = Field(default_factory=dict)
    jurisdiction: str = "global"
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"
    performance_score: float = 1.0


class Message(BaseModel):
    """Agent-to-agent message envelope."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: str = ""


class BaseAgent(ABC):
    """
    Abstract base for all supply chain agents.
    Provides registry integration, messaging, state management, and logging.
    """

    def __init__(self, identity: AgentIdentity):
        self.identity = identity
        self.state: Dict[str, Any] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[Message] = []
        logger.info(f"Agent created: {identity.role} [{identity.agent_id[:8]}]")

    @property
    def agent_id(self) -> str:
        return self.identity.agent_id

    @property
    def role(self) -> str:
        return self.identity.role

    @abstractmethod
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming message and optionally return response."""
        pass

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific task and return results."""
        pass

    async def register_with_registry(self, registry) -> bool:
        """Register this agent in the NANDA registry."""
        try:
            await registry.register_agent(self.identity.model_dump())
            logger.info(f"Registered {self.role} [{self.agent_id[:8]}] in registry")
            return True
        except Exception as e:
            logger.error(f"Registration failed for {self.agent_id[:8]}: {e}")
            return False

    async def send_message(
        self, to_agent: str, message_type: str, payload: Dict[str, Any],
        bus=None
    ) -> Message:
        """Create and optionally send a message via the message bus."""
        msg = Message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
        )
        self.message_history.append(msg)
        if bus:
            await bus.send_message(msg)
        return msg

    async def receive_messages(self) -> List[Message]:
        """Drain the message queue."""
        messages = []
        while not self.message_queue.empty():
            messages.append(await self.message_queue.get())
        return messages

    def log_action(self, action: str, details: Dict[str, Any] | None = None):
        """Structured logging for agent actions."""
        logger.info(
            f"[{self.role}:{self.agent_id[:8]}] {action}",
            **{"details": details or {}},
        )

    def get_state_summary(self) -> Dict[str, Any]:
        """Return a summary of this agent's current state."""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.identity.status,
            "capabilities": self.identity.capabilities,
            "messages_sent": len(self.message_history),
            "state_keys": list(self.state.keys()),
        }
