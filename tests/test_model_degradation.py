import pytest
from app.security.budget_controller import BudgetController, BudgetConfig
from app.agents.llm_factory import get_degraded_llm
from app.graph.graph import guardrail_node
from langchain_core.messages import HumanMessage


def test_budget_should_degrade_threshold():
    # max_session_cost = 1.0, alert_at_percentage = 0.8 -> warning threshold is 0.8
    config = BudgetConfig(max_session_cost=1.0, max_daily_cost=10.0, alert_at_percentage=0.8)
    bc = BudgetController(config)
    session_id = "test-degrade-session"

    # Initially cost is 0.0 -> should not degrade
    assert bc.should_degrade(session_id) is False

    # Record usage of 0.79 -> still below threshold
    bc.record_usage(session_id, "gemini-2.5-pro", 500, 20)  # ~0.00083
    assert bc.should_degrade(session_id) is False

    # Record usage to cross 0.8 threshold
    # gemini-2.5-pro output is $0.010 per 1k -> 85k output = $0.85 -> total > $0.80
    bc.record_usage(session_id, "gemini-2.5-pro", 1000, 85000)
    assert bc.should_degrade(session_id) is True


def test_get_degraded_llm_factory():
    llm = get_degraded_llm(temperature=0.1)
    assert llm is not None


def test_guardrail_node_activates_degraded_mode():
    config = BudgetConfig(max_session_cost=1.0, max_daily_cost=10.0, max_tokens_per_session=200000, alert_at_percentage=0.8)
    from app.security.budget_controller import configure_budget_controller
    configure_budget_controller(config)
    bc = configure_budget_controller(config)

    session_id = "test-guardrail-degrade"
    # Push session cost above 0.80
    bc.record_usage(session_id, "gemini-2.5-pro", 1000, 85000)

    state = {
        "messages": [HumanMessage(content="Recommend a laptop")],
        "session_id": session_id,
        "customer_id": None,
        "routing_decision": "",
        "budget_ok": True,
        "budget_message": None,
        "guardrail_fail": False,
        "guardrail_message": None,
        "degraded_mode": None,
    }

    result = guardrail_node(state)
    assert result["budget_ok"] is True
    assert result["guardrail_fail"] is False
    assert result["degraded_mode"] is True
