from typing import Optional
from langchain_core.tools import tool
from sqlmodel import select
from app.db.database import async_session_maker
from app.db.models import CustomerProfile, User
from app.tools.utils import run_async_sync


async def _get_customer_profile_db(customer_id: str) -> Optional[dict]:
    async with async_session_maker() as session:
        # Check profile
        res = await session.execute(select(CustomerProfile).where(CustomerProfile.user_id == customer_id))
        prof = res.scalar_one_or_none()
        if prof:
            return {
                "customer_id": prof.user_id,
                "preferences": prof.preferences,
                "interests": prof.interests,
                "created_at": prof.created_at,
            }

        # Check user
        res_u = await session.execute(select(User).where(User.id == customer_id))
        user = res_u.scalar_one_or_none()
        if user:
            return {
                "customer_id": user.id,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
            }
        return None


@tool
def get_customer_profile(customer_id: str) -> str:
    """Look up basic profile information for a customer from the database."""
    try:
        data = run_async_sync(_get_customer_profile_db(customer_id))
    except Exception:
        data = None

    if not data:
        return f"Customer '{customer_id}' not found."

    lines = [f"Customer ID: {data['customer_id']}"]
    if "email" in data:
        lines.append(f"Email: {data['email']}")
    if "preferences" in data and data["preferences"]:
        lines.append(f"Preferences: {data['preferences']}")
    if "interests" in data and data["interests"]:
        lines.append(f"Interests: {', '.join(data['interests'])}")
    lines.append(f"Member since: {data['created_at'][:10]}")
    return "\n".join(lines)


@tool
def get_purchase_summary(customer_id: str) -> str:
    """Get a summary of a customer's order history."""
    from .order_tools import get_order_history
    return get_order_history.invoke({"customer_id": customer_id})
