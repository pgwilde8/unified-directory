"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App Configuration
    APP_NAME: str = "Business Directory"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 9178
    
    # Database
    DATABASE_URL: str = "postgresql://dir-admin:Securepass@localhost:5432/directories"
    
    # Security
    SECRET_KEY: str = "Ege4aZ0BP6JCKnBJ7OoUnLk8tW_EIDU2qSll5ntUfFE"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth Configuration - from environment variables only
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:9178/api/auth/google/callback")
    
    # Business Directory Settings
    MAX_BUSINESS_LISTINGS_PER_USER: int = 10
    BUSINESS_APPROVAL_REQUIRED: bool = True
    ALLOWED_BUSINESS_CATEGORIES: str = "restaurant,retail,service,healthcare,education,entertainment,automotive,professional"
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "jpg,jpeg,png,pdf,doc,docx"
    UPLOAD_DIRECTORY: str = "uploads/"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@yourdomain.com"
    
    # Stripe Configuration
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Legacy Admin Authentication (for system admin)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    SESSION_TIMEOUT_HOURS: int = 24
    
    # Timing Controls
    LOGIN_START_HOUR: int = 6  # 6 AM
    LOGIN_END_HOUR: int = 22   # 10 PM
    TIMEZONE: str = "US/Eastern"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
