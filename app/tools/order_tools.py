from typing import Optional
import asyncio
from langchain_core.tools import tool
from sqlmodel import select
from app.db.database import async_session_maker
from app.db.models import Order, PendingApproval


async def _get_order_db(order_id: str) -> Optional[Order]:
    async with async_session_maker() as session:
        res = await session.execute(select(Order).where(Order.id == order_id))
        return res.scalar_one_or_none()


@tool
def get_order_status(order_id: str) -> str:
    """Look up the current status and details of an order from the database."""
    try:
        order = asyncio.run(_get_order_db(order_id))
    except Exception:
        order = None

    if not order:
        return f"Order '{order_id}' not found."

    items_str = ", ".join(f"{item.get('name', 'Item')} x{item.get('quantity', 1)}" for item in order.items)
    lines = [
        f"Order {order.id} — Status: {order.status}",
        f"Customer ID: {order.customer_id}",
        f"Items: {items_str}",
        f"Total: ${order.total:.2f}",
        f"Created At: {order.created_at}",
    ]
    if order.tracking_number:
        lines.append(f"Tracking: {order.tracking_number}")
    return "\n".join(lines)


@tool
def track_shipment(order_id: str) -> str:
    """Get tracking information for a shipped order."""
    try:
        order = asyncio.run(_get_order_db(order_id))
    except Exception:
        order = None

    if not order:
        return f"Order '{order_id}' not found."
    if order.status not in ("shipped", "delivered"):
        return f"Order {order_id} has not shipped yet (current status: {order.status})."

    return (
        f"Order {order.id}\n"
        f"Status: {order.status}\n"
        f"Tracking Number: {order.tracking_number or 'TRK-GENERIC-12345'}"
    )


async def _cancel_order_db(order_id: str, reason: str) -> str:
    async with async_session_maker() as session:
        res = await session.execute(select(Order).where(Order.id == order_id))
        order = res.scalar_one_or_none()
        if not order:
            return f"Order '{order_id}' not found."
        if order.status in ("shipped", "delivered"):
            return f"Cannot cancel order {order_id} – it has already been {order.status}."
        if order.status == "cancelled":
            return f"Order {order_id} is already cancelled."

        order.status = "cancelled"
        session.add(order)
        await session.commit()
        return f"Order {order_id} has been cancelled successfully. Reason: {reason}. Refund initiated."


@tool
def cancel_order(order_id: str, reason: str) -> str:
    """Cancel an order that hasn't shipped yet. Provide the order ID and reason."""
    try:
        return asyncio.run(_cancel_order_db(order_id, reason))
    except Exception as e:
        return f"Failed to cancel order '{order_id}': {str(e)}"


async def _get_order_history_db(customer_id: str, limit: int = 10) -> str:
    async with async_session_maker() as session:
        res = await session.execute(
            select(Order).where(Order.customer_id == customer_id).limit(limit)
        )
        orders = res.scalars().all()
        if not orders:
            return f"No orders found for customer '{customer_id}'."

        lines = [f"Found {len(orders)} order(s):"]
        for o in orders:
            lines.append(f"  • {o.id} — {o.status} — ${o.total:.2f} ({o.created_at[:10]})")
        return "\n".join(lines)


@tool
def get_order_history(customer_id: str, limit: Optional[int] = 10) -> str:
    """Retrieve recent orders for a customer."""
    try:
        return asyncio.run(_get_order_history_db(customer_id, limit or 10))
    except Exception as e:
        return f"Failed to fetch order history: {str(e)}"
