from redis import Redis

from src.application.interfaces.repositories.tokens import AbstractTokensRepository
from src.domain.entities.tokens import TokenMeta


class RedisTokensRepository(AbstractTokensRepository):
    # TODO implement
    async def is_banned(self, subject: str = "*", token_id: str = "*") -> bool:  # type: ignore
        pass

    async def get_active_one(  # type: ignore
        self, subject: str = "*", token_id: str = "*"
    ) -> tuple[str, TokenMeta] | None:
        pass

    async def get_active_all(  # type: ignore
        self, subject: str = "*", token_id: str = "*"
    ) -> dict[str, TokenMeta] | None:
        pass

    async def delete(self, key: str) -> bool:  # type: ignore
        pass

    async def ban(  # type: ignore
        self, subject: str = "*", token_id: str = "*", reason: str = ""
    ) -> bool:
        pass

    async def register(  # type: ignore
        self, subject: str, token_id: str, expiration: int, token_meta: TokenMeta
    ) -> bool:
        pass

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
