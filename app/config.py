import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    groq_api_key: str = ""
    gemini_api_key: str = ""

    groq_api_key_file: Optional[str] = "/run/secrets/groq_api_key"
    gemini_api_key_file: Optional[str] = "/run/secrets/gemini_api_key"
    jwt_secret_file: Optional[str] = "/run/secrets/jwt_secret"

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

    def model_post_init(self, __context):
        # Load from Docker secrets files if present and env var is not set
        for secret_attr, file_attr in [
            ("gemini_api_key", "gemini_api_key_file"),
            ("groq_api_key", "groq_api_key_file"),
            ("jwt_secret", "jwt_secret_file"),
        ]:
            val = getattr(self, secret_attr)
            filePath = getattr(self, file_attr, None)
            if (not val or val == "super-secret-aisle-key-change-in-production-12345") and filePath and os.path.exists(filePath):
                try:
                    with open(filePath, "r", encoding="utf-8") as f:
                        secret_val = f.read().strip()
                        if secret_val:
                            setattr(self, secret_attr, secret_val)
                except Exception:
                    pass


settings = Settings()
