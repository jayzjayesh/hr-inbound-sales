"""
Application settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration via environment variables."""

    # FMCSA API
    FMCSA_API_KEY: str = "your_fmcsa_web_key_here"
    FMCSA_BASE_URL: str = "https://mobile.fmcsa.dot.gov/qc/services"

    # API Security
    API_KEY: str = "your_secret_api_key_here"

    # Negotiation
    NEGOTIATION_FLOOR: float = 0.90  # Accept offers >= 90% of loadboard rate

    # App
    APP_NAME: str = "Inbound Carrier Sales API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
