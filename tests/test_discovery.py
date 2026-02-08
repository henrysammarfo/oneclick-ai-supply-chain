"""Tests for discovery modules."""

import pytest
from data.mock_data import get_mock_suppliers, get_mock_components, MOCK_SUPPLIERS
from data.product_taxonomy import ProductTaxonomy
from discovery.supplier_finder import SupplierFinder


def test_mock_suppliers():
    suppliers = get_mock_suppliers("ferrari", count=10)
    assert len(suppliers) <= 10
    assert all("company_name" in s for s in suppliers)


def test_mock_components_ferrari():
    components = get_mock_components("Ferrari F8")
    assert len(components) > 10


def test_taxonomy_automotive():
    assert ProductTaxonomy.get_category("Ferrari F8 Tributo") == "automotive"


def test_taxonomy_marine():
    assert ProductTaxonomy.get_category("60ft Luxury Yacht") == "marine"


def test_taxonomy_hospitality():
    assert ProductTaxonomy.get_category("200-Room Hotel") == "hospitality"


def test_taxonomy_template():
    comps = ProductTaxonomy.get_components_template("automotive")
    assert len(comps) > 0
    assert all("name" in c for c in comps)


def test_supplier_ranking():
    finder = SupplierFinder()
    suppliers = [
        {"company_name": "ISO Mfg", "description": "Certified ISO manufacturer 20 years", "website": ""},
        {"company_name": "Store", "description": "Online retail", "website": ""},
    ]
    ranked = finder.rank_suppliers(suppliers)
    assert ranked[0]["relevance_score"] >= ranked[1]["relevance_score"]


def test_mock_structure():
    for s in MOCK_SUPPLIERS:
        assert "company_name" in s
        assert "lat" in s
        assert "lng" in s
