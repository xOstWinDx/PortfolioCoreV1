from abc import ABC, abstractmethod

from src.domain.entities.tokens import (
    RefreshTokenPayload,
    AccessTokenPayload,
    AccessToken,
    RefreshToken,
)
from src.domain.entities.user import User


class AbstractAuthService(ABC):
    @abstractmethod
    def check_password(self, user_password: bytes, plain_password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_access_token(self, user: User) -> AccessToken:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user: User) -> RefreshToken:
        """
        Генерирует рефреш токен и возвращает сам токен + его айди
        :param user:
        :return: Кортеж токен + айди токена
        """
        raise NotImplementedError

    @abstractmethod
    def hash_password(self, password: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def decode_token(
        self, token: str
    ) -> RefreshTokenPayload | AccessTokenPayload | None:
        raise NotImplementedError
