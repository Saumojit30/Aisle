from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    groq_api_key: str = ""

    supervisor_model: str = "llama-3.3-70b-versatile"
    support_model: str = "llama-3.1-8b-instant"
    recommendation_model: str = "llama-3.3-70b-versatile"
    order_model: str = "mixtral-8x7b-32768"
    profiling_model: str = "llama-3.1-8b-instant"

    max_daily_cost: float = 10.0
    max_session_cost: float = 2.0
    max_tokens_per_session: int = 50000
    max_requests_per_minute: int = 30
    budget_alert_percentage: float = 0.8
    hard_stop_enabled: bool = True

    google_cloud_project: Optional[str] = None
    google_cloud_location: str = "us-central1"

    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
