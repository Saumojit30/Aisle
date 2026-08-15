import re
import logging
from typing import Any, Dict
from langchain_core.messages import SystemMessage
from app.config import settings
from app.agents.llm_factory import get_llm

logger = logging.getLogger(__name__)

PROMPT = """You route customer requests to the right specialist in an e-commerce system.

Available agents:
- support         — Returns, refunds, complaints, account help, order issues.
- order           — Order status, tracking, cancellations, shipping info.
- recommendation  — Product suggestions, comparisons, finding items.
- respond         — Simple greetings, thanks, farewells.
- human_handoff   — Requests to speak to a real human, manager, or live agent.

Rules:
1. Pick the SINGLE best agent name.
2. If the user explicitly asks for a human, manager, or live agent, pick "human_handoff".
3. Respond with exactly one word — the agent name."""


class SupervisorAgent:
    def __init__(self):
        self.llm = None
        if settings.groq_api_key or settings.gemini_api_key:
            try:
                self.llm = get_llm(
                    model_name=settings.support_model,  # Uses supervisor_model or support_model as config
                    temperature=0.0,
                )
            except Exception as e:
                logger.warning("Could not initialize LLM for supervisor: %s", str(e))
        self.system = SystemMessage(content=PROMPT)

    def _fast_keyword_route(self, text: str) -> str | None:
        lower = text.lower().strip()

        # Human escalation intent
        if any(kw in lower for kw in ["human", "live agent", "real person", "manager", "representative", "talk to person"]):
            return "human_handoff"

        # Greetings & farewells
        if lower in ["hi", "hello", "hey", "good morning", "good evening", "thanks", "thank you", "bye", "goodbye"]:
            return "respond"

        # Order & tracking intent
        if re.search(r'\bord-\w+', lower) or any(kw in lower for kw in ["track", "tracking", "order status", "cancel order", "cancel my order", "shipment"]):
            return "order"

        # Product recommendation intent
        if any(kw in lower for kw in ["recommend", "buy", "product", "laptop", "headphones", "shoes", "price", "stock", "search"]):
            return "recommendation"

        # Support & refund intent
        if any(kw in lower for kw in ["refund", "return", "broken", "complaint", "damaged", "wrong item"]):
            return "support"

        return None

    def decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state.get("messages", [])
        if not messages:
            return {"routing_decision": "respond"}

        last_human_msg = ""
        for m in reversed(messages):
            if hasattr(m, "type") and m.type == "human":
                last_human_msg = m.content
                break

        # Step 1: Fast Intent Matching (< 1ms)
        fast_choice = self._fast_keyword_route(last_human_msg)
        if fast_choice:
            logger.info("Supervisor fast-routed to: %s", fast_choice)
            return {"routing_decision": fast_choice}

        # Step 2: LLM Route Fallback
        if self.llm:
            try:
                response = self.llm.invoke([self.system] + messages[-3:])
                decision = response.content.strip().lower()
                valid = {"support", "order", "recommendation", "respond", "human_handoff"}
                if decision in valid:
                    return {"routing_decision": decision}
            except Exception as e:
                logger.warning("LLM supervisor routing failed: %s", str(e))

        return {"routing_decision": "support"}


_supervisor: SupervisorAgent | None = None


def get_supervisor() -> SupervisorAgent:
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor
