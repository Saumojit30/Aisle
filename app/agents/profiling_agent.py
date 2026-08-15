import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.memory.customer_memory import get_customer_memory
from app.agents.llm_factory import get_llm
from typing import Any, Dict

logger = logging.getLogger(__name__)

PROMPT = """Analyse the conversation below and extract customer preferences and interests.
Return ONLY a JSON object with these optional fields (omit fields that aren't relevant):
{
  "preferred_categories": ["Electronics", "Fitness", ...],
  "interests": ["headphones", "running", "yoga", ...],
  "budget_preference": "budget" | "mid-range" | "premium",
  "shopping_occasion": "gift" | "personal" | "business",
  "summary": "one-line summary of what this customer cares about"
}"""


def run(customer_id: str, messages: list) -> Dict[str, Any]:
    memory = get_customer_memory()
    profile = memory.get_or_create(customer_id)

    chat_messages = [m for m in messages if hasattr(m, "type") and m.type in ("human", "ai")]
    if not chat_messages:
        return profile

    llm = get_llm(
        model_name=settings.profiling_model,
        temperature=0.0,
    )

    try:
        response = llm.invoke([
            SystemMessage(content=PROMPT),
            HumanMessage(content="\n".join(
                f"{'Customer' if m.type == 'human' else 'Agent'}: {m.content}"
                for m in chat_messages[-6:]
            )),
        ])

        import json, re
        content = response.content.strip()
        m = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
        json_str = m.group(1).strip() if m else content
        data = json.loads(json_str)

        if "preferred_categories" in data:
            for cat in data["preferred_categories"]:
                memory.update_preference(customer_id, cat, True)

        if "interests" in data:
            for interest in data["interests"]:
                memory.add_interest(customer_id, interest)

        if "summary" in data:
            memory.update_preference(customer_id, "_summary", data["summary"])

        logger.info("Profiling complete for %s", customer_id)
    except Exception:
        logger.exception("Profiling failed for %s", customer_id)

    return memory.get_or_create(customer_id)
