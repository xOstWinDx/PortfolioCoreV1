from abc import ABC, abstractmethod
from typing import Any


class AbstractAuthRepository(ABC):
    @abstractmethod
    async def is_banned(self, subject: str = "*", credentials_id: str = "*") -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_active_one(
        self, subject: str = "*", credentials_id: str = "*"
    ) -> tuple[str, str] | None:
        raise NotImplementedError

    @abstractmethod
    async def get_active_all(
        self, subject: str = "*", credentials_id: str = "*"
    ) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def ban(
        self, subject: str = "*", credentials_id: str = "*", reason: str = ""
    ) -> Any:
        """Перемещает токен из white листа в black лист"""
        raise NotImplementedError

    @abstractmethod
    async def register(
        self, subject: str, credentials_id: str, expiration: int, payload: str
    ) -> bool:
        raise NotImplementedError
