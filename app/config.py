from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    groq_api_key: str = ""
    gemini_api_key: str = ""

    # Default to Gemini models for the enterprise setup
    supervisor_model: str = "gemini-2.5-flash"
    support_model: str = "gemini-2.5-flash-lite"
    recommendation_model: str = "gemini-2.5-flash"
    order_model: str = "gemini-2.5-flash-lite"
    profiling_model: str = "gemini-2.5-flash-lite"

    max_daily_cost: float = 10.0
    max_session_cost: float = 2.0
    max_tokens_per_session: int = 50000
    max_requests_per_minute: int = 30
    budget_alert_percentage: float = 0.8
    hard_stop_enabled: bool = True

    google_cloud_project: Optional[str] = None
    google_cloud_location: str = "us-central1"

    # Database & Security Settings
    database_url: str = "sqlite+aiosqlite:///./aisle.db"
    jwt_secret: str = "super-secret-aisle-key-change-in-production-12345"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
