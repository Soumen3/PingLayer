"""
Application Configuration Module

This module handles all application settings using Pydantic Settings.
Environment variables are loaded from .env file and validated.

Design Decisions:
- Using Pydantic Settings for type-safe configuration
- Separate settings classes for different concerns (Database, JWT, etc.)
- Validation happens at startup, fail-fast approach
- Sensitive data (SECRET_KEY) must be provided via environment
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    """
    Main application settings.
    
    All settings are loaded from environment variables or .env file.
    Pydantic validates types and required fields at startup.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra env vars
    )
    
    # Application
    app_name: str = Field(default="PingLayer", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database
    database_url: str = Field(
        ...,  # Required field
        description="PostgreSQL connection string"
    )
    db_echo: bool = Field(default=False, description="SQLAlchemy echo SQL queries")
    
    # Security & JWT
    secret_key: str = Field(
        ...,  # Required field
        min_length=32,
        description="Secret key for JWT signing - must be 32+ characters"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=1440,  # 24 hours
        description="JWT token expiration in minutes"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for background jobs"
    )
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="API rate limit per minute per user"
    )
    
    # WhatsApp API (for future phases)
    whatsapp_api_url: str = Field(
        default="https://graph.facebook.com/v18.0",
        description="WhatsApp Business API base URL"
    )
    whatsapp_api_token: str = Field(
        default="",
        description="WhatsApp API token (optional for Phase 1)"
    )
    
    # Smart Links
    smart_link_base_url: str = Field(
        default="http://localhost:8000/s",
        description="Base URL for smart link redirects"
    )
    
    # GeoIP
    geoip_db_path: str = Field(
        default="./data/GeoLite2-City.mmdb",
        description="Path to GeoIP database file"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values"""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"


# Global settings instance
# This will be imported throughout the application
settings = Settings()


def generate_secret_key() -> str:
    """
    Generate a secure random secret key.
    Use this to generate a new SECRET_KEY for your .env file.
    
    Usage:
        python -c "from app.config import generate_secret_key; print(generate_secret_key())"
    """
    return secrets.token_urlsafe(32)


if __name__ == "__main__":
    # For testing configuration
    print("=== PingLayer Configuration ===")
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database_url}")
    print(f"Debug Mode: {settings.debug}")
    print(f"JWT Expiry: {settings.access_token_expire_minutes} minutes")
    print(f"CORS Origins: {settings.cors_origins}")
    print("=" * 40)
