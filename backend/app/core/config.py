from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "SpecSharp"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    database_url: str = "sqlite:///./specsharp.db"
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()