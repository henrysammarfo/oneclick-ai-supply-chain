#!/usr/bin/env python3
"""
OneClick AI - Supply Chain Agent Network Demo Runner
Run: python run_demo.py --scenario ferrari
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from loguru import logger

load_dotenv()

console = Console()

BANNER = """
 ██████╗ █████╗   ██╗████████╗ ██████╗██╗     ██╗ ██████╗██╗  ██╗
██╔═══██╗██████╗  ██║╚══██╔══╝██╔═══██╗██║     ██║██╔════╝██║ ██╔╝
██║   ██║██╔██╗ ██║   ██║   ██║   ██║██║     ██║██║     █████╔╝
██║   ██║██║╚██╗██║   ██║   ██║   ██║██║     ██║██║     ██╔═██╗
╚██████╔╝██║ ╚████║   ██║   ╚██████╔╝███████╗██║╚██████╗██║  ██╗
 ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝ ╚═════╝╚═╝  ╚═╝
           AI Supply Chain Agent Network
"""

BANNER_ASCII = """
  ONECLICK AI SUPPLY CHAIN AGENT NETWORK
  -------------------------------------
"""


def _supports_utf8() -> bool:
    encoding = (getattr(sys.stdout, "encoding", "") or "").lower()
    return "utf" in encoding


def _progress(console: Console) -> Progress:
    if _supports_utf8():
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        )
    return Progress(TextColumn("[progress.description]{task.description}"), console=console)


async def run_pipeline(product: str, scenario_name: str = ""):
    """Run the full supply chain agent pipeline."""

    banner = BANNER if _supports_utf8() else BANNER_ASCII
    console.print(Panel(banner, style="bold cyan", title="Hack-Nation 2026"))
    console.print(f"\n[bold yellow]Product:[/] {product}\n")

    feed_path = os.getenv("MESSAGE_FEED_PATH", "logs/agent_feed.jsonl")
    graph_path = os.getenv("SUPPLY_GRAPH_PATH", "supply_graph.json")

    offline_flag = os.getenv("OFFLINE_MODE", "").strip().lower()
    has_openai = bool(os.getenv("OPENAI_API_KEY", ""))
    has_rapidapi = bool(os.getenv("RAPIDAPI_KEY", ""))
    has_google = bool(os.getenv("GOOGLE_SEARCH_API_KEY", "")) and bool(
        os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    )
    if offline_flag not in {"1", "true", "yes", "on"} and not (has_openai or has_rapidapi or has_google):
        os.environ["OFFLINE_MODE"] = "1"
        console.print("[bold yellow]Offline mode enabled (no API keys found). Using mock data.[/]")

    # 1. Initialize
    from registry.agent_registry import AgentRegistry
    from protocols.messaging import MessageBus
    from protocols.negotiation import NegotiationEngine
    from protocols.coordination import CoordinationProtocol
    from agents.buyer_agent import BuyerAgent
    from agents.supplier_factory import SupplierFactory
    from agents.logistics_agent import LogisticsAgent
    from agents.compliance_agent import ComplianceAgent
    from visualization.supply_graph import SupplyGraphBuilder

    registry = AgentRegistry(db_url="sqlite:///demo_registry.db")
    bus = MessageBus(feed_path=feed_path)
    bus.clear_feed()
    negotiation = NegotiationEngine()
    coordination = CoordinationProtocol()
    graph_builder = SupplyGraphBuilder()

    with _progress(console) as progress:

        # 2. Create buyer agent and decompose product
        task = progress.add_task("[cyan]Creating Buyer Agent...", total=None)
        buyer = BuyerAgent(product)
        await buyer.register_with_registry(registry)
        bus.register_handler(buyer.agent_id, buyer.process_message)
        progress.update(task, description="[green]Buyer Agent ready")

        task = progress.add_task("[cyan]Decomposing product into components...", total=None)
        result = await buyer.execute_task({"product": product})
        components = result["components"]
        progress.update(task, description=f"[green]Decomposed into {len(components)} components")

    graph_builder.build_graph(product, components, {})
    graph_builder.export_json(graph_path)

    # Show components table
    comp_table = Table(title=f"Components for {product}", style="cyan")
    comp_table.add_column("Component", style="white")
    comp_table.add_column("Category", style="blue")
    comp_table.add_column("Qty", justify="right")
    comp_table.add_column("Est. Cost", justify="right", style="green")
    comp_table.add_column("Priority", style="yellow")

    for comp in components[:20]:
        comp_table.add_row(
            comp.get("name", "")[:40],
            comp.get("category", ""),
            str(comp.get("quantity", 1)),
            f"${comp.get('estimated_cost_usd', 0):,.0f}",
            comp.get("priority", ""),
        )
    console.print(comp_table)

    with _progress(console) as progress:

        # 3. Discover suppliers
        task = progress.add_task("[cyan]Discovering real suppliers...", total=None)
        from discovery.discovery_service import UniversalDiscoveryService
        discovery = UniversalDiscoveryService()
        suppliers_data = await discovery.discover_suppliers(product, components)
        progress.update(task, description=f"[green]Found {len(suppliers_data)} suppliers")

        # Snapshot graph with supplier candidates
        supplier_map = {}
        for s in suppliers_data:
            comp = s.get("component") or s.get("specialization")
            if comp and comp not in supplier_map:
                supplier_map[comp] = {
                    "supplier_name": s.get("company_name", ""),
                    "location": s.get("location", ""),
                    "country": s.get("country", ""),
                    "total_price": s.get("estimated_price", 0),
                    "delivery_days": s.get("delivery_days", 0),
                }
        graph_builder.build_graph(product, components, supplier_map)
        graph_builder.export_json(graph_path)

        # 4. Create supplier agents
        task = progress.add_task("[cyan]Spawning supplier agents...", total=None)
        supplier_agents = SupplierFactory.create_fleet(suppliers_data)
        for agent in supplier_agents:
            await agent.register_with_registry(registry)
            bus.register_handler(agent.agent_id, agent.process_message)
        progress.update(task, description=f"[green]{len(supplier_agents)} supplier agents active")

        # 5. Run negotiations
        task = progress.add_task("[cyan]Running multi-round negotiations...", total=None)
        winners = {}
        for comp in components[:10]:  # Top 10 for demo speed
            name = comp.get("name", "")
            # Match suppliers to component
            relevant = supplier_agents[:5]  # Use available suppliers
            if relevant:
                winner = await negotiation.run_auction(name, relevant, comp, bus=bus)
                if winner:
                    winners[name] = winner
        progress.update(task, description=f"[green]Negotiated {len(winners)} contracts")

        # 6. Create supply plan
        task = progress.add_task("[cyan]Building supply plan...", total=None)
        plan = coordination.create_supply_plan(product, winners)
        progress.update(task, description="[green]Supply plan created")

        # 7. Logistics & Compliance
        task = progress.add_task("[cyan]Running logistics & compliance checks...", total=None)
        logistics = LogisticsAgent()
        compliance = ComplianceAgent()
        await logistics.register_with_registry(registry)
        await compliance.register_with_registry(registry)
        validation = await coordination.validate_plan(plan, logistics, compliance)
        progress.update(task, description="[green]Validation complete")

        # 8. Build graph
        task = progress.add_task("[cyan]Building supply graph...", total=None)
        routes = (validation.get("logistics") or {}).get("routes", [])
        graph = graph_builder.build_graph(product, components, winners, routes=routes)
        graph_builder.export_json(graph_path)
        stats = graph_builder.get_statistics()
        progress.update(task, description="[green]Graph exported")

    # Results
    console.print("\n")
    results_table = Table(title="SUPPLY CHAIN RESULTS", style="bold green")
    results_table.add_column("Metric", style="white")
    results_table.add_column("Value", style="cyan", justify="right")

    results_table.add_row("Product", product)
    results_table.add_row("Components", str(len(components)))
    results_table.add_row("Suppliers Found", str(len(suppliers_data)))
    results_table.add_row("Contracts Awarded", str(len(winners)))
    results_table.add_row("Total Cost", f"${plan.get('total_cost', 0):,.2f}")
    results_table.add_row("Delivery Estimate", f"{plan.get('estimated_completion_days', 0)} days")
    results_table.add_row("Messages Exchanged", str(bus.message_count))
    results_table.add_row("Graph Nodes", str(stats.get("total_nodes", 0)))
    results_table.add_row("Compliance", "PASSED" if validation.get("valid") else "ISSUES FOUND")

    console.print(results_table)

    # Winner details
    if winners:
        win_table = Table(title="WINNING BIDS", style="bold yellow")
        win_table.add_column("Component", style="white")
        win_table.add_column("Supplier", style="green")
        win_table.add_column("Price", justify="right", style="cyan")
        win_table.add_column("Delivery", justify="right")
        win_table.add_column("Score", justify="right", style="yellow")

        for comp_name, winner in winners.items():
            win_table.add_row(
                comp_name[:35],
                winner.get("supplier_name", "")[:25],
                f"${winner.get('total_price', 0):,.2f}",
                f"{winner.get('delivery_days', 0)}d",
                f"{winner.get('total_score', 0):.3f}",
            )
        console.print(win_table)

    registry_stats = await registry.get_statistics()
    console.print(f"\n[dim]Registry: {registry_stats['total_agents']} agents registered[/]")
    console.print("[bold green]Pipeline complete! Graph saved to supply_graph.json[/]\n")

    return plan


def main():
    parser = argparse.ArgumentParser(description="OneClick AI Supply Chain Demo")
    parser.add_argument("--scenario", choices=["ferrari", "yacht", "hotel", "custom"], default="ferrari")
    parser.add_argument("--product", type=str, default="")
    args = parser.parse_args()

    products = {
        "ferrari": "Ferrari F8 Tributo",
        "yacht": "60ft Luxury Yacht",
        "hotel": "200-Room Luxury Hotel",
    }

    product = args.product if args.product else products.get(args.scenario, "Ferrari F8 Tributo")
    asyncio.run(run_pipeline(product, args.scenario))


if __name__ == "__main__":
    main()
