from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DEV_DATABASE_URL: str = "sqlite+aiosqlite:///dev_db.db"
    DEV_REDIS_URL: str = "redis://localhost:6379/0"
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str = Field(min_length=8)
    JWT_PRIVATE_KEY: Path = Path(__file__).parent.parent / "jwt_private_key.pem"
    JWT_PUBLIC_KEY: Path = Path(__file__).parent.parent / "jwt_public_key.pem"
    model_config = SettingsConfigDict(env_file=".env")


CONFIG = Config()
