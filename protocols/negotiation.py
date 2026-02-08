"""Multi-round sealed-bid auction engine."""

from typing import Dict, List, Any
from loguru import logger


class NegotiationEngine:
    """
    Multi-round sealed-bid auctions.
    Round 1: All suppliers bid (sealed)
    Round 2: Top 50% re-bid with market feedback
    Round 3: Best-and-final offers from top 3
    """

    def __init__(self):
        self.auctions: Dict[str, Dict[str, Any]] = {}
        self.bid_history: List[Dict[str, Any]] = []

    async def run_auction(
        self,
        component: str,
        supplier_agents: List[Any],
        requirements: Dict[str, Any],
        rounds: int = 3,
    ) -> Dict[str, Any]:
        """Run full multi-round auction for a component."""
        logger.info(f"Auction: '{component}' with {len(supplier_agents)} suppliers")
        self.auctions[component] = {"rounds": [], "winner": None}

        current_bidders = list(supplier_agents)
        all_bids: List[Dict[str, Any]] = []

        for round_num in range(1, rounds + 1):
            round_bids = []
            for agent in current_bidders:
                if round_num == 1:
                    bid = agent.generate_bid(component, requirements)
                else:
                    best_price = min(b["total_price"] for b in all_bids) if all_bids else 0
                    counter = {"target_price": best_price * 0.95, "round": round_num}
                    prev_bid = next(
                        (b for b in all_bids if b["supplier_id"] == agent.agent_id),
                        agent.generate_bid(component, requirements),
                    )
                    bid = agent.negotiate(prev_bid, counter)

                bid["round"] = round_num
                round_bids.append(bid)
                self.bid_history.append(bid)

            scored = self._score_bids(round_bids)
            self.auctions[component]["rounds"].append({
                "round": round_num,
                "bids": scored,
                "bidder_count": len(scored),
            })
            all_bids = scored

            if scored:
                logger.info(
                    f"  Round {round_num}: {len(scored)} bids, "
                    f"best ${scored[0]['total_price']:,.2f}"
                )

            # Narrow field
            if round_num == 1:
                cutoff = max(1, len(scored) // 2)
                top_ids = {b["supplier_id"] for b in scored[:cutoff]}
                current_bidders = [a for a in current_bidders if a.agent_id in top_ids]
            elif round_num == 2:
                top_ids = {b["supplier_id"] for b in scored[:3]}
                current_bidders = [a for a in current_bidders if a.agent_id in top_ids]

        if all_bids:
            winner = all_bids[0]
            self.auctions[component]["winner"] = winner
            logger.info(f"Winner: '{component}' -> {winner['supplier_name']} at ${winner['total_price']:,.2f}")
            return winner
        return {}

    def _score_bids(self, bids: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score: price 40%, quality 30%, delivery 20%, reliability 10%."""
        if not bids:
            return []
        max_price = max(b.get("total_price", 1) for b in bids) or 1
        for bid in bids:
            ps = 1.0 - (bid.get("total_price", 0) / max_price)
            qs = bid.get("quality_score", 0.5)
            ds = 1.0 - min(bid.get("delivery_days", 30) / 90, 1.0)
            rs = bid.get("reliability", 0.5)
            bid["total_score"] = round(ps * 0.40 + qs * 0.30 + ds * 0.20 + rs * 0.10, 4)
        bids.sort(key=lambda x: x["total_score"], reverse=True)
        return bids

    def get_auction_results(self) -> Dict[str, Any]:
        return dict(self.auctions)

    def get_bid_history(self) -> List[Dict[str, Any]]:
        return list(self.bid_history)
