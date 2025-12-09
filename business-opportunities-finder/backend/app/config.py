"""
Configuration management for the Business Opportunities Finder application.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://oppfinder:oppfinder_password@db:5432/opportunities_db"
    
    # Google Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    gemini_temperature: float = 0.3
    
    # Reddit API
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "BusinessOpportunitiesFinder/1.0"
    
    # ProductHunt API (Optional)
    producthunt_api_key: Optional[str] = None
    
    # Twitter API (Optional)
    twitter_bearer_token: Optional[str] = None
    
    # Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_to: str = ""
    
    # Scheduler Configuration
    daily_run_hour: int = 7
    daily_run_minute: int = 0
    timezone: str = "Europe/Madrid"
    
    # Scoring Configuration
    score_weight_pain: float = 0.30
    score_weight_frequency: float = 0.20
    score_weight_willingness_to_pay: float = 0.20
    score_weight_low_competition: float = 0.15
    score_weight_technical_feasibility: float = 0.10
    score_weight_ai_synergy: float = 0.05
    
    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:8000,http://localhost:3000"
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 30
    
    # Paths
    reports_dir: str = "/app/reports"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_scoring_weights() -> dict:
    """Get scoring weights as a dictionary."""
    return {
        "pain": settings.score_weight_pain,
        "frequency": settings.score_weight_frequency,
        "willingness_to_pay": settings.score_weight_willingness_to_pay,
        "low_competition": settings.score_weight_low_competition,
        "technical_feasibility": settings.score_weight_technical_feasibility,
        "ai_synergy": settings.score_weight_ai_synergy,
    }


def get_cors_origins() -> list:
    """Get CORS origins as a list."""
    return [origin.strip() for origin in settings.cors_origins.split(",")]
