"""
Configuration management for ZenRows Device Profile API.
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # API Key
    api_key_pepper: str = Field(..., alias="API_KEY_PEPPER")
    
    # Request limits
    max_request_size: int = Field(default=1048576, alias="MAX_REQUEST_SIZE")  # 1MB
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8"
    }


# Global settings instance
settings = Settings()
