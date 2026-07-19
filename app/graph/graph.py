import logging
from typing import Any, Dict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from app.graph.state import AgentState
from app.config import settings
from app.security.budget_controller import get_budget_controller
from app.security.content_filter import get_content_filter
from app.agents.supervisor import get_supervisor
from app.agents.support_agent import get_agent as get_support_agent
from app.agents.recommendation_agent import get_agent as get_recommendation_agent
from app.agents.order_agent import get_agent as get_order_agent
from app.memory.customer_memory import get_customer_memory

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def guardrail_node(state: AgentState) -> Dict[str, Any]:
    """Pre-flight: check budget and redact PII.  If budget fails the graph
    short-circuits and the denial message is added to `messages`."""
    budget = get_budget_controller()
    session_id = state["session_id"]
    customer_id = state.get("customer_id")

    ok, msg = budget.can_proceed(session_id)
    if not ok:
        return {
            "budget_ok": False,
            "budget_message": msg,
            "guardrail_fail": True,
            "guardrail_message": msg,
            "messages": [AIMessage(content=(
                "I'm sorry, but I can't process this request right now. "
                f"{msg} Please contact support if you think this is an error."
            ))],
        }

    # Redact PII from the last human message
    msgs = state.get("messages", [])
    if msgs and hasattr(msgs[-1], "type") and msgs[-1].type == "human":
        redacted, findings, safe, safemsg = get_content_filter().sanitize(msgs[-1].content)
        if not safe:
            return {
                "budget_ok": True,
                "guardrail_fail": True,
                "guardrail_message": safemsg,
                "messages": [AIMessage(content="I can't process that request. Please rephrase.")],
            }
        if findings:
            logger.info("PII redacted in session %s", session_id)
            # Update the message content in place – the reducer keeps the original
            # reference so we modify the message object directly.
            msgs[-1].content = redacted

    # Link anonymous sessions to a customer ID for profiling
    if customer_id:
        get_customer_memory().link_session(session_id, customer_id)

    return {
        "budget_ok": True,
        "guardrail_fail": False,
        "guardrail_message": None,
    }


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Route to the appropriate specialist agent."""
    agent = get_supervisor()
    result = agent.decide(state)
    return {"routing_decision": result["routing_decision"]}


def support_node(state: AgentState) -> Dict[str, Any]:
    agent = get_support_agent()
    result = agent.invoke({"messages": state["messages"]})
    new_msgs = [m for m in result["messages"] if isinstance(m, AIMessage) and m.content]
    return {"messages": new_msgs[-1:]} if new_msgs else {}


def recommendation_node(state: AgentState) -> Dict[str, Any]:
    agent = get_recommendation_agent()
    result = agent.invoke({"messages": state["messages"]})
    new_msgs = [m for m in result["messages"] if isinstance(m, AIMessage) and m.content]
    return {"messages": new_msgs[-1:]} if new_msgs else {}


def order_node(state: AgentState) -> Dict[str, Any]:
    agent = get_order_agent()
    result = agent.invoke({"messages": state["messages"]})
    new_msgs = [m for m in result["messages"] if isinstance(m, AIMessage) and m.content]
    return {"messages": new_msgs[-1:]} if new_msgs else {}


def respond_node(state: AgentState) -> Dict[str, Any]:
    """Generate a natural reply for simple queries (greetings, thanks, etc.)."""
    llm = ChatGroq(
        model=settings.support_model,
        temperature=0.3,
        groq_api_key=settings.groq_api_key,
    )
    prompt = SystemMessage(content=(
        "You are a friendly e-commerce assistant. Keep responses brief and warm. "
        "Do NOT use markdown."
    ))
    reply = llm.invoke([prompt] + state["messages"])
    return {"messages": [reply]}


def profiling_node(state: AgentState) -> Dict[str, Any]:
    """Silently extract preferences from the conversation (side-effect only)."""
    customer_id = state.get("customer_id")
    if not customer_id:
        return {}

    from app.agents.profiling_agent import run as profile_run
    profile_run(customer_id, state["messages"])
    return {}


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def guardrail_router(state: AgentState) -> Literal["supervisor", "__end__"]:
    return "__end__" if state.get("guardrail_fail") else "supervisor"


def supervisor_router(state: AgentState) -> str:
    return state.get("routing_decision", "respond")


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("guardrail", guardrail_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("support", support_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("order", order_node)
    builder.add_node("respond", respond_node)
    builder.add_node("profiling", profiling_node)

    builder.set_entry_point("guardrail")

    builder.add_conditional_edges("guardrail", guardrail_router, {
        "supervisor": "supervisor",
        "__end__": END,
    })

    builder.add_conditional_edges("supervisor", supervisor_router, {
        "support": "support",
        "recommendation": "recommendation",
        "order": "order",
        "respond": "respond",
    })

    builder.add_edge("support", "profiling")
    builder.add_edge("recommendation", "profiling")
    builder.add_edge("order", "profiling")
    builder.add_edge("respond", "profiling")
    builder.add_edge("profiling", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
