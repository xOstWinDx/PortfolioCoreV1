from typing import Any

from redis.asyncio import Redis

from src.application.interfaces.repositories.auth import AbstractAuthRepository


class JWTRedisAuthRepository(AbstractAuthRepository):
    ban_prefix = "black"
    white_prefix = "white"

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def __aenter__(self) -> "JWTRedisAuthRepository":
        await self.redis_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        await self.redis_client.__aexit__(exc_type, exc_val, exc_tb)

    async def is_banned(self, subject: str = "*", credentials_id: str = "*") -> bool:  # type: ignore
        key = f"{self.ban_prefix}:{subject}:{credentials_id}"
        return bool(await self.redis_client.exists(key))

    async def get_active_one(  # type: ignore
        self, subject: str = "*", credentials_id: str = "*"
    ) -> tuple[str, str] | None:
        key = f"{self.white_prefix}:{subject}:{credentials_id}"
        token: str = await self.redis_client.get(key)
        if not token:
            return None
        return key, token

    async def get_active_all(  # type: ignore
        self, subject: str = "*", credentials_id: str = "*"
    ) -> list[str]:
        keys: list[str] = await self.redis_client.keys(
            f"{self.white_prefix}:{subject}:{credentials_id}"
        )
        res = []
        for key in keys:
            token = await self.redis_client.get(key)
            if not token:
                continue
            res.append(token)
        return res

    async def delete(self, key: str) -> bool:  # type: ignore
        res = await self.redis_client.delete(key)
        return bool(res)

    async def ban(  # type: ignore
        self, subject: str = "*", credentials_id: str = "*", reason: str = ""
    ) -> Any:
        src = f"{self.white_prefix}:{subject}:{credentials_id}"
        dst = f"{self.ban_prefix}:{subject}:{credentials_id}"
        return await self.redis_client.rename(src, dst)

    async def register(  # type: ignore
        self, subject: str, credentials_id: str, expiration: int, payload: str
    ) -> bool:
        key = f"{self.white_prefix}:{subject}:*"
        keys = await self.redis_client.keys(key)

        if len(keys) >= 10:
            to_delete = keys[9:]
            await self.redis_client.delete(to_delete)

        key = f"{self.white_prefix}:{subject}:{credentials_id}"
        res = await self.redis_client.set(name=key, value=payload, ex=expiration)
        return bool(res)
