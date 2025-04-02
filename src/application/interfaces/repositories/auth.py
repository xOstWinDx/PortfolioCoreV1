from abc import ABC, abstractmethod

from src.infrastructure.models.auth import AuthMetaData


class AbstractAuthRepository(ABC):
    @abstractmethod
    async def is_active(
        self, subject: str, credentials_id: str, device_id: str
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_active_one(
        self, subject: str, credentials_id: str, device_id: str
    ) -> AuthMetaData | None:
        raise NotImplementedError

    @abstractmethod
    async def get_active_all(
        self, subject: str = "*", credentials_id: str = "*", device_id: str = "*"
    ) -> list[AuthMetaData]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, subject_id: str, device_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def register(
        self,
        subject: str,
        credentials_id: str,
        expiration: int,
        credentials: str,
        device_id: str,
    ) -> bool:
        raise NotImplementedError
