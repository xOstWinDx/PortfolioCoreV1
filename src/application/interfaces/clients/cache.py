from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class AbstractCacheClient(ABC):
    @abstractmethod
    async def set(
        self,
        /,
        *,
        key: str,
        expiration: int | None = None,
        data: Mapping[str, Any] | Sequence[Any],
    ) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *keys: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def keys(self, pattern: str) -> list[str]:
        raise NotImplementedError
