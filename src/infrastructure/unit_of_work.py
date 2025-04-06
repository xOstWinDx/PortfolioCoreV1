from typing import Callable

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.repositories.posts import MongoPostsRepository
from src.infrastructure.repositories.projects import SQLProjectsRepository
from src.infrastructure.repositories.users import SQLUsersRepository


class UnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        sql_session_factory: Callable[[], AsyncSession],
        mongo_client_factory: Callable[[], AsyncIOMotorClient],
    ) -> None:
        self.sql_session_factory = sql_session_factory
        self.mongo_client_factory = mongo_client_factory
        self._mongo_client: AsyncIOMotorClient | None = None
        self._sql_session: AsyncSession | None = None

    @property
    def posts(self) -> MongoPostsRepository:
        if self._mongo_client is None:
            raise RuntimeError("Mongo is not connected")
        return MongoPostsRepository(mongo_client=self._mongo_client)

    @property
    def users(self) -> SQLUsersRepository:
        if self._sql_session is None:
            raise RuntimeError("Redis is not connected")
        return SQLUsersRepository(session=self._sql_session)

    @property
    def projects(self) -> SQLProjectsRepository:
        if self._sql_session is None:
            raise RuntimeError("Redis is not connected")
        return SQLProjectsRepository(session=self._sql_session)

    async def __aenter__(self) -> "UnitOfWork":
        self._mongo_client = self.mongo_client_factory()
        self._sql_session = self.sql_session_factory()
        await self._sql_session.__aenter__()
        return self

    async def commit(self) -> None:
        if self._sql_session is None:
            raise RuntimeError("No connection")
        await self._sql_session.commit()

    async def rollback(self) -> None:
        if self._sql_session is None:
            raise RuntimeError("No connection")
        await self._sql_session.rollback()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        if exc_type is not None:
            await self.rollback()
        if self._sql_session is not None:
            await self._sql_session.__aexit__(exc_type, exc_value, traceback)
        self._sql_session = None
