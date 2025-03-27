from src.application.interfaces.clients.cache import AbstractCacheClient
from src.application.interfaces.repositories.users import AbstractUsersRepository
from src.application.interfaces.services.auth import AbstractAuthService
from src.domain.entities.tokens import RefreshTokenPayload
from src.domain.filters.users import UserFilter

# TODO: вынести создание key для хранение токенов в отдельный класс, возможно в AuthService


class UpdateTokenUseCase:
    """Юзкейс, который обновляет access токены."""

    def __init__(
        self,
        auth_service: AbstractAuthService,
        cache_client: AbstractCacheClient,
        users_repo: AbstractUsersRepository,
    ) -> None:
        self.auth = auth_service
        self.cache_client = cache_client
        self.users_repo = users_repo

    async def __call__(
        self, ip: str, platform: str, browser: str, refresh_token: str
    ) -> str | None:
        payload = self.auth.decode_token(refresh_token)
        if not payload or not isinstance(payload, RefreshTokenPayload):
            return None
        user_id = payload.sub

        user = await self.users_repo.get_user(UserFilter(id=user_id))
        if user is None:
            return None

        async with self.cache_client:
            baned = await self.cache_client.keys(f"black:{payload.sub}:{payload.jti}")
            if baned:
                return None
            keys = await self.cache_client.keys(f"white:{payload.sub}:{payload.jti}")

            if not keys:
                return None
            meta = await self.cache_client.get(keys[0])

            if meta is None:
                return None
            if (
                meta["ip"] == ip
                and meta["platform"] == platform
                and meta["browser"] == browser
            ):
                return self.auth.create_access_token(user).token
            else:
                # Можно добавить уведомления, о том что токен взломан
                await self.cache_client.delete(keys[0])
                await self.cache_client.set(
                    key=f"black:{user.id}:{payload.jti}",
                    banned_by="incorrect ip or platform or browser",
                )
                return None
