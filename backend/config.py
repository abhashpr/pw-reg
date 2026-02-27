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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
