**Tech Video (60s max) — Script**

0–10s:  
“Stack: Python + FastAPI, D3.js, NetworkX, RapidAPI product search, and a NANDA‑style agent registry.”

10–30s:  
“We implemented a coordination cascade: the buyer agent decomposes a product, discovery finds supplier candidates in real time, negotiation runs a multi‑round auction, then logistics and compliance validate the plan.”

30–45s:  
“All agents communicate over a message bus; events stream to `/ws/feed` and power the live D3 graph.”

45–55s:  
“Key challenges were provider reliability and live updates — we added offline fallback and provider selection for stability.”

55–60s:  
“Result: a programmable, interoperable supply‑chain network with a live, demo‑ready UI.”
