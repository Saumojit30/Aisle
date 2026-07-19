from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from app.config import settings
from typing import Any, Dict

PROMPT = """You route customer requests to the right specialist in an e-commerce system.

Available agents:
- support   — Returns, refunds, complaints, account help, order issues.
- order     — Order status, tracking, cancellations, shipping info.
- recommendation — Product suggestions, comparisons, finding items.
- respond   — Simple greetings, thanks, farewells, or when the request is handled.

Rules:
1. Pick the SINGLE best agent. Never guess an order ID or customer ID.
2. Route to "respond" when the customer is just greeting, thanking, or saying goodbye.
3. Route to "respond" if an agent already handled the request and no further action is needed.
4. If unsure, pick "support".

Respond with exactly one word — the agent name."""


class SupervisorAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.supervisor_model,
            temperature=0.0,
            groq_api_key=settings.groq_api_key,
        )
        self.system = SystemMessage(content=PROMPT)

    def decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state.get("messages", [])
        if not messages:
            return {"routing_decision": "respond"}

        response = self.llm.invoke([self.system] + messages[-3:])
        decision = response.content.strip().lower()

        valid = {"support", "order", "recommendation", "respond"}
        if decision not in valid:
            decision = "support"

        return {"routing_decision": decision}


_supervisor: SupervisorAgent | None = None


def get_supervisor() -> SupervisorAgent:
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor
