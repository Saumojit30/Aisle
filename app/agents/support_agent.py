from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from app.config import settings
from app.tools.order_tools import get_order_status, track_shipment, cancel_order

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
        model=ChatGroq(
            model=settings.support_model,
            temperature=0.2,
            groq_api_key=settings.groq_api_key,
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
