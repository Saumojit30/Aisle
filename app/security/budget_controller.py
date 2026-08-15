import time
import threading
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date

logger = logging.getLogger(__name__)


MODEL_COST_MAP: Dict[str, tuple[float, float]] = {
    # Groq model rates per 1K tokens
    "llama-3.3-70b-versatile": (0.00059, 0.00079),
    "llama-3.1-8b-instant": (0.00005, 0.00008),
    "mixtral-8x7b-32768": (0.00024, 0.00024),
    "gemma2-9b-it": (0.00008, 0.00008),
    # Gemini 2.5 model rates per 1K tokens
    "gemini-2.5-pro": (0.00125, 0.01000),
    "gemini-2.5-flash": (0.00030, 0.00250),
}


@dataclass
class BudgetConfig:
    max_daily_cost: float = 10.0
    max_session_cost: float = 2.0
    max_tokens_per_session: int = 50000
    max_requests_per_minute: int = 30
    hard_stop_enabled: bool = True
    alert_at_percentage: float = 0.8


class BudgetController:
    def __init__(self, config: BudgetConfig):
        self.config = config
        self._lock = threading.RLock()
        self._daily_cost: float = 0.0
        self._daily_reset: date = datetime.now().date()
        self._session_tokens: Dict[str, int] = {}
        self._session_cost: Dict[str, float] = {}
        self._request_timestamps: Dict[str, list] = {}
        self._total_tokens_used: int = 0

    @staticmethod
    def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        rates = MODEL_COST_MAP.get(model, (0.0001, 0.0001))
        input_cost = (input_tokens / 1000) * rates[0]
        output_cost = (output_tokens / 1000) * rates[1]
        return input_cost + output_cost

    def can_proceed(self, session_id: str, estimated_total_tokens: int = 0) -> Tuple[bool, Optional[str]]:
        with self._lock:
            self._reset_daily_if_needed()

            if self._daily_cost >= self.config.max_daily_cost:
                return False, (
                    f"Daily budget (${self.config.max_daily_cost:.2f}) exhausted. "
                    "Please try again tomorrow."
                )

            session_cost = self._session_cost.get(session_id, 0.0)
            if session_cost >= self.config.max_session_cost:
                return False, (
                    f"Session budget (${self.config.max_session_cost:.2f}) exhausted. "
                    "Start a new session to continue."
                )

            session_tokens = self._session_tokens.get(session_id, 0)
            if session_tokens + estimated_total_tokens > self.config.max_tokens_per_session:
                return False, "Session token limit reached. Please start a new conversation."

            if self._is_rate_limited(session_id):
                return False, "Too many requests. Please wait a moment."

            return True, None

    def record_usage(self, session_id: str, model: str, input_tokens: int, output_tokens: int) -> None:
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens

        with self._lock:
            self._reset_daily_if_needed()
            self._session_tokens[session_id] = self._session_tokens.get(session_id, 0) + total_tokens
            self._session_cost[session_id] = self._session_cost.get(session_id, 0.0) + cost
            self._daily_cost += cost
            self._total_tokens_used += total_tokens

            logger.info(
                "usage model=%s input=%d output=%d cost=%.6f session_cost=%.4f daily_cost=%.4f",
                model, input_tokens, output_tokens, cost,
                self._session_cost[session_id], self._daily_cost,
            )

    def get_summary(self, session_id: str) -> Dict:
        with self._lock:
            self._reset_daily_if_needed()
            session_tokens = self._session_tokens.get(session_id, 0)
            session_cost = self._session_cost.get(session_id, 0.0)
            daily_pct = (self._daily_cost / self.config.max_daily_cost * 100) if self.config.max_daily_cost > 0 else 0

            return {
                "session_id": session_id,
                "session_tokens": session_tokens,
                "session_cost": round(session_cost, 4),
                "daily_cost": round(self._daily_cost, 4),
                "daily_usage_pct": round(daily_pct, 1),
                "total_tokens_all_time": self._total_tokens_used,
                "approaching_limit": daily_pct >= self.config.alert_at_percentage * 100,
            }

    def _reset_daily_if_needed(self) -> None:
        today = datetime.now().date()
        if today > self._daily_reset:
            logger.info("Daily budget reset")
            self._daily_cost = 0.0
            self._daily_reset = today

    def _is_rate_limited(self, session_id: str) -> bool:
        now = time.time()
        timestamps = self._request_timestamps.get(session_id, [])
        timestamps = [t for t in timestamps if now - t < 60]
        self._request_timestamps[session_id] = timestamps
        return len(timestamps) >= self.config.max_requests_per_minute


_budget_controller: Optional[BudgetController] = None


def get_budget_controller() -> BudgetController:
    global _budget_controller
    if _budget_controller is None:
        _budget_controller = BudgetController(BudgetConfig())
    return _budget_controller


def configure_budget_controller(config: BudgetConfig) -> BudgetController:
    global _budget_controller
    _budget_controller = BudgetController(config)
    return _budget_controller
