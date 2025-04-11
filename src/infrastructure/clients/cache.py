import json
from typing import Any, Mapping, Sequence

from redis.asyncio import Redis

from src.application.interfaces.clients.cache import AbstractCacheClient, cache


class RedisCacheClient(AbstractCacheClient):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def set(
        self,
        /,
        *,
        key: str,
        expiration: int | None = None,
        data: Mapping[str, Any] | Sequence[Any],
    ) -> str | None:
        data = json.dumps(data, ensure_ascii=False)
        return await self.redis_client.set(name=key, value=data, ex=expiration)  # type: ignore

    async def get(self, key: str) -> cache | None:
        if data := await self.redis_client.get(key):
            return json.loads(data)  # type: ignore
        return None

    async def delete(self, *keys: str) -> None:
        if not keys:
            return None
        return await self.redis_client.delete(*keys)  # type: ignore

    async def keys(self, pattern: str) -> list[str]:
        return await self.redis_client.keys(pattern)  # type: ignore
