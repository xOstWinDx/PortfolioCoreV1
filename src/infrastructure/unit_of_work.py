from typing import Callable

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.repositories.projects import SQLProjectsRepository
from src.infrastructure.repositories.tokens import RedisTokensRepository
from src.infrastructure.repositories.users import SQLUsersRepository


class UnitOfWork(AbstractUnitOfWork):
    def __init__(
        self, session_factory: Callable[[], AsyncSession], redis_client: Redis
    ) -> None:
        super().__init__(
            user_repo_cls=SQLUsersRepository,
            project_repo_cls=SQLProjectsRepository,
            tokens_repo_cls=RedisTokensRepository,
        )
        self.session_factory = session_factory
        self.redis_client = redis_client
        self._sql_session: AsyncSession | None = None
        self._is_redis_connected = False

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

    @property
    def tokens(self) -> RedisTokensRepository:
        if not self._is_redis_connected:
            raise RuntimeError("Redis is not connected")
        return RedisTokensRepository(redis_client=self.redis_client)

    async def __aenter__(self) -> "UnitOfWork":
        self._sql_session = self.session_factory()
        await self._sql_session.__aenter__()
        await self.redis_client.__aenter__()
        self._is_redis_connected = True
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
        await self.redis_client.__aexit__(exc_type, exc_value, traceback)
        self._is_redis_connected = False
        self._sql_session = None
