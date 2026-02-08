import json
import pytest
from agents.base_agent import Message
from protocols.messaging import MessageBus


@pytest.mark.asyncio
async def test_message_bus_writes_feed(tmp_path):
    feed_path = tmp_path / "feed.jsonl"
    bus = MessageBus(feed_path=str(feed_path))
    msg = Message(from_agent="a1", to_agent="a2", message_type="ping", payload={})
    await bus.send_message(msg)

    lines = feed_path.read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["type"] == "ping"
