from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.infrastructure.repositories.projects import SQLProjectsRepository
from src.infrastructure.repositories.users import SQLUsersRepository


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        super().__init__(
            user_repo_cls=SQLUsersRepository,
            project_repo_cls=SQLProjectsRepository,
        )
        self.session_factory = session_factory
        self._sql_session: AsyncSession | None = None

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
        self._sql_session = self.session_factory()
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
