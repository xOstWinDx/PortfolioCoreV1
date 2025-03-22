from abc import ABC, abstractmethod

from src.application.interfaces.repositories.project_repo import (
    AbstractProjectsRepository,
)


class AbstractProjectsUnitOfWork(ABC):
    projects: AbstractProjectsRepository

    @abstractmethod
    async def __aenter__(self) -> "AbstractProjectsUnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        raise NotImplementedError
