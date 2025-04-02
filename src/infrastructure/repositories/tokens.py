import logging

from redis import ResponseError
from redis.asyncio import Redis

from src.application.interfaces.repositories.auth import AbstractAuthRepository
from src.infrastructure.models.auth import AuthMetaData, Payload

logger = logging.getLogger(__name__)


class JWTRedisAuthRepository(AbstractAuthRepository):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def __aenter__(self) -> "JWTRedisAuthRepository":
        await self.redis_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        await self.redis_client.__aexit__(exc_type, exc_val, exc_tb)

    async def is_active(
        self, subject: str, credentials_id: str, device_id: str
    ) -> bool:
        key = self.make_key(
            subject=subject, credentials_id=credentials_id, device_id=device_id
        )
        return bool(await self.redis_client.exists(key))

    async def get_active_one(  # type: ignore
        self, subject: str, credentials_id: str, device_id: str
    ) -> AuthMetaData | None:
        key = self.make_key(
            subject=subject, credentials_id=credentials_id, device_id=device_id
        )
        return await self.redis_client.get(key)  # type: ignore

    async def get_active_all(  # type: ignore
        self, subject: str = "*", credentials_id: str = "*", device_id: str = "*"
    ) -> list[AuthMetaData]:
        keys: list[str] = await self.redis_client.keys(
            self.make_key(subject, credentials_id, device_id)
        )
        res = [
            AuthMetaData(key=k, payload=Payload(**await self.redis_client.hgetall(k)))
            for k in keys
        ]
        return res

    async def delete(self, subject_id: str, device_id: str) -> bool:
        keys: list[str] = await self.redis_client.keys(
            self.make_key(subject=subject_id, credentials_id="*", device_id=device_id)
        )
        if not keys:
            return False
        try:
            await self.redis_client.delete(*keys)
        except ResponseError as e:
            logger.warning(f"Redis delete failed: {keys}", exc_info=e)
            return False
        return True

    async def register(
        self,
        subject: str,
        credentials_id: str,
        expiration: int,
        credentials: str,
        device_id: str,
    ) -> bool:
        key = self.make_key(
            subject=subject, credentials_id=credentials_id, device_id=device_id
        )
        res = await self.redis_client.set(name=key, value=credentials, ex=expiration)
        return bool(res)

    @staticmethod
    def make_key(subject: str, credentials_id: str, device_id: str) -> str:
        return f"tokens:{subject}:{credentials_id}:{device_id}"
