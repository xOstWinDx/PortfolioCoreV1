from abc import ABC, abstractmethod

from src.application.interfaces.credentials import Credentials
from src.application.interfaces.repositories.auth import AbstractAuthRepository
from src.domain.entities.user import User
from src.domain.value_objects.auth import AuthorizationContext


class AbstractAuthService(ABC):
    def __init__(self, auth_repo: AbstractAuthRepository):
        self.auth_repo = auth_repo

    @abstractmethod
    async def authenticate(
        self,
        email: str,
        password: str,
        user: User | None,
        device_id: str,
    ) -> Credentials:
        raise NotImplementedError

    @abstractmethod
    async def authorize(
        self, credentials: Credentials | None, device_id: str
    ) -> AuthorizationContext:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def hash_password(password: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def renew_credentials(
        self, credentials: Credentials, user: User, device_id: str
    ) -> Credentials:
        raise NotImplementedError

    @abstractmethod
    def get_subject_id(self, credentials: Credentials) -> int:
        raise NotImplementedError
