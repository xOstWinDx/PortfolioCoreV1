from abc import ABC, abstractmethod

from src.application.interfaces.repositories.posts import AbstractPostsRepository
from src.application.interfaces.repositories.projects import AbstractProjectsRepository
from src.application.interfaces.repositories.users import AbstractUsersRepository


class AbstractUnitOfWork(ABC):
    @property
    @abstractmethod
    def users(self) -> AbstractUsersRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def projects(self) -> AbstractProjectsRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def posts(self) -> AbstractPostsRepository:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork":
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
