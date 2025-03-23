from typing import Any

from redis.asyncio import Redis

from src.application.interfaces.clients.cache import AbstractCacheClient


class RedisClient(AbstractCacheClient):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def __aenter__(self) -> "RedisClient":
        await self.redis.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        await self.redis.__aexit__(exc_type, exc_value, traceback)

    async def set(  # type: ignore
        self, /, *, key: str, expiration: int | None = None, **data
    ) -> str | None:
        await self.redis.hset(name=key, mapping=data)
        await self.redis.expire(name=key, time=expiration)

    async def get(self, key: str) -> dict[str, Any] | None:
        res: dict[str, Any] = await self.redis.hgetall(name=key)
        return res

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def keys(self, pattern: str) -> list[str]:
        res: list[str] = await self.redis.keys(pattern)
        return res
