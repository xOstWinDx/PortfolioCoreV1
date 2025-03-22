from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.uow.project_uow import AbstractProjectsUnitOfWork
from src.infrastructure.repositories.projects import ProjectsRepository


class ProjectsUnitOfWork(AbstractProjectsUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> "ProjectsUnitOfWork":
        self.session = self.session_factory()
        await self.session.__aenter__()
        self.projects = ProjectsRepository(self.session)
        return self

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        await self.session.close()
        if exc_value is not None:
            await self.rollback()
        self.session = None
        self.projects = None  # type: ignore
