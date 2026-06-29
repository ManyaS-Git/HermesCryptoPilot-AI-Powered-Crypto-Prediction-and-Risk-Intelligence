import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Profile: development, testing, production
    PROFILE: str = "development"
    
    # API Keys
    OPENROUTER_API_KEY: str = ""
    APIFY_API_TOKEN: str = ""
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    POLYMARKET_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///app/data/hermes_crypto.db"
    
    # Model configs
    KRONOS_MODEL_NAME: str = "NeoQuasar/Kronos-small"
    KRONOS_TOKENIZER_NAME: str = "NeoQuasar/Kronos-Tokenizer-base"
    LLM_MODEL: str = "openrouter/google/gemini-2.5-flash"
    
    # Telemetry
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the settings."""
    # Ensure profile-specific env files can override if needed
    profile = os.getenv("PROFILE", "development")
    env_file = f".env.{profile}"
    if os.path.exists(env_file):
        return Settings(_env_file=env_file)
    return Settings()
