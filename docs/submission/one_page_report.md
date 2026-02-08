# OneClick AI — 1‑Page Report

## 1) Problem & Challenge  
Global supply chains depend on manual coordination across organizations, systems, and jurisdictions. Discovery, negotiation, and logistics are still email‑and‑spreadsheet workflows, making sourcing slow and opaque. The challenge is to make coordination programmable across independent actors.

## 2) Target Audience  
Procurement teams, manufacturers, logistics operators, and enterprise buyers who need fast, verifiable sourcing across multiple suppliers and tiers.

## 3) Solution & Core Features  
OneClick AI is a NANDA‑inspired network of agents that turns a single intent into a supply plan.  
Core features:
- Agent registry with identity + capability facts  
- Discovery of real supplier candidates (RapidAPI product search)  
- Negotiation cascade with a message bus  
- Logistics + compliance validation  
- Live D3 graph of components, suppliers, and routes

## 4) Unique Selling Proposition (USP)  
Unlike centralized procurement software, OneClick AI demonstrates **agent‑native interoperability**: independent services discover each other dynamically, negotiate in real time, and publish a shared execution plan.

## 5) Implementation & Technology  
Python 3.11, FastAPI, NetworkX, D3.js, RapidAPI product search, WebSocket feed, and a NANDA‑style registry. The system emits artifacts (`supply_graph.json`, `agent_feed.jsonl`) for audit and replay.

## 6) Results & Impact  
The demo produces a full supply plan in minutes: components, suppliers, prices, delivery estimates, and compliance checks. The live UI makes coordination observable, reducing integration friction and enabling faster, more resilient sourcing.

**Optional Reflection:** With 24 more hours we would add reputation scoring and disruption recovery.
