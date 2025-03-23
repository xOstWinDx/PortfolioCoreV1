from abc import ABC, abstractmethod
from typing import Any


class AbstractAuthService(ABC):
    @abstractmethod
    def check_password(self, username: str, password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_access_token(self, username: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, username: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def hash_password(self, password: str) -> str | bytes:
        raise NotImplementedError

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]:
        raise NotImplementedError
