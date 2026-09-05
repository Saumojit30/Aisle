import pytest
from tests.eval_suite import run_full_langsmith_eval_suite, run_supervisor_routing_evaluation, run_security_pii_evaluation


def test_eval_suite_routing_accuracy():
    res = run_supervisor_routing_evaluation()
    assert res["total_cases"] == 5
    assert res["accuracy_pct"] == 100.0
    assert res["correct_cases"] == 5


def test_eval_suite_security_pii():
    res = run_security_pii_evaluation()
    assert res["pii_detected"] is True
    assert res["redaction_ok"] is True
    assert res["latency_ok"] is True


def test_full_eval_suite_runner():
    res = run_full_langsmith_eval_suite()
    assert "routing" in res
    assert "security" in res
    assert res["routing"]["accuracy_pct"] >= 80.0
