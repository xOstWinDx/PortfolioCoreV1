from abc import ABC, abstractmethod


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
    def validate_token(self, token: str) -> bool:
        raise NotImplementedError
