from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from src.application.interfaces.credentials import Credentials
from src.application.interfaces.repositories.auth import AbstractAuthRepository
from src.domain.entities.user import User
from src.domain.value_objects.auth import AuthorizationContext


class AbstractAuthService(ABC):
    def __init__(self, auth_repo: AbstractAuthRepository):
        self.auth_repo = auth_repo

    @abstractmethod
    async def authenticate(
        self, email: str, password: str, user: User | None
    ) -> Credentials:
        raise NotImplementedError

    @abstractmethod
    async def authorize(self, credentials: Credentials) -> AuthorizationContext:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def hash_password(password: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def renew_credentials(
        self, refresh_credentials: Credentials
    ) -> AsyncGenerator[int | Credentials, User]:
        """
        Генератор для обновления credentials с запросом пользователя извне.
        Ожидаемое использование:
        1. next() -> int: возвращает user_id из токена.
        2. send(user_data) -> None: принимает данные пользователя.
        3. next() -> Credentials: возвращает новые креденшалы.

        Raises:
            StopIteration: если вызвано больше шагов, чем ожидается.
            ValueError: если переданы некорректные данные.
        """
        raise NotImplementedError
