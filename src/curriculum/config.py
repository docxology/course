"""Configuration management for the Curriculum Repository System."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = Field(default="CurriculumRepository", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/curriculum_db",
        alias="DATABASE_URL",
    )
    mongodb_url: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URL")
    mongodb_db_name: str = Field(default="curriculum_content", alias="MONGODB_DB_NAME")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Security
    secret_key: str = Field(default="change-this-secret-key", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], alias="CORS_ORIGINS"
    )

    # File Storage
    upload_dir: str = Field(default="./data/uploads", alias="UPLOAD_DIR")
    max_upload_size: int = Field(default=104857600, alias="MAX_UPLOAD_SIZE")  # 100MB
    allowed_extensions: str = Field(
        default=".pdf,.docx,.md,.tex,.mp4,.mp3,.jpg,.png,.gif", alias="ALLOWED_EXTENSIONS"
    )

    # CDN & Cloud Storage
    cdn_url: str = Field(default="https://cdn.example.com", alias="CDN_URL")
    s3_bucket: str = Field(default="curriculum-content", alias="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")

    # Search
    elasticsearch_url: str = Field(default="http://localhost:9200", alias="ELASTICSEARCH_URL")
    elasticsearch_index: str = Field(default="curriculum", alias="ELASTICSEARCH_INDEX")

    # Analytics
    analytics_enabled: bool = Field(default=True, alias="ANALYTICS_ENABLED")
    analytics_batch_size: int = Field(default=100, alias="ANALYTICS_BATCH_SIZE")

    # Email
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    email_from: str = Field(default="noreply@curriculum.example.com", alias="EMAIL_FROM")

    # Feature Flags
    enable_versioning: bool = Field(default=True, alias="ENABLE_VERSIONING")
    enable_analytics: bool = Field(default=True, alias="ENABLE_ANALYTICS")
    enable_ai_features: bool = Field(default=False, alias="ENABLE_AI_FEATURES")

    # Logging
    enable_file_logging: bool = Field(default=True, alias="ENABLE_FILE_LOGGING")
    enable_json_logging: bool = Field(default=False, alias="ENABLE_JSON_LOGGING")
    log_file: Optional[str] = Field(default=None, alias="LOG_FILE")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # Security
    allowed_hosts: List[str] = Field(default=["*"], alias="ALLOWED_HOSTS")
    require_https: bool = Field(default=False, alias="REQUIRE_HTTPS")

    # Monitoring
    enable_health_check: bool = Field(default=True, alias="ENABLE_HEALTH_CHECK")
    health_check_interval: int = Field(default=30, alias="HEALTH_CHECK_INTERVAL")
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed file extensions as a list."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
