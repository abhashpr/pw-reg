"""Configuration management."""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # App config
    app_name: str = "PWNSAT Registration System"
    debug: bool = False
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Email config
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""  # Gmail app password
    
    # OTP config
    otp_expiry_minutes: int = 5
    otp_rate_limit_seconds: int = 60
    
    # CORS – add your Lightsail IP/domain in .env as:
    # CORS_ORIGINS=["http://your-ip","https://yourdomain.com"]
    cors_origins: List[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
    ]

    # Admin access – JSON array of email addresses that have admin privileges.
    # If not set, falls back to SENDER_EMAIL only.
    # Example: ADMIN_EMAILS=["alice@example.com","bob@example.com"]
    admin_emails: List[str] = []
    # Optional pre-generated token that grants access to admin OTP flow.
    # Set this in your .env as ADMIN_ACCESS_TOKEN to require the token for admin OTP requests.
    admin_access_token: str | None = None

    # Results search fuzzy matching settings
    # When enabled, results search will first filter by phone, then fuzzy-match name
    # Set to False to only match by phone number (ignoring name input)
    fuzzy_name_match_enabled: bool = True
    # Minimum similarity score (0-100) for a name to be considered a match
    fuzzy_name_threshold: int = 85


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
