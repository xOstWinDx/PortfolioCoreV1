from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities.tokens import TokenMeta


class AbstractTokensRepository(ABC):
    @abstractmethod
    async def is_banned(self, subject: str = "*", token_id: str = "*") -> bool:
        """Проверяет забанен ли токен"""
        raise NotImplementedError

    @abstractmethod
    async def get_active_one(
        self, subject: str = "*", token_id: str = "*"
    ) -> tuple[str, TokenMeta] | None:
        """
        Получить ключ и метаданные токена
        :param subject:
        :param token_id:
        :return: кортеж из ключа и метаданных
        """
        raise NotImplementedError

    @abstractmethod
    async def get_active_all(
        self, subject: str = "*", token_id: str = "*"
    ) -> dict[str, TokenMeta] | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def ban(
        self, subject: str = "*", token_id: str = "*", reason: str = ""
    ) -> Any:
        """Перемещает токен из white листа в black лист"""
        raise NotImplementedError

    @abstractmethod
    async def register(
        self, subject: str, token_id: str, expiration: int, token_meta: TokenMeta
    ) -> bool:
        raise NotImplementedError
