import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from visualization.supply_graph import SupplyGraphBuilder
from data.mock_data import get_mock_components, get_mock_suppliers

app = FastAPI(title="OneClick AI Supply Chain")

app.mount("/static", StaticFiles(directory="visualization/static"), name="static")

RUN_STATE = {"running": False, "product": None, "error": None}


class RunRequest(BaseModel):
    product: str


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


def _graph_path() -> Path:
    return Path(os.getenv("SUPPLY_GRAPH_PATH", "supply_graph.json"))


def _feed_path() -> Path:
    return Path(os.getenv("MESSAGE_FEED_PATH", "logs/agent_feed.jsonl"))


def _demo_graph():
    product = "Ferrari F8 Tributo"
    components = get_mock_components(product)[:8]
    suppliers = get_mock_suppliers(product, count=8)
    supplier_map = {}
    for comp, sup in zip(components, suppliers):
        supplier_map[comp["name"]] = {
            "supplier_name": sup.get("company_name", ""),
            "location": sup.get("location", ""),
            "country": sup.get("country", ""),
            "total_price": sup.get("total_price", 0),
            "delivery_days": sup.get("delivery_days", 0),
        }
    builder = SupplyGraphBuilder()
    builder.build_graph(product, components, supplier_map)
    return builder.export_for_d3()


@app.get("/api/graph")
def graph():
    path = _graph_path()
    if path.exists():
        return JSONResponse(content=json.loads(path.read_text(encoding="utf-8")))
    return JSONResponse(content=_demo_graph())


@app.get("/api/status")
def status():
    return RUN_STATE


@app.post("/api/run")
async def run_demo(req: RunRequest):
    if RUN_STATE["running"]:
        return JSONResponse(status_code=409, content={"status": "busy"})

    product = (req.product or "").strip()
    if not product:
        return JSONResponse(status_code=400, content={"status": "error", "message": "product required"})

    RUN_STATE["running"] = True
    RUN_STATE["product"] = product
    RUN_STATE["error"] = None

    async def _runner():
        try:
            from run_demo import run_pipeline
            await run_pipeline(product, "custom")
        except Exception as exc:
            RUN_STATE["error"] = str(exc)
        finally:
            RUN_STATE["running"] = False

    asyncio.create_task(_runner())
    return {"status": "started", "product": product}


@app.websocket("/ws/feed")
async def ws_feed(websocket: WebSocket):
    await websocket.accept()

    feed_path = _feed_path()
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.touch(exist_ok=True)

    graph_path = _graph_path()
    last_graph_mtime = graph_path.stat().st_mtime if graph_path.exists() else None
    pos = 0

    try:
        while True:
            if feed_path.exists():
                with feed_path.open("r", encoding="utf-8") as f:
                    f.seek(pos)
                    lines = f.readlines()
                    pos = f.tell()
                for line in lines:
                    line = line.strip()
                    if line:
                        await websocket.send_text(line)

            if graph_path.exists():
                mtime = graph_path.stat().st_mtime
                if last_graph_mtime is None or mtime > last_graph_mtime:
                    last_graph_mtime = mtime
                    try:
                        data = json.loads(graph_path.read_text(encoding="utf-8"))
                        await websocket.send_text(json.dumps({"type": "graph_update", "graph": data}))
                    except Exception:
                        pass

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        return
