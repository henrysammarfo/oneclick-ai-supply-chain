# OneClick AI — Judge One‑Pager

**Track:** One Click AI – Supply Chain Agents (NANDA‑Native “Internet of Agents”)  
**Team:** OneClick AI  
**Goal:** Show how agent discovery + coordination + execution become programmable in a supply chain.

## What This Is
OneClick AI is a NANDA‑inspired network of interoperable agents that takes a single intent (“build a Ferrari”) and orchestrates a full supply plan. It demonstrates:
- **Agent‑native discovery** (registry + semantic search)
- **Interoperable coordination** (message bus + negotiation)
- **Supply graph intelligence** (live D3 visualization)

## Core MVP Features (Challenge Mapping)
1. **Agent‑Native Supply Network**  
   Registry publishes AgentFacts (identity, role, capabilities, endpoint, policy). Agents are discoverable by capability/region.

2. **Interoperable Coordination & Execution Cascade**  
   Buyer → discovery → supplier agents → negotiation → logistics → compliance, all via structured message events and a live feed.

3. **Supply Graph Intelligence & Visualization**  
   Live D3 graph renders components, suppliers, and routes; updates stream over `/ws/feed`.

## How Judges Can Test (5‑Minute Flow)
**Offline (no keys needed):**
1. `OFFLINE_MODE=1`
2. `python run_demo.py --scenario ferrari`
3. `uvicorn main:app --port 8000`
4. Open `http://localhost:8000/static/index.html`

**Online (real APIs):**
1. Set keys in `.env` (`RAPIDAPI_KEY`, `GEOCODING_API_KEY`, `EXCHANGE_RATE_API_KEY`)
2. `OFFLINE_MODE=0`
3. Run same demo + server steps

**Deployed (Vercel + Render):**
1. Backend on Render/Fly/Railway with WebSockets enabled
2. Frontend on Vercel
3. Visit UI with backend pointer: `?api=https://your-backend.onrender.com`

## What You’ll See
- Live graph updates with suppliers and routes
- Message feed with negotiation events
- Supply plan summary in CLI output
- Memphis‑style UI with bold geometric patterns and high‑contrast panels
- Search bar to trigger new product runs (e.g., “fridge”, “airplane”)

## Key Artifacts
- `supply_graph.json` — graph snapshots
- `logs/agent_feed.jsonl` — message stream
- `docs/network-coordination-report.md` — required report

## Why This Wins
This project demonstrates the **three required hero features** with a cohesive, demo‑ready flow. The agent network is **discoverable**, **interoperable**, and **observable**, and the system produces the coordination artifacts the challenge requires. Offline mode guarantees a deterministic demo; online mode proves real‑time supplier discovery and enrichment.
