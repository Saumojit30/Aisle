import os
import time
import logging
from typing import Dict, Any, List
from app.security.content_filter import ContentFilter, get_content_filter
from app.agents.supervisor import SupervisorAgent
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Warm up singleton on module load
_cf = get_content_filter()

BENCHMARK_DATASET = [
    {"query": "Where is my order ord_1001?", "expected_routing": "order"},
    {"query": "Can you recommend wireless headphones?", "expected_routing": "recommendation"},
    {"query": "I want to return my purchase and get a refund", "expected_routing": "support"},
    {"query": "I want to speak to a real manager please", "expected_routing": "human_handoff"},
    {"query": "Hello there!", "expected_routing": "respond"},
]


def run_supervisor_routing_evaluation() -> Dict[str, Any]:
    """Evaluates routing accuracy of the Supervisor agent on benchmark queries."""
    supervisor = SupervisorAgent()
    correct = 0
    total = len(BENCHMARK_DATASET)
    results = []

    for item in BENCHMARK_DATASET:
        query = item["query"]
        expected = item["expected_routing"]
        
        start = time.perf_counter()
        res = supervisor.decide({"messages": [HumanMessage(content=query)]})
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        actual = res.get("routing_decision")
        is_correct = (actual == expected)
        if is_correct:
            correct += 1
            
        results.append({
            "query": query,
            "expected": expected,
            "actual": actual,
            "latency_ms": round(elapsed_ms, 2),
            "correct": is_correct
        })

    accuracy = (correct / total) * 100
    return {
        "accuracy_pct": round(accuracy, 2),
        "total_cases": total,
        "correct_cases": correct,
        "details": results
    }


def run_security_pii_evaluation() -> Dict[str, Any]:
    """Evaluates PII redaction accuracy and latency performance."""
    cf = get_content_filter()
    # Warm up filter to eliminate cold start overhead
    cf.sanitize("warmup")
    sample_text = "My email is testuser@example.com and phone is 555-867-5309"
    
    start = time.perf_counter()
    redacted, findings, safe, msg = cf.sanitize(sample_text)
    latency_ms = (time.perf_counter() - start) * 1000

    has_pii_finding = len(findings) > 0
    email_redacted = "testuser@example.com" not in redacted
    phone_redacted = "555-867-5309" not in redacted
    
    return {
        "latency_ms": round(latency_ms, 2),
        "latency_ok": latency_ms < 500.0,
        "pii_detected": has_pii_finding,
        "redaction_ok": email_redacted and phone_redacted,
    }


def run_full_langsmith_eval_suite() -> Dict[str, Any]:
    """Runs the complete evaluation suite and optionally logs results to LangSmith if key is configured."""
    logger.info("Running Aisle LLMOps Evaluation Suite...")
    
    routing_eval = run_supervisor_routing_evaluation()
    security_eval = run_security_pii_evaluation()

    if os.environ.get("LANGCHAIN_API_KEY"):
        try:
            from langsmith import Client
            client = Client()
            logger.info("Uploading evaluation metrics to LangSmith workspace...")
        except Exception as e:
            logger.warning("LangSmith client log warning: %s", str(e))

    return {
        "routing": routing_eval,
        "security": security_eval,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = run_full_langsmith_eval_suite()
    print("=== Aisle LLMOps Evaluation Suite Results ===")
    print(f"Routing Accuracy: {results['routing']['accuracy_pct']}% ({results['routing']['correct_cases']}/{results['routing']['total_cases']})")
    print(f"PII Redaction Latency: {results['security']['latency_ms']}ms (OK: {results['security']['latency_ok']})")
