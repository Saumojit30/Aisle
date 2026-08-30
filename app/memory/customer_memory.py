import logging
from typing import Dict, Optional, Any
from datetime import datetime
from sqlmodel import select
from sqlalchemy import func
from app.db.database import async_session_maker
from app.db.models import CustomerProfile

logger = logging.getLogger(__name__)


class CustomerMemory:
    def __init__(self):
        # Session mapping is transient and kept in memory
        self._sessions: Dict[str, str] = {}

    async def get_or_create(self, customer_id: str) -> Dict[str, Any]:
        async with async_session_maker() as session:
            try:
                res = await session.execute(
                    select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
                )
                profile = res.scalar_one_or_none()
                
                if not profile:
                    profile = CustomerProfile(
                        user_id=customer_id,
                        preferences={},
                        interests=[],
                        interaction_count=0,
                        last_interaction=None,
                        created_at=datetime.now().isoformat()
                    )
                    session.add(profile)
                    await session.commit()
                    await session.refresh(profile)
                
                return {
                    "customer_id": profile.user_id,
                    "preferences": profile.preferences or {},
                    "interests": profile.interests or [],
                    "interaction_count": profile.interaction_count,
                    "last_interaction": profile.last_interaction,
                    "created_at": profile.created_at,
                }
            except Exception as e:
                logger.error("Error in get_or_create for customer %s: %s", customer_id, str(e))
                # Fallback to dictionary in case of database errors (resilience)
                return {
                    "customer_id": customer_id,
                    "preferences": {},
                    "interests": [],
                    "interaction_count": 0,
                    "last_interaction": None,
                    "created_at": datetime.now().isoformat()
                }

    async def update_preference(self, customer_id: str, category: str, value: Any) -> Dict[str, Any]:
        async with async_session_maker() as session:
            try:
                res = await session.execute(
                    select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
                )
                profile = res.scalar_one_or_none()
                
                if not profile:
                    profile = CustomerProfile(
                        user_id=customer_id,
                        preferences={},
                        interests=[],
                        interaction_count=0,
                        last_interaction=None,
                        created_at=datetime.now().isoformat()
                    )
                    session.add(profile)
                
                # Assign a copy to trigger SQLModel/SQLAlchemy JSON change detection
                profile.preferences = {**(profile.preferences or {}), category: value}
                session.add(profile)
                await session.commit()
                await session.refresh(profile)
                
                return {
                    "customer_id": profile.user_id,
                    "preferences": profile.preferences,
                    "interests": profile.interests,
                    "interaction_count": profile.interaction_count,
                    "last_interaction": profile.last_interaction,
                    "created_at": profile.created_at,
                }
            except Exception as e:
                logger.error("Error updating preference for customer %s: %s", customer_id, str(e))
                return {
                    "customer_id": customer_id,
                    "preferences": {},
                    "interests": [],
                    "interaction_count": 0,
                    "last_interaction": None,
                    "created_at": datetime.now().isoformat()
                }

    async def add_interest(self, customer_id: str, interest: str) -> Dict[str, Any]:
        async with async_session_maker() as session:
            try:
                res = await session.execute(
                    select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
                )
                profile = res.scalar_one_or_none()
                
                if not profile:
                    profile = CustomerProfile(
                        user_id=customer_id,
                        preferences={},
                        interests=[],
                        interaction_count=0,
                        last_interaction=None,
                        created_at=datetime.now().isoformat()
                    )
                    session.add(profile)
                
                current_interests = list(profile.interests or [])
                if interest not in current_interests:
                    current_interests.append(interest)
                    profile.interests = current_interests
                    session.add(profile)
                    await session.commit()
                    await session.refresh(profile)
                
                return {
                    "customer_id": profile.user_id,
                    "preferences": profile.preferences,
                    "interests": profile.interests,
                    "interaction_count": profile.interaction_count,
                    "last_interaction": profile.last_interaction,
                    "created_at": profile.created_at,
                }
            except Exception as e:
                logger.error("Error adding interest for customer %s: %s", customer_id, str(e))
                return {
                    "customer_id": customer_id,
                    "preferences": {},
                    "interests": [],
                    "interaction_count": 0,
                    "last_interaction": None,
                    "created_at": datetime.now().isoformat()
                }

    async def record_interaction(self, customer_id: str) -> None:
        async with async_session_maker() as session:
            try:
                res = await session.execute(
                    select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
                )
                profile = res.scalar_one_or_none()
                if profile:
                    profile.interaction_count += 1
                    profile.last_interaction = datetime.now().isoformat()
                    session.add(profile)
                    await session.commit()
            except Exception as e:
                logger.error("Error recording interaction for customer %s: %s", customer_id, str(e))

    def link_session(self, session_id: str, customer_id: str) -> None:
        self._sessions[session_id] = customer_id

    def resolve_session(self, session_id: str) -> Optional[str]:
        return self._sessions.get(session_id)

    async def get_preferences(self, customer_id: str) -> Dict[str, Any]:
        async with async_session_maker() as session:
            try:
                res = await session.execute(
                    select(CustomerProfile).where(CustomerProfile.user_id == customer_id)
                )
                profile = res.scalar_one_or_none()
                return profile.preferences if profile else {}
            except Exception as e:
                logger.error("Error getting preferences for customer %s: %s", customer_id, str(e))
                return {}

    async def stats(self) -> Dict:
        async with async_session_maker() as session:
            try:
                res = await session.execute(select(func.count()).select_from(CustomerProfile))
                count = res.scalar()
                return {
                    "customers": count,
                    "active_sessions": len(self._sessions),
                }
            except Exception as e:
                logger.error("Error fetching stats: %s", str(e))
                return {
                    "customers": 0,
                    "active_sessions": len(self._sessions),
                }


_memory: Optional[CustomerMemory] = None


def get_customer_memory() -> CustomerMemory:
    global _memory
    if _memory is None:
        _memory = CustomerMemory()
    return _memory
