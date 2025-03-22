from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from src.application.interfaces.repositories.project_repo import (
    AbstractProjectsRepository,
)

U = TypeVar("U")


class AbstractProjectsUnitOfWork(ABC, Generic[U]):
    projects: AbstractProjectsRepository

    @abstractmethod
    async def __aenter__(self) -> U:
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
