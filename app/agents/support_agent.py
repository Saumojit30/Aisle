from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from app.config import settings
from app.tools.order_tools import get_order_status, track_shipment, cancel_order
from app.agents.llm_factory import get_llm

PROMPT = """You are a helpful e-commerce customer support agent.

You can:
- Look up order status (ask for the order ID)
- Track shipments
- Cancel orders that haven't shipped yet
- Answer questions about returns and refunds

Be empathetic and professional. If you need an order ID, ask for it politely.
If a cancellation succeeds, explain the refund process."""


def _make_agent():
    return create_react_agent(
        model=get_llm(
            model_name=settings.support_model,
            temperature=0.2,
        ),
        tools=[get_order_status, track_shipment, cancel_order],
        state_modifier=SystemMessage(content=PROMPT),
    )


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = _make_agent()
    return _agent
