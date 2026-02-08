"""WebSocket-compatible message bus for agent-to-agent communication."""

from typing import Dict, List, Callable, Any, Optional
from loguru import logger
import os
import json
from pathlib import Path

from agents.base_agent import Message


class MessageBus:
    """Central message router with conversation logging."""

    def __init__(self, feed_path: Optional[str] = None):
        self._handlers: Dict[str, Callable] = {}
        self._history: List[Dict[str, Any]] = []
        self._subscribers: List[Callable] = []
        self._feed_path = feed_path or os.getenv("MESSAGE_FEED_PATH", "")
        if self._feed_path:
            Path(self._feed_path).parent.mkdir(parents=True, exist_ok=True)
        logger.info("MessageBus initialized")

    def register_handler(self, agent_id: str, handler: Callable):
        """Register a message handler for an agent."""
        self._handlers[agent_id] = handler

    async def send_message(self, message: Message) -> Optional[Message]:
        """Route message to target agent handler."""
        self._log_message(message)
        handler = self._handlers.get(message.to_agent)
        if handler:
            response = await handler(message)
            if response:
                self._log_message(response)
            return response
        logger.warning(f"No handler for agent {message.to_agent[:8]}")
        return None

    async def broadcast(self, from_agent: str, message_type: str, payload: Dict[str, Any]):
        """Send message to all registered handlers."""
        for agent_id, handler in self._handlers.items():
            if agent_id != from_agent:
                msg = Message(
                    from_agent=from_agent,
                    to_agent=agent_id,
                    message_type=message_type,
                    payload=payload,
                )
                self._log_message(msg)
                await handler(msg)

    def subscribe(self, callback: Callable):
        """Subscribe to all messages for real-time monitoring."""
        self._subscribers.append(callback)

    def clear_feed(self):
        """Truncate feed file for a clean demo run."""
        if not self._feed_path:
            return
        Path(self._feed_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self._feed_path).write_text("", encoding="utf-8")

    def _write_feed(self, entry: Dict[str, Any]):
        if not self._feed_path:
            return
        with open(self._feed_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def _log_message(self, message: Message):
        entry = {
            "from": message.from_agent[:8],
            "to": message.to_agent[:8],
            "type": message.message_type,
            "timestamp": str(message.timestamp),
            "payload_keys": list(message.payload.keys()),
        }
        self._history.append(entry)
        self._write_feed(entry)
        for sub in self._subscribers:
            try:
                sub(entry)
            except Exception:
                pass

    def get_conversation_log(self) -> List[Dict[str, Any]]:
        return list(self._history)

    @property
    def message_count(self) -> int:
        return len(self._history)
