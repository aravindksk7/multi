"""Application configuration."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Test Tool Platform")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    # Supports MySQL or SQLite
    # MySQL: mysql+pymysql://user:pass@host:port/dbname
    # SQLite: sqlite:///./testtool.db
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./testtool.db"  # Default to SQLite for easy setup
    )
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")


settings = Settings()
