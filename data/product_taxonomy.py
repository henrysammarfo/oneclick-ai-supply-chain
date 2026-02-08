"""Product categories and component templates for universal decomposition."""

from typing import Dict, List, Any


TAXONOMIES: Dict[str, Dict[str, List[str]]] = {
    "automotive": {
        "engine": ["engine block", "turbocharger", "fuel injection", "exhaust system", "cooling system"],
        "chassis": ["monocoque frame", "suspension", "steering rack", "subframe"],
        "electronics": ["ECU", "wiring harness", "sensors", "infotainment", "instrument cluster"],
        "interior": ["seats", "dashboard", "steering wheel", "carpet", "headliner"],
        "body": ["body panels", "windshield", "mirrors", "lights", "paint"],
        "safety": ["airbags", "seatbelts", "ABS module", "stability control"],
        "drivetrain": ["transmission", "driveshaft", "differential", "clutch"],
        "brakes": ["brake calipers", "brake rotors", "brake pads", "brake lines"],
        "wheels": ["wheels", "tires", "lug nuts", "TPMS sensors"],
    },
    "marine": {
        "hull": ["fiberglass hull", "keel", "rudder", "deck", "transom"],
        "propulsion": ["diesel engines", "propeller shafts", "propellers", "fuel tanks"],
        "navigation": ["radar", "GPS chartplotter", "compass", "AIS transponder"],
        "interior": ["cabin furniture", "galley", "berths", "upholstery"],
        "safety": ["life rafts", "fire extinguishers", "EPIRB", "flares"],
        "electrical": ["marine batteries", "generator", "shore power", "lighting"],
        "deck": ["teak decking", "winches", "anchor system", "fenders"],
    },
    "hospitality": {
        "furniture": ["king beds", "desks", "chairs", "wardrobes", "nightstands"],
        "electronics": ["smart TVs", "room phones", "POS systems", "key card systems"],
        "linens": ["sheets", "towels", "pillows", "duvets", "bathrobes"],
        "kitchen": ["commercial ovens", "refrigerators", "dishwashers", "cookware"],
        "bathroom": ["vanities", "toilets", "showers", "fixtures", "mirrors"],
        "lighting": ["chandeliers", "bedside lamps", "corridor lights", "emergency lights"],
        "hvac": ["AC units", "ventilation", "thermostats", "air purifiers"],
    },
    "electronics": {
        "processors": ["CPU", "GPU", "NPU", "memory controller"],
        "displays": ["LCD panel", "OLED panel", "touch digitizer", "display driver"],
        "batteries": ["lithium cells", "battery management system", "charging circuit"],
        "sensors": ["accelerometer", "gyroscope", "proximity sensor", "camera module"],
        "housing": ["aluminum chassis", "glass panels", "buttons", "SIM tray"],
    },
    "aerospace": {
        "propulsion": ["turbofan engine", "compressor stages", "combustion chamber", "turbine blades", "nacelle"],
        "airframe": ["fuselage sections", "wing spars", "composite skins", "fasteners", "cargo doors"],
        "avionics": ["flight computer", "navigation system", "radar", "communications radio", "black box"],
        "control": ["flight control surfaces", "actuators", "fly-by-wire system", "control cables"],
        "landing_gear": ["landing gear struts", "brake assemblies", "wheel/tire set", "retraction system"],
        "electrical": ["power distribution unit", "generator", "battery pack", "wiring harness"],
        "hydraulics": ["hydraulic pumps", "reservoirs", "valves", "hydraulic lines"],
        "fuel": ["fuel tanks", "fuel pumps", "fuel lines", "fuel control unit"],
        "safety": ["oxygen system", "fire suppression", "emergency beacons", "life vests"],
    },
}

KEYWORDS: Dict[str, List[str]] = {
    "automotive": ["car", "vehicle", "ferrari", "lamborghini", "porsche", "bmw", "mercedes", "tesla", "truck", "suv"],
    "marine": ["yacht", "boat", "ship", "vessel", "catamaran", "sailboat"],
    "hospitality": ["hotel", "resort", "motel", "inn", "lodge", "restaurant"],
    "electronics": ["phone", "laptop", "tablet", "computer", "iphone", "samsung", "tv", "monitor"],
    "aerospace": ["aircraft", "airplane", "plane", "jet", "turbine", "aerospace", "drone", "helicopter"],
}


class ProductTaxonomy:
    """Product classification and component templates."""

    @staticmethod
    def get_category(product_name: str) -> str:
        """Auto-detect product category from name."""
        lower = product_name.lower()
        for category, keywords in KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return category
        return "general"

    @staticmethod
    def get_components_template(category: str) -> List[Dict[str, Any]]:
        """Return typical components for a category."""
        taxonomy = TAXONOMIES.get(category, {})
        components = []
        for group, items in taxonomy.items():
            for item in items:
                components.append({
                    "name": item,
                    "category": group,
                    "quantity": 1,
                    "specifications": f"Standard {category} grade {item}",
                    "estimated_cost_usd": 500,
                    "priority": "important",
                    "lead_time_days": 14,
                })
        if components:
            return components
        # Generic fallback when category is unknown
        return [
            {
                "name": "core structure",
                "category": "structure",
                "quantity": 1,
                "specifications": "Primary structural assembly",
                "estimated_cost_usd": 1500,
                "priority": "critical",
                "lead_time_days": 21,
            },
            {
                "name": "power system",
                "category": "power",
                "quantity": 1,
                "specifications": "Primary power unit",
                "estimated_cost_usd": 1200,
                "priority": "critical",
                "lead_time_days": 21,
            },
            {
                "name": "control system",
                "category": "control",
                "quantity": 1,
                "specifications": "Control logic and actuators",
                "estimated_cost_usd": 800,
                "priority": "important",
                "lead_time_days": 14,
            },
            {
                "name": "safety systems",
                "category": "safety",
                "quantity": 1,
                "specifications": "Safety and compliance systems",
                "estimated_cost_usd": 600,
                "priority": "important",
                "lead_time_days": 10,
            },
            {
                "name": "enclosure & casing",
                "category": "body",
                "quantity": 1,
                "specifications": "External housing and protection",
                "estimated_cost_usd": 700,
                "priority": "important",
                "lead_time_days": 14,
            },
            {
                "name": "electronics & sensors",
                "category": "electronics",
                "quantity": 1,
                "specifications": "Core sensors and electronics",
                "estimated_cost_usd": 500,
                "priority": "important",
                "lead_time_days": 10,
            },
        ]

    @staticmethod
    def get_suppliers_by_category(category: str) -> List[str]:
        """Return likely supplier types for a category."""
        types = {
            "automotive": ["engine manufacturer", "parts supplier", "electronics OEM", "tire manufacturer"],
            "marine": ["shipyard", "marine engine dealer", "navigation equipment supplier"],
            "hospitality": ["furniture wholesaler", "linen supplier", "commercial kitchen supplier"],
            "electronics": ["semiconductor fab", "display manufacturer", "battery supplier"],
        }
        return types.get(category, ["general supplier"])
