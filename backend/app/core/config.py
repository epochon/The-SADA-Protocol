"""
Centralized Configuration using Pydantic Settings
Type-safe, validated configuration with environment variable support
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ==================== API Keys ====================
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    tavily_api_key: Optional[str] = Field(default=None, alias="TAVILY_API_KEY")
    alphavantage_api_key: Optional[str] = Field(default=None, alias="ALPHAVANTAGE_API_KEY")
    
    # ==================== Timeouts (seconds) ====================
    youtube_timeout: int = Field(default=30, description="Timeout for YouTube transcript fetching")
    yfinance_timeout: int = Field(default=15, description="Timeout for yfinance API calls") 
    openai_timeout: int = Field(default=60, description="Timeout for OpenAI API calls")
    groq_timeout: int = Field(default=30, description="Timeout for Groq API calls")
    
    # ==================== Cache Settings ====================
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds (5 minutes)")
    cache_max_size: int = Field(default=100, description="Maximum number of cached items")
    
    # ==================== Decision Thresholds ====================
    confidence_threshold: float = Field(default=60.0, description="Minimum confidence score to VERIFY")
    bullshit_auto_refuse_threshold: int = Field(default=80, description="Bullshit score that triggers auto-refuse")
    
    # ==================== Environment ====================
    env: str = Field(default="dev", alias="ENV")
    debug: bool = Field(default=True, description="Enable debug mode")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra env vars
        "populate_by_name": True  # Allow using both alias and field name
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Use this function to get settings throughout the application.
    """
    return Settings()


# Convenience shortcuts
settings = get_settings()
