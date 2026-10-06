"""EcoSort AI - Core Configuration Module."""

from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Metadata
    APP_NAME: str = "EcoSort AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"

    # Security & Networking
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    SECRET_KEY: str = "dev-secret-key-change-in-production-ecosort-ai"

    # Uploads & Rate Limiting
    MAX_UPLOAD_SIZE_MB: int = 5
    RATE_LIMIT: str = "10/minute"

    # Logging
    LOG_LEVEL: str = "INFO"

    # AI Provider Configuration
    AI_PROVIDER: str = "gemini"
    AI_MODEL: str = "gemini-3.5-flash"
    GEMINI_API_KEY: Optional[str] = None
    AI_TIMEOUT_SECONDS: int = 20
    AI_MAX_RETRIES: int = 2

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./ecosort.db"
    DATA_RETENTION_DAYS: int = 90
    METRICS_API_KEY: Optional[str] = None
    DB_POOL_PRE_PING: bool = True

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        """Ensure standard postgresql:// scheme is used if legacy postgres:// is supplied."""
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated origin strings into a clean list of origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return []

    @property
    def allowed_origins_list(self) -> List[str]:
        """Return the parsed list of allowed CORS origins."""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [self.ALLOWED_ORIGINS]

    @property
    def max_upload_size_bytes(self) -> int:
        """Return the maximum upload size converted to bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Helper to check if running in production mode."""
        return self.APP_ENV.lower() == "production"



settings = Settings()
