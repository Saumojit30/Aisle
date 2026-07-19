import threading
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CustomerMemory:
    def __init__(self):
        self._lock = threading.RLock()
        self._store: Dict[str, Dict[str, Any]] = {}
        self._sessions: Dict[str, str] = {}

    def get_or_create(self, customer_id: str) -> Dict[str, Any]:
        with self._lock:
            if customer_id not in self._store:
                self._store[customer_id] = {
                    "customer_id": customer_id,
                    "preferences": {},
                    "interests": [],
                    "interaction_count": 0,
                    "last_interaction": None,
                    "created_at": datetime.now().isoformat(),
                }
            return dict(self._store[customer_id])

    def update_preference(self, customer_id: str, category: str, value: Any) -> Dict[str, Any]:
        with self._lock:
            profile = self.get_or_create(customer_id)
            profile["preferences"][category] = value
            self._store[customer_id] = profile
            return dict(profile)

    def add_interest(self, customer_id: str, interest: str) -> Dict[str, Any]:
        with self._lock:
            profile = self.get_or_create(customer_id)
            if interest not in profile["interests"]:
                profile["interests"].append(interest)
            self._store[customer_id] = profile
            return dict(profile)

    def record_interaction(self, customer_id: str) -> None:
        with self._lock:
            profile = self.get_or_create(customer_id)
            profile["interaction_count"] += 1
            profile["last_interaction"] = datetime.now().isoformat()
            self._store[customer_id] = profile

    def link_session(self, session_id: str, customer_id: str) -> None:
        with self._lock:
            self._sessions[session_id] = customer_id

    def resolve_session(self, session_id: str) -> Optional[str]:
        with self._lock:
            return self._sessions.get(session_id)

    def get_preferences(self, customer_id: str) -> Dict[str, Any]:
        with self._lock:
            profile = self._store.get(customer_id, {})
            return dict(profile.get("preferences", {}))

    def stats(self) -> Dict:
        with self._lock:
            return {
                "customers": len(self._store),
                "active_sessions": len(self._sessions),
            }


_memory: Optional[CustomerMemory] = None


def get_customer_memory() -> CustomerMemory:
    global _memory
    if _memory is None:
        _memory = CustomerMemory()
    return _memory
