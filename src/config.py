from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DEV_DATABASE_URL: str = "sqlite+aiosqlite:///dev_db.db"

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
