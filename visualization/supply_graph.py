"""NetworkX-based supply chain graph builder."""

import json
from typing import Dict, List, Any
import networkx as nx
from loguru import logger


class SupplyGraphBuilder:
    """Builds and exports supply chain graphs for D3.js visualization."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(
        self,
        product: str,
        components: List[Dict[str, Any]],
        suppliers: Dict[str, Dict[str, Any]],
        routes: List[Dict[str, Any]] = None,
    ) -> nx.DiGraph:
        """Create supply chain directed graph."""
        self.graph = nx.DiGraph()

        # Product node (center)
        self.graph.add_node(product, type="product", color="#ffd700", size=40)

        # Component nodes
        for comp in components:
            name = comp.get("name", "")
            self.graph.add_node(name, type="component", color="#00d4ff",
                              size=20, category=comp.get("category", ""),
                              cost=comp.get("estimated_cost_usd", 0))
            self.graph.add_edge(product, name, type="requires")

        # Supplier nodes
        for component, supplier in suppliers.items():
            sname = supplier.get("supplier_name", supplier.get("company_name", ""))
            if sname and not self.graph.has_node(sname):
                self.graph.add_node(sname, type="supplier", color="#00ff88",
                                  size=15, location=supplier.get("location", ""),
                                  country=supplier.get("country", ""))
            if sname:
                self.graph.add_edge(sname, component, type="supplies",
                                  price=supplier.get("total_price", 0),
                                  delivery=supplier.get("delivery_days", 0))

        if routes:
            for route in routes:
                s = route.get("supplier", "")
                if self.graph.has_node(s):
                    self.graph.add_edge(s, product, type="ships_to",
                                      mode=route.get("mode", ""),
                                      days=route.get("total_days", 0),
                                      cost=route.get("estimated_cost_usd", 0))

        logger.info(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph

    def export_for_d3(self, graph: nx.DiGraph = None) -> Dict[str, Any]:
        """Convert to D3.js format: {nodes: [...], links: [...]}."""
        g = graph or self.graph
        nodes = [{"id": nid, **data} for nid, data in g.nodes(data=True)]
        links = [{"source": s, "target": t, **d} for s, t, d in g.edges(data=True)]
        return {"nodes": nodes, "links": links}

    def get_statistics(self, graph: nx.DiGraph = None) -> Dict[str, Any]:
        g = graph or self.graph
        cost = sum(d.get("price", 0) for _, _, d in g.edges(data=True) if d.get("type") == "supplies")
        return {
            "total_nodes": g.number_of_nodes(),
            "total_edges": g.number_of_edges(),
            "components": sum(1 for _, d in g.nodes(data=True) if d.get("type") == "component"),
            "suppliers": sum(1 for _, d in g.nodes(data=True) if d.get("type") == "supplier"),
            "total_cost": cost,
        }

    def export_json(self, filepath: str = "supply_graph.json"):
        data = self.export_for_d3()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Graph exported to {filepath}")
