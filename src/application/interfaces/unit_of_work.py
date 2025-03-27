from abc import ABC, abstractmethod

from src.application.interfaces.repositories.projects import AbstractProjectsRepository
from src.application.interfaces.repositories.tokens import AbstractTokensRepository
from src.application.interfaces.repositories.users import AbstractUsersRepository


class AbstractUnitOfWork(ABC):
    def __init__(
        self,
        user_repo_cls: type[AbstractUsersRepository],
        project_repo_cls: type[AbstractProjectsRepository],
        tokens_repo_cls: type[AbstractTokensRepository],
    ):
        self.user_repo_cls = user_repo_cls
        self.project_repo_cls = project_repo_cls
        self.tokens_repo_cls = tokens_repo_cls

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
    def tokens(self) -> AbstractTokensRepository:
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
