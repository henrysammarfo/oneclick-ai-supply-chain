"""
Compliance Agent - Trade policy validation and risk assessment.
Validates suppliers against sanctions, trade restrictions, and regulatory requirements.
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from .base_agent import BaseAgent, AgentIdentity, Message


RESTRICTED_COUNTRIES = {"KP", "IR", "SY", "CU", "VE", "RU", "BY"}
RESTRICTED_ENTITIES = {"huawei_restricted", "sanctioned_entity"}

HIGH_RISK_CATEGORIES = {"military", "dual_use", "nuclear", "chemical", "biotech"}
CONTROLLED_EXPORTS = {"encryption", "aerospace", "defense", "semiconductor_advanced"}


class ComplianceAgent(BaseAgent):
    """Trade compliance and risk assessment agent."""

    def __init__(self):
        identity = AgentIdentity(
            role="compliance",
            capabilities=["sanctions_check", "trade_compliance", "risk_assessment"],
            endpoint="/agents/compliance",
        )
        super().__init__(identity)
        self.validation_log: List[Dict[str, Any]] = []

    async def process_message(self, message: Message) -> Optional[Message]:
        if message.message_type == "validate_request":
            result = await self.execute_task(message.payload)
            return await self.send_message(
                message.from_agent, "compliance_result", result
            )
        return None

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        suppliers = task.get("suppliers", [])
        product_type = task.get("product_type", "general")
        destination = task.get("destination_country", "US")

        results = []
        for supplier in suppliers:
            validation = self.validate_supplier(supplier)
            trade_check = self.check_trade_compliance(
                supplier.get("country", ""), destination, product_type
            )
            risk = self.assess_risk(supplier)
            results.append({
                "supplier": supplier.get("company_name", "Unknown"),
                "validation": validation,
                "trade_compliance": trade_check,
                "risk_score": risk,
                "cleared": validation["passed"] and trade_check["compliant"],
            })

        cleared_count = sum(1 for r in results if r["cleared"])
        logger.info(f"Compliance: {cleared_count}/{len(results)} suppliers cleared")
        return {
            "results": results,
            "cleared_count": cleared_count,
            "total_checked": len(results),
        }

    def validate_supplier(self, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check supplier against sanctions and restrictions."""
        country = supplier_data.get("country", "")[:2].upper()
        issues = []

        if country in RESTRICTED_COUNTRIES:
            issues.append(f"Country {country} is on restricted list")

        entity_id = supplier_data.get("entity_id", "")
        if entity_id in RESTRICTED_ENTITIES:
            issues.append(f"Entity {entity_id} is sanctioned")

        result = {
            "passed": len(issues) == 0,
            "issues": issues,
            "country_code": country,
            "check_type": "sanctions_screening",
        }
        self.validation_log.append(result)
        return result

    def check_trade_compliance(
        self, origin: str, destination: str, product_type: str
    ) -> Dict[str, Any]:
        """Validate trade route and product type legality."""
        origin_code = origin[:2].upper() if origin else ""
        issues = []

        if origin_code in RESTRICTED_COUNTRIES:
            issues.append(f"Imports from {origin_code} restricted")

        if product_type.lower() in HIGH_RISK_CATEGORIES:
            issues.append(f"Product category '{product_type}' requires special license")

        if product_type.lower() in CONTROLLED_EXPORTS:
            issues.append(f"Export control applies to '{product_type}'")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "origin": origin_code,
            "destination": destination,
            "product_type": product_type,
        }

    def assess_risk(self, supplier_data: Dict[str, Any]) -> int:
        """Return risk score 0-100 (lower is better)."""
        score = 20  # base risk

        country = supplier_data.get("country", "")[:2].upper()
        if country in RESTRICTED_COUNTRIES:
            score += 60
        elif country in {"CN", "IN", "TR", "BR"}:
            score += 15
        elif country in {"DE", "JP", "US", "GB", "FR", "IT", "KR"}:
            score -= 10

        reliability = supplier_data.get("reliability", 0.5)
        score -= int(reliability * 20)

        if supplier_data.get("verified", False):
            score -= 10

        years = supplier_data.get("years_in_business", 0)
        if years > 10:
            score -= 10
        elif years < 2:
            score += 10

        return max(0, min(100, score))
