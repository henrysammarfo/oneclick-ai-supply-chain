# Prompt 2 Execution Plan (Codex-Direct) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Execute Prompt 2 directly in the repo by wiring RapidAPI LLM + discovery, enabling the live D3 UI feed, and making a demo-ready API server with tests and documentation.

**Architecture:** Keep CLI pipeline as the orchestration backbone. Persist agent events and graph snapshots to files. FastAPI serves D3 static assets, exposes `/api/graph`, and streams both agent events and graph updates over `/ws/feed`.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, D3.js, NetworkX, httpx.

## Summary
We will:
1. Switch BuyerAgent to dual LLM (RapidAPI default, OpenAI fallback).
2. Persist MessageBus events to a JSONL feed.
3. Emit negotiation events through the bus.
4. Update `run_demo.py` to write graph snapshots and feed events.
5. Add a minimal FastAPI server (`main.py`) to serve `/api/graph` + `/ws/feed`.
6. Update the D3 client to connect to the same port and update live.
7. Add the Network Coordination Report required by the challenge.
8. Update docs and environment examples.
9. Run tests and a manual demo.

## Public API / Interface Changes
1. `GET /api/health`
2. `GET /api/graph`
3. `WS /ws/feed`
   - Sends MessageBus events
   - Sends graph updates: `{"type":"graph_update","graph":{...}}`

---

## Task 0: Worktree + Plan Doc

**Files:**
- Create: `docs/plans/2026-02-08-prompt2-execution.md`

**Step 1: Create worktree**
Run: `node $HOME/.codex/superpowers/.codex/superpowers-codex use-skill superpowers:using-git-worktrees`
Expected: Isolated worktree.

**Step 2: Save plan**
Write this plan to `docs/plans/2026-02-08-prompt2-execution.md`.

**Step 3: Commit**
```bash
git add docs/plans/2026-02-08-prompt2-execution.md
git commit -m "docs: add prompt 2 execution plan"
```

---

## Task 1: Persist MessageBus Feed to JSONL

**Files:**
- Create: `tests/test_messaging.py`
- Modify: `protocols/messaging.py`

**Step 1: Write failing test**
```python
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
```

**Step 2: Run test to verify failure**
Run: `pytest tests/test_messaging.py::test_message_bus_writes_feed -v`
Expected: FAIL.

**Step 3: Minimal implementation**
Update `protocols/messaging.py` to accept `feed_path`, write JSONL, and expose `clear_feed()`.

**Step 4: Run test to verify pass**
Run: `pytest tests/test_messaging.py::test_message_bus_writes_feed -v`
Expected: PASS.

**Step 5: Commit**
```bash
git add protocols/messaging.py tests/test_messaging.py
git commit -m "feat: persist message bus feed to JSONL"
```

---

## Task 2: Negotiation Uses MessageBus

**Files:**
- Create: `tests/test_negotiation.py`
- Modify: `protocols/negotiation.py`

**Step 1: Write failing test**
```python
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
```

**Step 2: Run test to verify failure**
Run: `pytest tests/test_negotiation.py::test_negotiation_uses_bus -v`
Expected: FAIL.

**Step 3: Minimal implementation**
Add optional `bus` param to `run_auction`, and send `request_bid`, `counter_offer`, and `award_contract` via MessageBus.

**Step 4: Run test to verify pass**
Run: `pytest tests/test_negotiation.py::test_negotiation_uses_bus -v`
Expected: PASS.

**Step 5: Commit**
```bash
git add protocols/negotiation.py tests/test_negotiation.py
git commit -m "feat: emit negotiation events through message bus"
```

---

## Task 3: Dual LLM Client in BuyerAgent

**Files:**
- Create: `tests/test_buyer_agent_llm.py`
- Modify: `agents/buyer_agent.py`

**Step 1: Write failing test**
```python
from agents.buyer_agent import BuyerAgent

class DummyMsg: content = "ok"
class DummyChoice: message = DummyMsg()
class DummyResp: choices = [DummyChoice()]

def test_extract_content_handles_string_and_openai():
    buyer = BuyerAgent("Test")
    assert buyer._extract_content("hello") == "hello"
    assert buyer._extract_content(DummyResp()) == "ok"
```

**Step 2: Run test to verify failure**
Run: `pytest tests/test_buyer_agent_llm.py::test_extract_content_handles_string_and_openai -v`
Expected: FAIL.

**Step 3: Minimal implementation**
Add `_get_llm_client` and `_extract_content` to `BuyerAgent`.
Use OpenAI if `OPENAI_API_KEY` exists, else RapidAPI wrapper.

**Step 4: Run test to verify pass**
Run: `pytest tests/test_buyer_agent_llm.py::test_extract_content_handles_string_and_openai -v`
Expected: PASS.

**Step 5: Commit**
```bash
git add agents/buyer_agent.py tests/test_buyer_agent_llm.py
git commit -m "feat: dual LLM client with RapidAPI default"
```

---

## Task 4: Live Graph Snapshots + Feed in Demo Runner

**Files:**
- Modify: `run_demo.py`

**Step 1: Manual failing check**
Run: `python run_demo.py --scenario ferrari`
Expected: No feed file, no live snapshots.

**Step 2: Implementation**
- Initialize MessageBus with `MESSAGE_FEED_PATH`, call `clear_feed()`.
- Export graph after decomposition, supplier discovery, and final plan.
- Pass `bus` to `NegotiationEngine.run_auction`.

**Step 3: Manual verification**
Run: `python run_demo.py --scenario ferrari`
Expected: `logs/agent_feed.jsonl` exists and `supply_graph.json` updates.

**Step 4: Commit**
```bash
git add run_demo.py
git commit -m "feat: live graph snapshots and bus-backed demo feed"
```

---

## Task 5: Minimal FastAPI Server + WebSocket Feed

**Files:**
- Create: `main.py`
- Create: `tests/test_api.py`

**Step 1: Write failing test**
```python
from fastapi.testclient import TestClient
import json
from main import app

def test_health_and_graph(tmp_path, monkeypatch):
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps({"nodes": [], "links": []}))
    monkeypatch.setenv("SUPPLY_GRAPH_PATH", str(graph_path))

    client = TestClient(app)
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/graph").json() == {"nodes": [], "links": []}
```

**Step 2: Run test to verify failure**
Run: `pytest tests/test_api.py::test_health_and_graph -v`
Expected: FAIL.

**Step 3: Minimal implementation**
Create `main.py` serving `/static`, `/api/graph`, and `/ws/feed` with file tailing + graph mtime checks.

**Step 4: Run test to verify pass**
Run: `pytest tests/test_api.py::test_health_and_graph -v`
Expected: PASS.

**Step 5: Commit**
```bash
git add main.py tests/test_api.py
git commit -m "feat: minimal FastAPI server with live feed"
```

---

## Task 6: D3 Client Live Updates

**Files:**
- Modify: `visualization/static/graph.js`

**Step 1: Manual failing check**
Run: `uvicorn main:app --reload` and open `/static/index.html`.
Expected: graph loads but no live updates.

**Step 2: Implementation**
- Change WS URL to same port.
- Handle `graph_update` messages and re-render.
- Clear SVG before re-render to avoid duplication.

**Step 3: Manual verification**
Run demo + refresh UI.
Expected: agent feed live and graph updates at least 3 times.

**Step 4: Commit**
```bash
git add visualization/static/graph.js
git commit -m "feat: live D3 updates via same-port WS"
```

---

## Task 7: Network Coordination Report (Required)

**Files:**
- Create: `docs/network-coordination-report.md`
- Modify: `README.md`

**Step 1: Create report**
Include discovery paths, policy checks, message exchanges, and final plan summary.

**Step 2: Link in README**
Add section “Network Coordination Report”.

**Step 3: Commit**
```bash
git add docs/network-coordination-report.md README.md
git commit -m "docs: add network coordination report"
```

---

## Task 8: Config + Cleanup

**Files:**
- Modify: `.env.example`
- Modify: `.gitignore`

**Step 1: Add keys**
Add `OPENAI_API_KEY` (optional) and feed/graph paths.

**Step 2: Ignore demo files**
Add `logs/*.jsonl` and `supply_graph.json`.

**Step 3: Commit**
```bash
git add .env.example .gitignore
git commit -m "chore: update env example and ignores"
```

---

## Test Cases and Scenarios
1. `pytest tests/test_messaging.py::test_message_bus_writes_feed -v`
2. `pytest tests/test_negotiation.py::test_negotiation_uses_bus -v`
3. `pytest tests/test_buyer_agent_llm.py::test_extract_content_handles_string_and_openai -v`
4. `pytest tests/test_api.py::test_health_and_graph -v`
5. Manual demo:
   1. `uvicorn main:app --reload`
   2. `python run_demo.py --scenario ferrari`
   3. Open `http://localhost:8000/static/index.html`

---

## Assumptions and Defaults
1. RapidAPI is default LLM, OpenAI is optional fallback.
2. WebSocket uses same port as FastAPI.
3. Live graph updates are file-based (mtime polling).
4. We do not modify `.env` (to avoid touching secrets).
