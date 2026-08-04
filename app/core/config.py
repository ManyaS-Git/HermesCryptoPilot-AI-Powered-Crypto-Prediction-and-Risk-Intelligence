"""Application settings.

All configuration is environment-driven. No hardcoded credentials.
Secrets live in the environment / `.env` file (see `.env.example`).
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # --- Environment ---
    ENVIRONMENT: str = "development"  # development | testing | production
    APP_NAME: str = "Hermes Crypto Intelligence"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

    # --- HTTP ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # --- Database ---
    # SQLite by default (zero-dependency local dev); override with Postgres URL
    # e.g. postgresql+asyncpg://hermes:hermes@localhost:5432/hermes
    DATABASE_URL: str = "sqlite+aiosqlite:///./app/data/hermes.db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # --- Cache ---
    REDIS_URL: str = ""
    CACHE_TTL_SECONDS: int = 60
    CACHE_DEFAULT_SIZE: int = 4096

    # --- Auth ---
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/oauth/callback"

    # --- LLM ---
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "google/gemini-2.5-flash"

    # --- Market data providers ---
    COINGECKO_API_KEY: str = ""
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    COINMARKETCAP_API_KEY: str = ""
    CRYPTOPANIC_API_KEY: str = ""
    NEWSAPI_KEY: str = ""
    ETHERSCAN_API_KEY: str = ""
    GLASSNODE_API_KEY: str = ""
    INTOTHEBLOCK_API_KEY: str = ""
    ARKHAM_API_KEY: str = ""
    WHALE_ALERT_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHANNEL: str = ""

    # --- Prediction engine ---
    PREDICTION_HORIZON_BARS: int = 1
    PREDICTION_WINDOW: int = 256
    FEATURE_WINDOW: int = 128
    ENSEMBLE_MIN_SAMPLES: int = 60
    MONTE_CARLO_SIMS: int = 10_000
    MONTE_CARLO_HORIZON: int = 24
    VAR_CONFIDENCE: float = 0.95

    # --- Market defaults ---
    DEFAULT_ASSETS: list[str] = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX"]
    DEFAULT_INTERVAL: str = "15m"
    DEFAULT_QUOTE: str = "USDT"

    # --- Risk engine ---
    RISK_FREE_RATE: float = 0.02  # annualized
    KELLY_FRACTION: float = 0.25  # quarter Kelly default
    MAX_POSITION_SIZE: float = 0.20  # 20% of capital per position

    # --- Telemetry ---
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def cors_origins_list(self) -> list[str]:
        return list(self.CORS_ORIGINS)


@lru_cache
def get_settings() -> Settings:
    return Settings()
