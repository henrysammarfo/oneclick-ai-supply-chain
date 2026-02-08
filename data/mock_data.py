"""Fallback mock data for demo reliability when APIs are rate-limited."""

import random
from typing import List, Dict, Any


MOCK_SUPPLIERS = [
    {"company_name": "Precision Motors GmbH", "location": "Stuttgart, Germany", "country": "DE", "lat": 48.78, "lng": 9.18, "specialization": "engine", "quality_rating": 0.92, "reliability": 0.95, "price_modifier": 1.15},
    {"company_name": "Brembo S.p.A.", "location": "Bergamo, Italy", "country": "IT", "lat": 45.69, "lng": 9.67, "specialization": "brakes", "quality_rating": 0.95, "reliability": 0.93, "price_modifier": 1.2},
    {"company_name": "Pirelli Tyre S.p.A.", "location": "Milan, Italy", "country": "IT", "lat": 45.46, "lng": 9.19, "specialization": "wheels", "quality_rating": 0.90, "reliability": 0.92, "price_modifier": 1.1},
    {"company_name": "Bosch Automotive", "location": "Stuttgart, Germany", "country": "DE", "lat": 48.77, "lng": 9.17, "specialization": "electronics", "quality_rating": 0.94, "reliability": 0.96, "price_modifier": 1.05},
    {"company_name": "Magneti Marelli", "location": "Bologna, Italy", "country": "IT", "lat": 44.49, "lng": 11.34, "specialization": "electronics", "quality_rating": 0.88, "reliability": 0.90, "price_modifier": 0.95},
    {"company_name": "Recaro Automotive", "location": "Stuttgart, Germany", "country": "DE", "lat": 48.78, "lng": 9.18, "specialization": "interior", "quality_rating": 0.91, "reliability": 0.89, "price_modifier": 1.1},
    {"company_name": "ZF Friedrichshafen", "location": "Friedrichshafen, Germany", "country": "DE", "lat": 47.65, "lng": 9.48, "specialization": "drivetrain", "quality_rating": 0.93, "reliability": 0.94, "price_modifier": 1.08},
    {"company_name": "Continental AG", "location": "Hanover, Germany", "country": "DE", "lat": 52.37, "lng": 9.74, "specialization": "safety", "quality_rating": 0.91, "reliability": 0.93, "price_modifier": 1.0},
    {"company_name": "Denso Corporation", "location": "Kariya, Japan", "country": "JP", "lat": 34.99, "lng": 137.0, "specialization": "electronics", "quality_rating": 0.93, "reliability": 0.95, "price_modifier": 1.12},
    {"company_name": "Aisin Seiki", "location": "Kariya, Japan", "country": "JP", "lat": 34.98, "lng": 137.0, "specialization": "drivetrain", "quality_rating": 0.90, "reliability": 0.92, "price_modifier": 1.05},
    {"company_name": "BorgWarner Inc.", "location": "Detroit, USA", "country": "US", "lat": 42.33, "lng": -83.05, "specialization": "engine", "quality_rating": 0.89, "reliability": 0.91, "price_modifier": 1.0},
    {"company_name": "Dallara Automobili", "location": "Parma, Italy", "country": "IT", "lat": 44.80, "lng": 10.33, "specialization": "chassis", "quality_rating": 0.94, "reliability": 0.90, "price_modifier": 1.25},
    {"company_name": "Corning Glass", "location": "Corning, USA", "country": "US", "lat": 42.14, "lng": -77.05, "specialization": "body", "quality_rating": 0.88, "reliability": 0.94, "price_modifier": 0.95},
    {"company_name": "Shanghai Automotive", "location": "Shanghai, China", "country": "CN", "lat": 31.23, "lng": 121.47, "specialization": "body", "quality_rating": 0.78, "reliability": 0.80, "price_modifier": 0.65},
    {"company_name": "Hyundai Mobis", "location": "Seoul, South Korea", "country": "KR", "lat": 37.57, "lng": 126.98, "specialization": "safety", "quality_rating": 0.87, "reliability": 0.90, "price_modifier": 0.85},
    # Marine suppliers
    {"company_name": "Volvo Penta", "location": "Gothenburg, Sweden", "country": "SE", "lat": 57.71, "lng": 11.97, "specialization": "propulsion", "quality_rating": 0.93, "reliability": 0.95, "price_modifier": 1.15},
    {"company_name": "Raymarine", "location": "Portsmouth, UK", "country": "GB", "lat": 50.80, "lng": -1.09, "specialization": "navigation", "quality_rating": 0.90, "reliability": 0.92, "price_modifier": 1.1},
    {"company_name": "Ferretti Group", "location": "Forlì, Italy", "country": "IT", "lat": 44.22, "lng": 12.04, "specialization": "hull", "quality_rating": 0.95, "reliability": 0.90, "price_modifier": 1.3},
    {"company_name": "Kongsberg Maritime", "location": "Kongsberg, Norway", "country": "NO", "lat": 59.67, "lng": 9.65, "specialization": "navigation", "quality_rating": 0.94, "reliability": 0.96, "price_modifier": 1.2},
    # Hospitality suppliers
    {"company_name": "Serta Simmons", "location": "Atlanta, USA", "country": "US", "lat": 33.75, "lng": -84.39, "specialization": "furniture", "quality_rating": 0.88, "reliability": 0.92, "price_modifier": 0.90},
    {"company_name": "Samsung Display", "location": "Asan, South Korea", "country": "KR", "lat": 36.79, "lng": 127.0, "specialization": "electronics", "quality_rating": 0.92, "reliability": 0.94, "price_modifier": 0.85},
    {"company_name": "Welspun India", "location": "Mumbai, India", "country": "IN", "lat": 19.08, "lng": 72.88, "specialization": "linens", "quality_rating": 0.82, "reliability": 0.85, "price_modifier": 0.60},
    {"company_name": "Rational AG", "location": "Landsberg, Germany", "country": "DE", "lat": 48.05, "lng": 10.87, "specialization": "kitchen", "quality_rating": 0.95, "reliability": 0.93, "price_modifier": 1.25},
    {"company_name": "Kohler Co.", "location": "Kohler, USA", "country": "US", "lat": 43.74, "lng": -87.78, "specialization": "bathroom", "quality_rating": 0.90, "reliability": 0.94, "price_modifier": 1.05},
    {"company_name": "Turkish Textiles Co.", "location": "Istanbul, Turkey", "country": "TR", "lat": 41.01, "lng": 28.98, "specialization": "linens", "quality_rating": 0.80, "reliability": 0.82, "price_modifier": 0.55},
]

MOCK_COMPONENTS: Dict[str, List[Dict[str, Any]]] = {
    "ferrari": [
        {"name": "3.9L V8 Twin-Turbo Engine", "category": "engine", "quantity": 1, "specifications": "Ferrari F154 CB, 710hp, 7-speed DCT compatible", "estimated_cost_usd": 85000, "priority": "critical", "lead_time_days": 45},
        {"name": "Carbon Fiber Monocoque Chassis", "category": "chassis", "quantity": 1, "specifications": "Full carbon fiber tub, FIA safety cell", "estimated_cost_usd": 65000, "priority": "critical", "lead_time_days": 60},
        {"name": "Brembo Carbon-Ceramic Brakes", "category": "brakes", "quantity": 4, "specifications": "CCM3 398mm front, 360mm rear", "estimated_cost_usd": 8500, "priority": "critical", "lead_time_days": 21},
        {"name": "Pirelli P Zero Corsa Tires", "category": "wheels", "quantity": 4, "specifications": "245/35 ZR20 front, 305/30 ZR20 rear", "estimated_cost_usd": 450, "priority": "critical", "lead_time_days": 7},
        {"name": "Bosch Motorsport ECU", "category": "electronics", "quantity": 1, "specifications": "MS6.3 with Ferrari calibration", "estimated_cost_usd": 12000, "priority": "critical", "lead_time_days": 30},
        {"name": "7-Speed Dual-Clutch Transmission", "category": "drivetrain", "quantity": 1, "specifications": "Getrag F1 DCT, paddle shift", "estimated_cost_usd": 35000, "priority": "critical", "lead_time_days": 40},
        {"name": "Magneti Marelli Display", "category": "electronics", "quantity": 1, "specifications": "16-inch curved TFT instrument cluster", "estimated_cost_usd": 5500, "priority": "important", "lead_time_days": 21},
        {"name": "Recaro Carbon Bucket Seats", "category": "interior", "quantity": 2, "specifications": "Full carbon shell, Alcantara trim", "estimated_cost_usd": 9500, "priority": "important", "lead_time_days": 28},
        {"name": "Alcantara Interior Package", "category": "interior", "quantity": 1, "specifications": "Dashboard, door panels, headliner", "estimated_cost_usd": 8000, "priority": "important", "lead_time_days": 21},
        {"name": "LED Matrix Headlights", "category": "body", "quantity": 2, "specifications": "Adaptive matrix LED with DRL signature", "estimated_cost_usd": 4200, "priority": "important", "lead_time_days": 14},
        {"name": "Inconel Exhaust System", "category": "engine", "quantity": 1, "specifications": "Inconel 625 headers + titanium muffler", "estimated_cost_usd": 12000, "priority": "important", "lead_time_days": 35},
        {"name": "Electronic Stability Control", "category": "safety", "quantity": 1, "specifications": "Side Slip Control SSC 6.1", "estimated_cost_usd": 6500, "priority": "critical", "lead_time_days": 25},
        {"name": "Bilstein Racing Dampers", "category": "chassis", "quantity": 4, "specifications": "Magnetorheological adaptive dampers", "estimated_cost_usd": 3200, "priority": "important", "lead_time_days": 18},
        {"name": "Carbon Fiber Body Panels", "category": "body", "quantity": 1, "specifications": "Front bumper, rear diffuser, side skirts", "estimated_cost_usd": 25000, "priority": "critical", "lead_time_days": 35},
        {"name": "Racing Steering Wheel", "category": "interior", "quantity": 1, "specifications": "Carbon fiber, F1-style manettino, LED shift lights", "estimated_cost_usd": 4500, "priority": "important", "lead_time_days": 14},
        {"name": "Airbag System", "category": "safety", "quantity": 1, "specifications": "6-airbag system with knee airbags", "estimated_cost_usd": 2800, "priority": "critical", "lead_time_days": 14},
        {"name": "Multi-Link Rear Suspension", "category": "chassis", "quantity": 1, "specifications": "Aluminum multi-link with active control", "estimated_cost_usd": 8500, "priority": "critical", "lead_time_days": 25},
        {"name": "Windshield & Glass Package", "category": "body", "quantity": 1, "specifications": "Laminated windshield, rear glass, side windows", "estimated_cost_usd": 3500, "priority": "important", "lead_time_days": 10},
        {"name": "Wiring Harness", "category": "electronics", "quantity": 1, "specifications": "Complete vehicle wiring with CAN bus", "estimated_cost_usd": 4500, "priority": "critical", "lead_time_days": 21},
        {"name": "Paint & Clearcoat", "category": "body", "quantity": 1, "specifications": "Rosso Corsa triple-layer metallic", "estimated_cost_usd": 15000, "priority": "important", "lead_time_days": 14},
        {"name": "Forged Aluminum Wheels", "category": "wheels", "quantity": 4, "specifications": "20-inch forged aluminum, diamond cut", "estimated_cost_usd": 3800, "priority": "important", "lead_time_days": 21},
        {"name": "Fuel System", "category": "engine", "quantity": 1, "specifications": "Direct injection, 80L fuel tank", "estimated_cost_usd": 5500, "priority": "critical", "lead_time_days": 18},
        {"name": "Air Conditioning System", "category": "interior", "quantity": 1, "specifications": "Dual-zone automatic climate control", "estimated_cost_usd": 2200, "priority": "optional", "lead_time_days": 10},
        {"name": "Infotainment System", "category": "electronics", "quantity": 1, "specifications": "Apple CarPlay, JBL premium audio", "estimated_cost_usd": 3500, "priority": "optional", "lead_time_days": 14},
        {"name": "Cooling System", "category": "engine", "quantity": 1, "specifications": "Triple radiator setup with intercoolers", "estimated_cost_usd": 4200, "priority": "critical", "lead_time_days": 14},
    ],
}


def get_mock_suppliers(product_name: str = "", count: int = 15) -> List[Dict[str, Any]]:
    """Return mock suppliers appropriate for the product."""
    lower = product_name.lower()
    filtered = list(MOCK_SUPPLIERS)

    # Prioritize relevant suppliers
    if any(kw in lower for kw in ["ferrari", "car", "vehicle", "auto"]):
        filtered = [s for s in MOCK_SUPPLIERS if s["specialization"] in {"engine", "brakes", "chassis", "electronics", "drivetrain", "interior", "body", "safety", "wheels"}]
    elif any(kw in lower for kw in ["yacht", "boat", "ship"]):
        filtered = [s for s in MOCK_SUPPLIERS if s["specialization"] in {"propulsion", "navigation", "hull", "electrical", "deck"}]
    elif any(kw in lower for kw in ["hotel", "resort"]):
        filtered = [s for s in MOCK_SUPPLIERS if s["specialization"] in {"furniture", "electronics", "linens", "kitchen", "bathroom"}]

    if not filtered:
        filtered = list(MOCK_SUPPLIERS)

    random.shuffle(filtered)
    return filtered[:count]


def get_mock_components(product_name: str) -> List[Dict[str, Any]]:
    """Return pre-built component list for known products."""
    lower = product_name.lower()
    if "ferrari" in lower:
        return MOCK_COMPONENTS["ferrari"]
    # Fallback: use taxonomy
    from data.product_taxonomy import ProductTaxonomy
    category = ProductTaxonomy.get_category(product_name)
    return ProductTaxonomy.get_components_template(category)
