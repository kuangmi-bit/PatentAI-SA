"""
Application configuration using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


def parse_comma_separated(value: str) -> List[str]:
    """Parse comma-separated string to list"""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from env
    )
    
    # App Info
    app_name: str = Field(default="PatentAI Backend", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # CORS - comma-separated string from env
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3001",
        description="Allowed CORS origins (comma-separated)"
    )
    
    # Zhipu AI (智谱AI)
    zhipu_api_key: str = Field(default="", description="Zhipu API key")
    zhipu_base_url: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4",
        description="Zhipu API base URL"
    )
    zhipu_model: str = Field(default="glm-4", description="Zhipu chat model")
    zhipu_embedding_model: str = Field(
        default="embedding-3",
        description="Zhipu embedding model"
    )
    zhipu_embedding_dimensions: int = Field(
        default=1024,
        description="Embedding dimensions (256, 512, 1024, or 2048)"
    )
    
    # File Upload
    max_file_size: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum file size in bytes"
    )
    upload_dir: str = Field(default="./uploads", description="Upload directory")
    allowed_extensions: str = Field(
        default=".pdf,.docx,.txt",
        description="Allowed file extensions (comma-separated)"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./patentai.db",
        description="Database URL (SQLite or PostgreSQL)"
    )
    
    # Vector Database (optional)
    chroma_db_path: str = Field(default="./chroma_db", description="ChromaDB path")
    collection_name: str = Field(default="patents", description="Collection name")
    
    # Task Queue
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    
    # Helper methods
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        origins = parse_comma_separated(self.cors_origins)
        # Ensure 127.0.0.1 is included
        if 'http://127.0.0.1:3001' not in origins:
            origins.append('http://127.0.0.1:3001')
        return origins
    
    def get_allowed_extensions(self) -> List[str]:
        """Get allowed extensions as list"""
        return parse_comma_separated(self.allowed_extensions)


# Global settings instance
settings = Settings()
