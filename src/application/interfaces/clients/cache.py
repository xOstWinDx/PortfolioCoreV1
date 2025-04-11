from abc import ABC, abstractmethod
from typing import Any, TypedDict

cache = TypedDict(
    "cache",
    {
        "data": dict[str, Any] | list[dict[str, Any]],
        "has_next": bool | None,
    },
)


class AbstractCacheClient(ABC):
    @abstractmethod
    async def set(
        self,
        /,
        *,
        key: str,
        expiration: int | None = None,
        data: cache,
    ) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> cache | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *keys: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def keys(self, pattern: str) -> list[str]:
        raise NotImplementedError
