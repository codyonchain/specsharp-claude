from pydantic_settings import BaseSettings
from typing import Optional, List
import os
import json


class Settings(BaseSettings):
    app_name: str = "SpecSharp"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    database_url: str = "sqlite:///./specsharp.db"
    secret_key: str = ""  # Must be set via environment variable
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # CORS origins - can be overridden by environment variable
    @property
    def cors_origins(self) -> List[str]:
        # Check for environment variable first
        env_origins = os.getenv("CORS_ORIGINS")
        if env_origins:
            try:
                # Parse JSON array from environment variable
                return json.loads(env_origins)
            except json.JSONDecodeError:
                # Fallback to comma-separated list
                return [origin.strip() for origin in env_origins.split(",")]
        
        # Default origins
        default_origins = [
            "http://localhost:3000", 
            "http://localhost:3001", 
            "http://localhost:5173", 
            "https://specsharp.ai", 
            "https://www.specsharp.ai",
            "https://api.specsharp.ai",
            "https://specsharp.vercel.app"
        ]
        
        # In production, ensure production URLs are included
        if self.environment == "production":
            default_origins.extend([
                "https://specsharp.ai",
                "https://www.specsharp.ai",
                "https://api.specsharp.ai"
            ])
        
        return list(set(default_origins))  # Remove duplicates
    
    # Frontend URL - automatically set based on environment
    @property
    def frontend_url(self) -> str:
        if self.environment == "production":
            return os.getenv("FRONTEND_URL", "https://specsharp.ai")
        return os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # OAuth settings
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: Optional[str] = None
    
    # Session secret for OAuth state
    session_secret_key: str = ""
    
    # Stripe settings (optional)
    stripe_secret_key: Optional[str] = None
    
    # Redis settings for caching
    redis_url: str = "redis://localhost:6379"
    stripe_webhook_secret: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()