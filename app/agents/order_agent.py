from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from app.config import settings
from app.tools.order_tools import get_order_status, track_shipment, cancel_order, get_order_history

PROMPT = """You are an e-commerce order management assistant.

You can:
- Check the status of an order
- Provide shipment tracking details
- Cancel orders (must not have shipped yet)
- Show recent order history

Always ask for the order ID if it's not provided. For cancellations, explain the refund timeline.
Be clear and concise — avoid markdown in responses."""


def _make_agent():
    return create_react_agent(
        model=ChatGroq(
            model=settings.order_model,
            temperature=0.1,
            groq_api_key=settings.groq_api_key,
        ),
        tools=[get_order_status, track_shipment, cancel_order, get_order_history],
        state_modifier=SystemMessage(content=PROMPT),
    )


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = _make_agent()
    return _agent
