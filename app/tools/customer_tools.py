from langchain_core.tools import tool

_CUSTOMERS = {
    "CUST-001": {"customer_id": "CUST-001", "name": "Alice Johnson", "tier": "gold", "member_since": "2023-01-15"},
    "CUST-002": {"customer_id": "CUST-002", "name": "Bob Smith",     "tier": "silver", "member_since": "2024-03-20"},
}


@tool
def get_customer_profile(customer_id: str) -> str:
    """Look up basic profile information for a customer."""
    profile = _CUSTOMERS.get(customer_id)
    if not profile:
        return f"Customer '{customer_id}' not found."
    return (
        f"Name: {profile['name']}\n"
        f"Tier: {profile['tier']}\n"
        f"Member since: {profile['member_since']}"
    )


@tool
def get_purchase_summary(customer_id: str) -> str:
    """Get a summary of a customer's order history."""
    from .order_tools import get_order_history
    return get_order_history.invoke({"customer_id": customer_id})
