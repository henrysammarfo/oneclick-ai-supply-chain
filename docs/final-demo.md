# Final Demo Script (CLI + Expected Output)

This is the exact demo flow for judges. Use **offline** for deterministic runs; use **online** to show live APIs.

## 1) Offline (No API Keys)

**Windows (PowerShell):**
```powershell
$env:OFFLINE_MODE=1
.\.venv\Scripts\python.exe run_demo.py --scenario ferrari
```

**Expected output (samples):**
- `Product: Ferrari F8 Tributo`
- `Decomposed into 20-50 components`
- `Found 15 suppliers`
- `Negotiated 10 contracts`
- `Supply plan created`
- `Pipeline complete! Graph saved to supply_graph.json`

**Start server + UI:**
```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --port 8000
```
Open `http://localhost:8000/static/index.html`
If frontend is on Vercel, open: `https://your-vercel-site.vercel.app/?api=https://your-backend.onrender.com`

**Expected UI behavior:**
- Graph renders with components + suppliers
- Live feed updates with `request_bid` / `supplier_bid` messages
- Stats update on left panel
- Search bar triggers a new run and live updates

## 2) Online (Real APIs)

**Set keys in `.env`:**
- `RAPIDAPI_KEY`
- `GEOCODING_API_KEY`
- `EXCHANGE_RATE_API_KEY`
- `RAPIDAPI_PROVIDER=chat-gpt26`
- `RAPIDAPI_OPENAI_HOST=chat-gpt26.p.rapidapi.com`
- `RAPIDAPI_LLM_MODEL=GPT-5-mini`
- `ENABLE_GOOGLE_SEARCH=0`

**Run:**
```powershell
$env:OFFLINE_MODE=0
.\.venv\Scripts\python.exe run_demo.py --scenario ferrari
.\.venv\Scripts\python.exe -m uvicorn main:app --port 8000
```

**Expected output (samples):**
- `Product search 'brake caliper': X results`
- `Discovered N suppliers`
- Geocoded locations for suppliers

## 3) API Sanity Checks

```powershell
Invoke-RestMethod http://localhost:8000/api/health
Invoke-RestMethod http://localhost:8000/api/graph
Invoke-RestMethod http://localhost:8000/api/status
```

**Expected:**
- `/api/health` returns `{"status":"ok"}`
- `/api/graph` returns `{"nodes":[...], "links":[...]}`
- `/api/status` returns `{"running": false, ...}`

## 4) Screenshot Capture (Optional)

```powershell
pip install playwright
python -m playwright install chromium
python scripts/capture_screenshots.py
```

## 5) RapidAPI LLM Test (Tiny Prompt)

```powershell
python scripts/rapidapi_llm_test.py
```

If the default RapidAPI provider fails, run:
```powershell
python scripts/rapidapi_llm_sweep.py
```
Then set `RAPIDAPI_PROVIDER` + `RAPIDAPI_OPENAI_HOST` to the working provider.


