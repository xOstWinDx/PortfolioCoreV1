from abc import ABC, abstractmethod

from src.application.interfaces.repositories.users import AbstractUsersRepository


class AbstractUsersUnitOfWork(ABC):
    users: AbstractUsersRepository

    @abstractmethod
    async def __aenter__(self) -> "AbstractUsersUnitOfWork":
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
