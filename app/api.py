import logging
import uuid
import json
import asyncio
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.graph.graph import get_graph
from app.graph.state import AgentState
from app.security.budget_controller import get_budget_controller
from app.memory.customer_memory import get_customer_memory
from app.tools.product_tools import _CATALOGUE
from app.tools.order_tools import _ORDERS
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    customer_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    budget: dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_initial_state(message: str, session_id: str, customer_id: Optional[str]) -> AgentState:
    return {
        "messages": [HumanMessage(content=message)],
        "session_id": session_id,
        "customer_id": customer_id,
        "routing_decision": "",
        "budget_ok": True,
        "budget_message": None,
        "guardrail_fail": False,
        "guardrail_message": None,
    }


def _extract_reply(result: dict) -> str:
    messages = result.get("messages", [])
    for m in reversed(messages):
        if hasattr(m, "type") and m.type == "ai" and m.content:
            return m.content
    return "I'm sorry, I couldn't process that. Please try again."


# ---------------------------------------------------------------------------
# Standard chat endpoint
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:12]}"

    state = _make_initial_state(req.message, session_id, req.customer_id)

    graph = get_graph()
    try:
        result = await graph.ainvoke(state, {"configurable": {"thread_id": session_id}})
    except Exception:
        logger.exception("Graph invocation failed for session %s", session_id)
        raise HTTPException(status_code=500, detail="Internal error processing request")

    reply = _extract_reply(result)
    budget = get_budget_controller().get_summary(session_id)
    return ChatResponse(
        session_id=session_id,
        reply=reply,
        budget=budget,
    )


# ---------------------------------------------------------------------------
# SSE streaming endpoint  (real-time agent pipeline visualization)
# ---------------------------------------------------------------------------

@router.get("/chat/stream")
async def chat_stream(
    message: str = Query(...),
    session_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
):
    session_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"
    state = _make_initial_state(message, session_id, customer_id)
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            async for event in graph.astream_events(state, config, version="v2"):
                kind = event.get("event", "")
                node = event.get("name", "")

                # Node start / end events
                if kind == "on_chain_start" and node in (
                    "guardrail", "supervisor", "support", "order",
                    "recommendation", "respond", "profiling"
                ):
                    yield f"event: node_start\ndata: {json.dumps({'node': node, 'timestamp': str(asyncio.get_event_loop().time())})}\n\n"

                elif kind == "on_chain_end" and node in (
                    "guardrail", "supervisor", "support", "order",
                    "recommendation", "respond", "profiling"
                ):
                    output = event.get("data", {}).get("output", {})
                    result = ""
                    if isinstance(output, dict):
                        if output.get("guardrail_fail"):
                            result = "blocked"
                        elif output.get("routing_decision"):
                            result = output["routing_decision"]
                        elif node == "profiling":
                            result = "done"

                    yield (
                        f"event: node_end\n"
                        f"data: {json.dumps({'node': node, 'result': result, 'timestamp': str(asyncio.get_event_loop().time())})}\n\n"
                    )

                # Tool start / end events
                elif kind == "on_tool_start":
                    tool_input = event.get("data", {}).get("input", {})
                    yield (
                        f"event: tool_start\n"
                        f"data: {json.dumps({'node': node, 'tool': event.get('name', ''), 'args': tool_input})}\n\n"
                    )

                elif kind == "on_tool_end":
                    tool_output = event.get("data", {}).get("output", "")
                    duration = 0
                    yield (
                        f"event: tool_end\n"
                        f"data: {json.dumps({'node': node, 'tool': event.get('name', ''), 'result': str(tool_output)[:200], 'duration_ms': duration})}\n\n"
                    )

                # Chat model events (for typing indicator)
                elif kind == "on_chat_model_start":
                    yield f"event: thinking\ndata: {json.dumps({'node': node})}\n\n"

            # After streaming completes, send final result
            result = await graph.ainvoke(state, config)
            reply = _extract_reply(result)
            budget = get_budget_controller().get_summary(session_id)
            yield (
                f"event: complete\n"
                f"data: {json.dumps({'reply': reply, 'budget': budget, 'session_id': session_id})}\n\n"
            )

        except Exception as e:
            logger.exception("Stream error for session %s", session_id)
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Product endpoints
# ---------------------------------------------------------------------------

@router.get("/products")
async def list_products():
    return [p for p in _CATALOGUE]


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    for p in _CATALOGUE:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


# ---------------------------------------------------------------------------
# Order endpoints
# ---------------------------------------------------------------------------

@router.get("/orders")
async def list_orders():
    return [o for o in _ORDERS.values()]


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = _ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ---------------------------------------------------------------------------
# Customer memory endpoints
# ---------------------------------------------------------------------------

@router.get("/memory/customers")
async def list_customers():
    mem = get_customer_memory()
    customers = []
    for cid in list(mem._store.keys()):
        customers.append(mem.get_or_create(cid))
    return customers


@router.get("/memory/customers/{customer_id}")
async def get_customer(customer_id: str):
    mem = get_customer_memory()
    return mem.get_or_create(customer_id)


# ---------------------------------------------------------------------------
# Health & Stats
# ---------------------------------------------------------------------------

@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/budget/{session_id}")
async def budget_status(session_id: str):
    return get_budget_controller().get_summary(session_id)


@router.get("/admin/stats")
async def admin_stats():
    bc = get_budget_controller().get_summary("")
    mem = get_customer_memory().stats()
    return {"budget": bc, "memory": mem}
