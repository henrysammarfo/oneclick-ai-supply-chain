"""
Buyer Agent - LangGraph + GPT-4 powered product decomposition.
Decomposes ANY complex product into components, evaluates supplier bids.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from loguru import logger

from .base_agent import BaseAgent, AgentIdentity, Message

load_dotenv()


class BuyerAgent(BaseAgent):
    """
    LangGraph-based buyer agent that uses GPT-4 to decompose products
    into components and evaluate supplier bids.
    """

    def __init__(self, product_name: str = ""):
        identity = AgentIdentity(
            role="buyer",
            capabilities=["decompose", "evaluate_bids", "select_suppliers"],
            endpoint="/agents/buyer",
            policy_attributes={"budget_authority": True},
        )
        super().__init__(identity)
        self.product_name = product_name
        self.components: List[Dict[str, Any]] = []
        self.bids: Dict[str, List[Dict]] = {}  # component -> list of bids
        self.winners: Dict[str, Dict] = {}  # component -> winning bid

    async def process_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages."""
        handlers = {
            "decompose_request": self._handle_decompose,
            "supplier_bid": self._handle_bid,
            "negotiation_result": self._handle_negotiation_result,
        }
        handler = handlers.get(message.message_type)
        if handler:
            return await handler(message)
        logger.warning(f"Unknown message type: {message.message_type}")
        return None

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Main task: decompose product."""
        product = task.get("product", self.product_name)
        self.product_name = product
        components = await self.decompose_product(product)
        return {
            "product": product,
            "components": components,
            "component_count": len(components),
        }

    def _get_llm_client(self):
        """Return OpenAI client if OPENAI_API_KEY is set, else RapidAPI client."""
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=openai_key)
        from utils.rapidapi_openai import get_openai_client
        return get_openai_client()

    def _offline_mode(self) -> bool:
        flag = os.getenv("OFFLINE_MODE", "").strip().lower()
        if flag in {"1", "true", "yes", "on"}:
            return True
        has_openai = bool(os.getenv("OPENAI_API_KEY", ""))
        has_rapidapi = bool(os.getenv("RAPIDAPI_KEY", ""))
        return not (has_openai or has_rapidapi)

    def _extract_content(self, response):
        """Handle both OpenAI response objects and RapidAPI string responses."""
        if isinstance(response, str):
            return response
        if hasattr(response, "choices"):
            return response.choices[0].message.content
        return str(response)

    def _parse_components(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSON array from model output with simple recovery."""
        try:
            return json.loads(content)
        except Exception:
            start = content.find("[")
            end = content.rfind("]")
            if start != -1 and end != -1 and end > start:
                return json.loads(content[start : end + 1])
        raise ValueError("Failed to parse component JSON")

    async def decompose_product(self, product_name: str) -> List[Dict[str, Any]]:
        """Use GPT-4 to decompose a product into components."""
        self.log_action("decompose_start", {"product": product_name})

        try:
            if self._offline_mode():
                logger.info("Offline mode enabled or no LLM keys found, using fallback decomposition")
                return self._fallback_decomposition(product_name)

            client = self._get_llm_client()
            model = os.getenv("OPENAI_MODEL", "gpt-4o")

            prompt = f"""You are a supply chain expert. Decompose \"{product_name}\" into its key components/parts needed for manufacturing or assembly.

For each component return a JSON array where each item has:
- \"name\": component name
- \"category\": category (engine, chassis, electronics, interior, body, safety, etc.)
- \"quantity\": number needed
- \"specifications\": brief spec description
- \"estimated_cost_usd\": estimated unit cost in USD
- \"priority\": \"critical\", \"important\", or \"optional\"
- \"lead_time_days\": estimated procurement lead time

Return 20-50 components. Be specific with real part names and realistic costs.
Return ONLY the JSON array, no other text."""

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,
            )

            content = self._extract_content(response).strip()
            # Strip markdown code blocks if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]

            self.components = self._parse_components(content)
            if not self.components:
                raise ValueError("Empty component list from LLM")
            logger.info(f"Decomposed {product_name} into {len(self.components)} components")
            return self.components

        except Exception as e:
            logger.warning(f"GPT-4 decomposition failed: {e}, using fallback")
            return self._fallback_decomposition(product_name)

    def _fallback_decomposition(self, product_name: str) -> List[Dict[str, Any]]:
        """Fallback decomposition when API is unavailable."""
        from data.mock_data import get_mock_components
        self.components = get_mock_components(product_name)
        return self.components

    def evaluate_bids(
        self, component: str, bids: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Score bids using weighted criteria.
        Price: 40%, Quality: 30%, Delivery: 20%, Reliability: 10%
        """
        if not bids:
            return {}

        scored = []
        for bid in bids:
            price_score = 1.0 - min(bid.get("price", 0) / 100000, 1.0)
            quality_score = bid.get("quality_score", 0.5)
            delivery_score = 1.0 - min(bid.get("delivery_days", 30) / 90, 1.0)
            reliability_score = bid.get("reliability", 0.5)

            total = (
                price_score * 0.40
                + quality_score * 0.30
                + delivery_score * 0.20
                + reliability_score * 0.10
            )
            scored.append({**bid, "total_score": round(total, 4)})

        scored.sort(key=lambda x: x["total_score"], reverse=True)
        winner = scored[0]
        self.winners[component] = winner
        logger.info(
            f"Winner for {component}: {winner.get('supplier_name')} "
            f"(score: {winner['total_score']})"
        )
        return winner

    async def _handle_decompose(self, message: Message) -> Message:
        product = message.payload.get("product", "")
        components = await self.decompose_product(product)
        return await self.send_message(
            message.from_agent, "decompose_response",
            {"components": components, "count": len(components)},
        )

    async def _handle_bid(self, message: Message) -> Optional[Message]:
        component = message.payload.get("component", "")
        bid = message.payload.get("bid", {})
        if component not in self.bids:
            self.bids[component] = []
        self.bids[component].append(bid)
        return None

    async def _handle_negotiation_result(self, message: Message) -> Optional[Message]:
        results = message.payload.get("results", {})
        self.winners.update(results)
        return None
