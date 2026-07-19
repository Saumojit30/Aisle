from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from app.config import settings
from app.tools.product_tools import search_catalogue, get_product_details, check_inventory

PROMPT = """You are a knowledgeable e-commerce shopping assistant.

You can:
- Search the product catalogue
- Get detailed info on specific products
- Check stock availability
- Suggest alternatives and complementary items

When a customer asks for recommendations:
1. Ask about their needs (budget, category, use case)
2. Search the catalogue
3. Present 2-3 top options with key features
4. Offer to compare or check stock

Be enthusiastic and helpful — recommend products that genuinely fit the customer's needs."""


def _make_agent():
    return create_react_agent(
        model=ChatGroq(
            model=settings.recommendation_model,
            temperature=0.3,
            groq_api_key=settings.groq_api_key,
        ),
        tools=[search_catalogue, get_product_details, check_inventory],
        state_modifier=SystemMessage(content=PROMPT),
    )


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = _make_agent()
    return _agent
