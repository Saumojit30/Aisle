"""Unit tests for the e-commerce agent graph, tools, and security layer."""

from app.security.budget_controller import BudgetController, BudgetConfig
from app.security.content_filter import ContentFilter
from app.tools import order_tools, product_tools, customer_tools
from app.graph.state import AgentState
from app.graph.graph import guardrail_node, supervisor_node, respond_node
from langchain_core.messages import HumanMessage, AIMessage


# ---------------------------------------------------------------------------
# Budget controller
# ---------------------------------------------------------------------------

def test_budget_allows_valid_request():
    bc = BudgetController(BudgetConfig(max_daily_cost=10, max_session_cost=2))
    ok, msg = bc.can_proceed("test-sess")
    assert ok is True
    assert msg is None


def test_budget_blocks_when_exhausted():
    bc = BudgetController(BudgetConfig(max_daily_cost=0.001, max_session_cost=0.001))
    bc.record_usage("test-sess", "llama-3.1-8b-instant", 1000, 200)
    ok, msg = bc.can_proceed("test-sess")
    assert ok is False
    assert msg is not None


def test_budget_tracks_daily_reset():
    bc = BudgetController(BudgetConfig(max_daily_cost=10))
    bc.record_usage("test-sess", "llama-3.1-8b-instant", 5000, 1000)
    # Cost should be non-zero
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
    assert "[EMAIL_REDACTED]" in redacted
    assert any(f["type"] == "email" for f in findings)


def test_redact_phone():
    cf = ContentFilter()
    redacted, findings = cf.redact_pii("Call 555-123-4567")
    assert "[PHONE_REDACTED]" in redacted


def test_safe_text_passes():
    cf = ContentFilter()
    safe, msg = cf.check_safety("I love your products!")
    assert safe is True


def test_sensitive_topic_flagged():
    cf = ContentFilter()
    safe, msg = cf.check_safety("I want to hack your system")
    assert safe is False


# ---------------------------------------------------------------------------
# Order tools
# ---------------------------------------------------------------------------

def test_get_order_status_found():
    result = order_tools.get_order_status.invoke({"order_id": "ORD-001"})
    assert "ORD-001" in result
    assert "shipped" in result


def test_get_order_status_not_found():
    result = order_tools.get_order_status.invoke({"order_id": "INVALID"})
    assert "not found" in result


def test_cancel_order_success():
    result = order_tools.cancel_order.invoke({"order_id": "ORD-002", "reason": "Changed mind"})
    assert "cancelled" in result


def test_cancel_order_already_shipped():
    # ORD-001 is shipped, cannot cancel
    result = order_tools.cancel_order.invoke({"order_id": "ORD-001", "reason": "Test"})
    assert "Cannot cancel" in result


# ---------------------------------------------------------------------------
# Product tools
# ---------------------------------------------------------------------------

def test_search_catalogue():
    result = product_tools.search_catalogue.invoke({"query": "headphones"})
    assert "headphones" in result.lower() or "Headphones" in result


def test_search_catalogue_empty():
    result = product_tools.search_catalogue.invoke({"query": "zzzznotexist"})
    assert "No products found" in result


def test_get_product_details():
    result = product_tools.get_product_details.invoke({"product_id": "PROD-001"})
    assert "Wireless Headphones" in result


# ---------------------------------------------------------------------------
# Customer tools
# ---------------------------------------------------------------------------

def test_get_customer_profile():
    result = customer_tools.get_customer_profile.invoke({"customer_id": "CUST-001"})
    assert "Alice" in result


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
