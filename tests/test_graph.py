"""Unit tests for the e-commerce agent graph, tools, and security layer."""

import pytest
import asyncio
from app.security.budget_controller import BudgetController, BudgetConfig
from app.security.content_filter import ContentFilter
from app.tools import order_tools, product_tools, customer_tools
from app.graph.state import AgentState
from app.graph.graph import guardrail_node, supervisor_node, respond_node
from langchain_core.messages import HumanMessage, AIMessage
from app.db.database import init_db
from app.db.seed import seed_data


# ---------------------------------------------------------------------------
# Database Seeding Fixture for all Graph/Tool tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def setup_test_db():
    """Automatically initialize and seed the database before each test."""
    asyncio.run(init_db())
    asyncio.run(seed_data())


# ---------------------------------------------------------------------------
# Budget controller
# ---------------------------------------------------------------------------

def test_budget_allows_valid_request():
    bc = BudgetController(BudgetConfig(max_daily_cost=10, max_session_cost=2))
    ok, msg = bc.can_proceed("test-sess")
    assert ok is True
    assert msg is None


def test_budget_blocks_when_exhausted():
    # Set tiny limits (0.00001) so that recording usage of 1000/200 tokens (approx 0.000066 cost) exhausts it
    bc = BudgetController(BudgetConfig(max_daily_cost=0.00001, max_session_cost=0.00001))
    bc.record_usage("test-sess", "llama-3.1-8b-instant", 1000, 200)
    ok, msg = bc.can_proceed("test-sess")
    assert ok is False
    assert msg is not None


def test_budget_tracks_daily_reset():
    bc = BudgetController(BudgetConfig(max_daily_cost=10))
    bc.record_usage("test-sess", "llama-3.1-8b-instant", 5000, 1000)
    summary = bc.get_summary("test-sess")
    assert summary["session_tokens"] == 6000
    assert summary["session_cost"] > 0


def test_cost_estimate():
    cost = BudgetController.estimate_cost("llama-3.1-8b-instant", 1000, 500)
    expected = (1000 / 1000) * 0.00005 + (500 / 1000) * 0.00008
    assert abs(cost - expected) < 1e-8


# ---------------------------------------------------------------------------
# Content filter
# ---------------------------------------------------------------------------

def test_redact_email():
    cf = ContentFilter()
    redacted, findings = cf.redact_pii("Email me at alice@example.com")
    assert "alice@example.com" not in redacted
    assert any("email" in f["type"].lower() for f in findings)


def test_redact_phone():
    cf = ContentFilter()
    redacted, findings = cf.redact_pii("Call 555-123-4567")
    assert "555-123-4567" not in redacted
    assert any("phone" in f["type"].lower() for f in findings)


def test_safe_text_passes():
    cf = ContentFilter()
    safe, msg = cf.check_safety("I love your products!")
    assert safe is True


def test_sensitive_topic_flagged():
    cf = ContentFilter()
    safe, msg = cf.check_safety("I want to hack your system")
    assert safe is False


# ---------------------------------------------------------------------------
# Order tools (using actual seeded database IDs)
# ---------------------------------------------------------------------------

def test_get_order_status_found():
    result = order_tools.get_order_status.invoke({"order_id": "ord_1001"})
    assert "ord_1001" in result
    assert "shipped" in result


def test_get_order_status_not_found():
    result = order_tools.get_order_status.invoke({"order_id": "INVALID"})
    assert "not found" in result


def test_cancel_order_success():
    # ord_1002 is processing (not shipped yet) so it can be cancelled successfully
    result = order_tools.cancel_order.invoke({"order_id": "ord_1002", "reason": "Changed mind"})
    assert "cancelled" in result or "successfully" in result


def test_cancel_order_already_shipped():
    # ord_1001 is shipped, cannot cancel
    result = order_tools.cancel_order.invoke({"order_id": "ord_1001", "reason": "Test"})
    assert "Cannot cancel" in result or "already" in result


# ---------------------------------------------------------------------------
# Product tools (using actual seeded database IDs)
# ---------------------------------------------------------------------------

def test_search_catalogue():
    result = product_tools.search_catalogue.invoke({"query": "headphones"})
    assert "headphones" in result.lower() or "wireless" in result.lower()


def test_search_catalogue_empty():
    result = product_tools.search_catalogue.invoke({"query": "zzzznotexist"})
    assert "No products found" in result


def test_get_product_details():
    result = product_tools.get_product_details.invoke({"product_id": "prod_001"})
    assert "Wireless" in result or "Headphones" in result


# ---------------------------------------------------------------------------
# Customer tools (using actual seeded database IDs)
# ---------------------------------------------------------------------------

def test_get_customer_profile():
    result = customer_tools.get_customer_profile.invoke({"customer_id": "cust_123"})
    assert "cust_123" in result or "Electronics" in result


def test_get_customer_profile_not_found():
    result = customer_tools.get_customer_profile.invoke({"customer_id": "INVALID"})
    assert "not found" in result


# ---------------------------------------------------------------------------
# Guardrail node
# ---------------------------------------------------------------------------

def test_guardrail_node_passes():
    state: AgentState = {
        "messages": [HumanMessage(content="Hello")],
        "session_id": "ut-session",
        "customer_id": None,
        "routing_decision": "",
        "budget_ok": True,
        "budget_message": None,
        "guardrail_fail": False,
        "guardrail_message": None,
    }
    result = guardrail_node(state)
    assert result["budget_ok"] is True
    assert result["guardrail_fail"] is False
