from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.entities.tokens import RefreshTokenPayload
from src.domain.filters.users import UserFilter


# TODO: заменить ретёрны на райзы ошибки.


class UpdateTokenUseCase:
    """Юзкейс, который обновляет access токены."""

    def __init__(
        self,
        auth_service: AbstractAuthService,
        uow: AbstractUnitOfWork,
    ) -> None:
        self.auth = auth_service
        self.uow = uow

    async def __call__(
        self, ip: str, platform: str, browser: str, refresh_token: str
    ) -> str | None:
        payload = self.auth.decode_token(refresh_token)
        if not payload or not isinstance(payload, RefreshTokenPayload):
            return None
        user_id = payload.sub
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(id=user_id))
            if user is None:
                return None

            if await uow.tokens.is_banned(str(payload.sub), payload.jti):
                return None

            key_meta = await uow.tokens.get_active_one(str(payload.sub), payload.jti)
            if key_meta is None:
                return None

            key, meta = key_meta
            if meta is None:
                return None

            if meta.check(ip, platform, browser):
                return self.auth.create_access_token(user).token
            else:
                # Можно добавить уведомления, о том что токен взломан
                await uow.tokens.ban(
                    subject=str(user.id),
                    token_id=payload.jti,
                    reason="incorrect ip or platform or browser",
                )
                return None
