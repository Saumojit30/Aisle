import pytest
from app.db.database import init_db, async_session_maker
from app.memory.customer_memory import get_customer_memory
from app.db.models import CustomerProfile
from sqlmodel import select


@pytest.mark.asyncio
async def test_customer_memory_db_persistence():
    await init_db()
    memory = get_customer_memory()
    customer_id = "test_persist_cust_999"

    # Clean up any existing test profile
    async with async_session_maker() as session:
        res = await session.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
        )
        existing = res.scalar_one_or_none()
        if existing:
            await session.delete(existing)
            await session.commit()

    # 1. Test get_or_create constructs profile in DB
    profile = await memory.get_or_create(customer_id)
    assert profile["customer_id"] == customer_id
    assert profile["interaction_count"] == 0

    # Verify it's actually in the database
    async with async_session_maker() as session:
        res = await session.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
        )
        prof_db = res.scalar_one_or_none()
        assert prof_db is not None
        assert prof_db.user_id == customer_id

    # 2. Test update_preference saves to DB
    await memory.update_preference(customer_id, "category", "Electronics")
    await memory.update_preference(customer_id, "brand", "Apple")

    async with async_session_maker() as session:
        res = await session.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
        )
        prof_db = res.scalar_one_or_none()
        assert prof_db.preferences.get("category") == "Electronics"
        assert prof_db.preferences.get("brand") == "Apple"

    # 3. Test add_interest saves to DB
    await memory.add_interest(customer_id, "headphones")
    await memory.add_interest(customer_id, "smartphones")

    async with async_session_maker() as session:
        res = await session.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
        )
        prof_db = res.scalar_one_or_none()
        assert "headphones" in prof_db.interests
        assert "smartphones" in prof_db.interests

    # 4. Test record_interaction increments count
    await memory.record_interaction(customer_id)
    
    async with async_session_maker() as session:
        res = await session.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
        )
        prof_db = res.scalar_one_or_none()
        assert prof_db.interaction_count == 1
        assert prof_db.last_interaction is not None
