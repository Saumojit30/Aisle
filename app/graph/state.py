from typing import List, Dict, Optional, Any, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

    session_id: str
    customer_id: Optional[str]

    routing_decision: str  # "support" | "order" | "recommendation" | "respond" | "human_handoff"

    budget_ok: bool
    budget_message: Optional[str]

    guardrail_fail: bool
    guardrail_message: Optional[str]

    # Human-in-the-Loop & Escalation fields
    requires_human_approval: bool
    approval_id: Optional[str]
    escalation_reason: Optional[str]

    # Dynamic Model Degradation field
    degraded_mode: Optional[bool]
