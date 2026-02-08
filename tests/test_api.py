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
