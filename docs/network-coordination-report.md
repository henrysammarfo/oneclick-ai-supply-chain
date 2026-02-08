# Network Coordination Report

## Summary
This report documents the discovery, verification, negotiation, and coordination cascade for the OneClick AI supply chain agent network. The system models a NANDA-inspired registry of interoperable agents and executes a procurement workflow end-to-end.

## Scenario
- **Product:** Ferrari F8 Tributo (demo scenario)
- **Goal:** Decompose product, discover suppliers, negotiate bids, validate logistics and compliance, and produce a supply plan.

## Discovery Paths
1. **Product Decomposition**
   - Buyer agent uses GPT-based decomposition to generate 20–50 components with quantities, priorities, and lead times.

2. **Supplier Discovery**
   - **RapidAPI Product Search** (Amazon + Alibaba): extracts real product listings and supplier hints.

3. **Enrichment**
   - **Geocoding API:** resolves supplier locations to lat/lng.
   - **Exchange Rate API:** normalizes pricing into USD when currency is non-USD.

4. **Deduplication + Ranking**
   - Suppliers are deduplicated by name similarity.
   - Relevance scoring boosts ISO/wholesale/manufacturer indicators.

> **Offline Mode:** If API keys are missing or `OFFLINE_MODE=1`, the system uses high-fidelity mock data for decomposition, discovery, and enrichment to keep the demo deterministic.

## Trust and Policy Enforcement
- **Compliance Agent** validates suppliers using:
  - Country-based restrictions
  - Reliability thresholds
  - Known restricted jurisdictions (e.g., KP)
- **Logistics Agent** estimates routing and customs delays to validate feasibility.

## Message Exchange Timeline (Typical)
1. `decompose_request` → buyer agent decomposes product.
2. `request_bid` → suppliers receive bid requests (message bus).
3. `supplier_bid` → suppliers respond with sealed bids.
4. `counter_offer` → negotiation engine triggers re-bids.
5. `award_contract` → winning suppliers receive awards.
6. `logistics_result` → routing and cost validation.
7. `compliance_result` → policy validation.

## Final Execution Plan (Example)
- **Components:** ~20–50
- **Suppliers:** ~10–15 real candidates + fallback mock data if required
- **Negotiation:** 3 rounds sealed-bid auction
- **Supply Plan Output:**
  - Total cost, max delivery lead time, and supplier assignments
  - Execution readiness gated by compliance + logistics checks

## Artifacts Produced
- `supply_graph.json` with nodes/edges for components, suppliers, and routes
- Message feed (`logs/agent_feed.jsonl`) for live UI playback

## Conclusion
The network demonstrates discovery, verification, negotiation, and execution cascade across interoperable agents—matching the NANDA-inspired “Internet of Agents” goals. The architecture shows how modular coordination primitives can unlock programmable trade workflows.
