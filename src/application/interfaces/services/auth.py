from abc import ABC, abstractmethod

from src.domain.entities.tokens import (
    RefreshTokenPayload,
    AccessTokenPayload,
    AccessToken,
    RefreshToken,
)


class AbstractAuthService(ABC):
    @abstractmethod
    def check_password(self, username: str, password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_access_token(self, username: str) -> AccessToken:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, username: str) -> RefreshToken:
        """
        Генерирует рефреш токен и возвращает сам токен + его айди
        :param username:
        :return: Кортеж токен + айди токена
        """
        raise NotImplementedError

    @abstractmethod
    def hash_password(self, password: str) -> str | bytes:
        raise NotImplementedError

    @abstractmethod
    def decode_token(
        self, token: str
    ) -> RefreshTokenPayload | AccessTokenPayload | None:
        raise NotImplementedError
