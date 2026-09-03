"""
Application configuration.

All secrets/config come from environment variables (see .env.example).
Never hardcode API keys or connection strings here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    APP_NAME: str = "VerifyNow API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080"

    # --- Database (PostgreSQL) ---
    DATABASE_URL: str = "postgresql+asyncpg://verifynow:verifynow@localhost:5432/verifynow"

    # --- Redis (cache + rate limiting) ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 6 * 60 * 60  # 6 hours
    RATE_LIMIT_PER_MINUTE: int = 20

    # --- Kafka (async verification jobs) ---
    KAFKA_ENABLED: bool = True
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_VERIFICATION_TOPIC: str = "verification-tasks"
    KAFKA_CONSUMER_GROUP: str = "verification-workers"

    # --- OpenAI (verification/reasoning + web search + vision) ---
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1"
    OPENAI_WEB_SEARCH_ENABLED: bool = True

    # --- Optional: local AI-generated-text signal model (HuggingFace) ---
    AI_TEXT_DETECTOR_MODEL: str = ""  # e.g. "roberta-base-openai-detector"; empty = disabled

    # --- Uploads ---
    MAX_UPLOAD_MB: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
