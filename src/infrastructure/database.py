from typing import Annotated

from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import config

Str128 = Annotated[str, mapped_column(String(128))]


engine = create_async_engine(url=config.DEV_DATABASE_URL)

DEFAULT_SESSION_FACTORY = async_sessionmaker(engine, expire_on_commit=False)
