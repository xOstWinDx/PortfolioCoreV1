from src.application.interfaces.clients.cache import AbstractCacheClient
from src.application.interfaces.services.auth import AbstractAuthService


class UpdateTokenUseCase:
    def __init__(
        self, auth_service: AbstractAuthService, cache_client: AbstractCacheClient
    ) -> None:
        self.auth = auth_service
        self.cache_client = cache_client

    async def __call__(
        self, ip: str, platform: str, browser: str, refresh_token: str
    ) -> str | None:
        async with self.cache_client:
            baned = await self.cache_client.keys(f"black:*:{refresh_token}")
            if baned:
                # Можно добавить уведомления, о том что токен взломан
                return None
            keys = await self.cache_client.keys(f"white:*:{refresh_token}")

            if not keys:
                return None
            meta = await self.cache_client.get(keys[0])

            if meta is None:
                return None
            payload = self.auth.decode_token(refresh_token)
            if not payload:
                return None
            username = payload["sub"]
            if (
                username == meta["username"]
                and meta["ip"] == ip
                and meta["platform"] == platform
                and meta["browser"] == browser
            ):
                return self.auth.create_access_token(username)
            else:
                await self.cache_client.delete(keys[0])
                await self.cache_client.set(
                    key=f"black:{username}:{refresh_token}",
                    banned_by="incorrect ip or platform or browser",
                )
                return None
