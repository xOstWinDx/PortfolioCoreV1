from abc import ABC, abstractmethod
from typing import Any


class AbstractCacheClient(ABC):
    @abstractmethod
    async def __aenter__(self) -> "AbstractCacheClient":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        raise NotImplementedError

    @abstractmethod
    async def set(  # type: ignore
        self,
        /,
        *,
        key: str,
        expiration: int | None = None,
        **data,
    ) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def keys(self, pattern: str) -> list[str]:
        raise NotImplementedError
