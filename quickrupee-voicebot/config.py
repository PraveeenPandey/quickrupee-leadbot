"""
Configuration management for QuickRupee Voice Bot - Demo Version
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-realtime-preview-2024-12-17"

    # Application Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Eligibility Criteria
    MIN_SALARY: int = 25000
    ELIGIBLE_CITIES: List[str] = ["delhi", "mumbai", "bangalore"]

    # Voice Configuration
    VOICE: str = "alloy"  # OpenAI TTS voice options: alloy, echo, fable, onyx, nova, shimmer
    LANGUAGE: str = "en"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
