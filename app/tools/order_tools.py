from datetime import datetime, timedelta
from typing import Optional
from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# In-memory order store – swap for a real DB / API in production
# ---------------------------------------------------------------------------
_ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "customer_id": "CUST-001",
        "status": "shipped",
        "items": [{"name": "Wireless Headphones", "qty": 1, "price": 79.99}],
        "total": 79.99,
        "estimated_delivery": (datetime.now() + timedelta(days=2)).isoformat(),
        "tracking": "1Z999AA10123456784",
        "carrier": "UPS",
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "customer_id": "CUST-001",
        "status": "processing",
        "items": [{"name": "Running Shoes", "qty": 1, "price": 129.99}],
        "total": 129.99,
        "estimated_delivery": (datetime.now() + timedelta(days=5)).isoformat(),
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "customer_id": "CUST-002",
        "status": "delivered",
        "items": [{"name": "Yoga Mat", "qty": 2, "price": 34.99}],
        "total": 69.98,
        "delivered_at": (datetime.now() - timedelta(days=1)).isoformat(),
    },
}


@tool
def get_order_status(order_id: str) -> str:
    """Look up the current status and details of an order."""
    order = _ORDERS.get(order_id)
    if not order:
        return f"Order '{order_id}' not found."
    items = ", ".join(f"{item['name']} x{item['qty']}" for item in order["items"])
    lines = [
        f"Order {order['order_id']} — Status: {order['status']}",
        f"Items: {items}",
        f"Total: ${order['total']:.2f}",
    ]
    if order.get("estimated_delivery"):
        lines.append(f"Estimated delivery: {order['estimated_delivery']}")
    if order.get("tracking"):
        lines.append(f"Tracking: {order['tracking']} ({order.get('carrier', 'N/A')})")
    return "\n".join(lines)


@tool
def track_shipment(order_id: str) -> str:
    """Get tracking information for a shipped order."""
    order = _ORDERS.get(order_id)
    if not order:
        return f"Order '{order_id}' not found."
    if order["status"] not in ("shipped", "delivered"):
        return f"Order {order_id} has not shipped yet (status: {order['status']})."
    return (
        f"Order {order_id}\n"
        f"Carrier: {order.get('carrier', 'N/A')}\n"
        f"Tracking: {order.get('tracking', 'N/A')}\n"
        f"Estimated delivery: {order.get('estimated_delivery', 'N/A')}"
    )


@tool
def cancel_order(order_id: str, reason: str) -> str:
    """Cancel an order that hasn't shipped yet. Provide the order ID and reason."""
    order = _ORDERS.get(order_id)
    if not order:
        return f"Order '{order_id}' not found."
    if order["status"] in ("shipped", "delivered"):
        return f"Cannot cancel order {order_id} – it has already been {order['status']}."
    _ORDERS[order_id]["status"] = "cancelled"
    return f"Order {order_id} has been cancelled. Reason: {reason}. A refund will be processed."


@tool
def get_order_history(customer_id: str, limit: Optional[int] = 10) -> str:
    """Retrieve recent orders for a customer."""
    orders = [o for o in _ORDERS.values() if o["customer_id"] == customer_id]
    if not orders:
        return f"No orders found for customer '{customer_id}'."
    orders.sort(key=lambda o: o.get("estimated_delivery", ""), reverse=True)
    lines = [f"Found {len(orders)} order(s):"]
    for o in orders[:limit]:
        lines.append(f"  • {o['order_id']} — {o['status']} — ${o['total']:.2f}")
    return "\n".join(lines)
