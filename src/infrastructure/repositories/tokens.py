from typing import Any

from redis import Redis

from src.application.interfaces.repositories.tokens import AbstractTokensRepository
from src.domain.entities.tokens import TokenMeta


class RedisTokensRepository(AbstractTokensRepository):
    ban_prefix = "black"
    white_prefix = "white"

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def is_banned(self, subject: str = "*", token_id: str = "*") -> bool:  # type: ignore
        key = f"{self.ban_prefix}:{subject}:{token_id}"
        return bool(await self.redis_client.exists(key))

    async def get_active_one(  # type: ignore
        self, subject: str = "*", token_id: str = "*"
    ) -> tuple[str, TokenMeta] | None:
        key = f"{self.white_prefix}:{subject}:{token_id}"
        data = await self.redis_client.hgetall(key)
        if not data:
            return None
        return key, TokenMeta(**data)

    async def get_active_all(  # type: ignore
        self, subject: str = "*", token_id: str = "*"
    ) -> dict[str, TokenMeta] | None:
        keys: list[str] = await self.redis_client.keys(
            f"{self.white_prefix}:{subject}:{token_id}"
        )
        res = {}
        for key in keys:
            data = await self.redis_client.hgetall(key)
            if not data:
                continue
            res[key] = TokenMeta(**data)
        return res

    async def delete(self, key: str) -> bool:  # type: ignore
        res = await self.redis_client.delete(key)
        return bool(res)

    async def ban(  # type: ignore
        self, subject: str = "*", token_id: str = "*", reason: str = ""
    ) -> Any:
        src = f"{self.white_prefix}:{subject}:{token_id}"
        dst = f"{self.ban_prefix}:{subject}:{token_id}"
        return await self.redis_client.rename(src, dst)

    async def register(  # type: ignore
        self, subject: str, token_id: str, expiration: int, token_meta: TokenMeta
    ) -> bool:
        key = f"{self.white_prefix}:{subject}:*"
        keys = await self.redis_client.keys(key)

        if len(keys) >= 10:
            key_data = {
                key: await self.redis_client.hget("created_at", key) for key in keys
            }
            to_delete = min(key_data, key=lambda k: key_data[k])
            await self.redis_client.delete(to_delete)

        key = f"{self.white_prefix}:{subject}:{token_id}"
        res = await self.redis_client.hset(name=key, mapping=token_meta.to_dict())
        return bool(res)
