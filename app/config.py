"""Application Configuration Module."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "OmniFinance Multi-Country Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "dev-secret-key-please-change-in-production"

    # Groq AI Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Database
    DATABASE_URL: str = "sqlite:///./finance_platform.db"

    # Country & i18n
    DEFAULT_COUNTRY: str = "fi"
    DEFAULT_LANGUAGE: str = "en"

    # Monetization
    ENABLE_ADS: bool = False
    ADSENSE_CLIENT_ID: str = "ca-pub-0000000000000000"

    # Paths
    BASE_DIR: Path = BASE_DIR
    APP_DIR: Path = BASE_DIR / "app"
    COUNTRIES_DIR: Path = BASE_DIR / "app" / "countries"
    STATIC_DIR: Path = BASE_DIR / "app" / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "app" / "templates"

settings = Settings()
