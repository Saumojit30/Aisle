import logging
import uuid
import json
import asyncio
from typing import Optional, AsyncGenerator, List
from fastapi import APIRouter, HTTPException, Query, Request, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.graph import get_graph
from app.graph.state import AgentState
from app.security.budget_controller import get_budget_controller
from app.security.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_optional_user,
)
from app.db.database import get_async_session
from app.db.models import User, Product, Order, CustomerProfile
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = "customer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    customer_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    budget: dict


# ---------------------------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------------------------

@router.post("/auth/register", response_model=TokenResponse)
async def register_user(
    req: UserRegisterRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Register a new user and return an access token."""
    res = await session.execute(select(User).where(User.email == req.email))
    existing = res.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        role=req.role if req.role in ("customer", "admin") else "customer",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Create CustomerProfile if role is customer
    if user.role == "customer":
        prof = CustomerProfile(user_id=user.id)
        session.add(prof)
        await session.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """OAuth2 password form login endpoint."""
    res = await session.execute(select(User).where(User.email == form_data.username))
    user = res.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Return authenticated user details."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


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
async def chat(
    req: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
):
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:12]}"
    customer_id = current_user.id if current_user else req.customer_id

    state = _make_initial_state(req.message, session_id, customer_id)

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
# SSE streaming endpoint
# ---------------------------------------------------------------------------

@router.get("/chat/stream")
async def chat_stream(
    message: str = Query(...),
    session_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_optional_user),
):
    session_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"
    effective_customer_id = current_user.id if current_user else customer_id

    state = _make_initial_state(message, session_id, effective_customer_id)
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            async for event in graph.astream_events(state, config, version="v2"):
                kind = event.get("event", "")
                node = event.get("name", "")

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

                elif kind == "on_tool_start":
                    tool_input = event.get("data", {}).get("input", {})
                    yield (
                        f"event: tool_start\n"
                        f"data: {json.dumps({'node': node, 'tool': event.get('name', ''), 'args': tool_input})}\n\n"
                    )

                elif kind == "on_tool_end":
                    tool_output = event.get("data", {}).get("output", "")
                    yield (
                        f"event: tool_end\n"
                        f"data: {json.dumps({'node': node, 'tool': event.get('name', ''), 'result': str(tool_output)[:200]})}\n\n"
                    )

                elif kind == "on_chat_model_start":
                    yield f"event: thinking\ndata: {json.dumps({'node': node})}\n\n"

            # Final result
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
# Product Endpoints (Database-backed)
# ---------------------------------------------------------------------------

@router.get("/products")
async def list_products(session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(Product))
    return res.scalars().all()


@router.get("/products/{product_id}")
async def get_product(product_id: str, session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(Product).where(Product.id == product_id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ---------------------------------------------------------------------------
# Order Endpoints (Database-backed)
# ---------------------------------------------------------------------------

@router.get("/orders")
async def list_orders(session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(Order))
    return res.scalars().all()


@router.get("/orders/{order_id}")
async def get_order(order_id: str, session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(Order).where(Order.id == order_id))
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ---------------------------------------------------------------------------
# Customer Memory Endpoints (Database-backed)
# ---------------------------------------------------------------------------

@router.get("/memory/customers")
async def list_customers(session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(CustomerProfile))
    return res.scalars().all()


@router.get("/memory/customers/{user_id}")
async def get_customer_profile_api(user_id: str, session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(select(CustomerProfile).where(CustomerProfile.user_id == user_id))
    prof = res.scalar_one_or_none()
    if not prof:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    return prof


# ---------------------------------------------------------------------------
# Health & Stats
# ---------------------------------------------------------------------------

@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/budget/{session_id}")
async def budget_status(session_id: str):
    return get_budget_controller().get_summary(session_id)


# ---------------------------------------------------------------------------
# Admin Human-in-the-Loop (HITL) Approvals
# ---------------------------------------------------------------------------

class ApprovalResponseRequest(BaseModel):
    action: str  # "approved" or "rejected"
    reason: Optional[str] = None


@router.get("/admin/approvals")
async def list_pending_approvals(session: AsyncSession = Depends(get_async_session)):
    """List all pending manager approval requests."""
    from app.db.models import PendingApproval
    res = await session.execute(select(PendingApproval).where(PendingApproval.status == "pending"))
    return res.scalars().all()


@router.post("/admin/approvals/{approval_id}/respond")
async def respond_to_approval(
    approval_id: str,
    req: ApprovalResponseRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Approve or reject a pending human-in-the-loop action."""
    from app.db.models import PendingApproval
    res = await session.execute(select(PendingApproval).where(PendingApproval.id == approval_id))
    appr = res.scalar_one_or_none()
    if not appr:
        raise HTTPException(status_code=404, detail="Approval request not found")

    appr.status = req.action if req.action in ("approved", "rejected") else "rejected"
    appr.reason = req.reason
    session.add(appr)
    await session.commit()
    await session.refresh(appr)

    return {
        "id": appr.id,
        "status": appr.status,
        "message": f"Action {appr.status} successfully.",
    }
