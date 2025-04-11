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

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_PORT: int

    REFRESH_TOKEN_EXPIRE_SECONDS: int
    ACCESS_TOKEN_EXPIRE_SECONDS: int

    POSTS_CACHE_EXPIRE_SECONDS: int
    COMMENTS_CACHE_EXPIRE_SECONDS: int
    PROJECTS_CACHE_EXPIRE_SECONDS: int

    RATE_LIMIT_LIMIT: int = 10
    RATE_LIMIT_EXPIRE_SECONDS: int = 5

    BLOG_DB_NAME: str = "blog"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self) -> str:
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/admin"


CONFIG = Config()
