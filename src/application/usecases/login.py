import datetime
import uuid

from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.entities.tokens import TokenMeta
from src.domain.entities.user import User
from src.domain.filters.users import UserFilter


# TODO: райзить ошибки, а не возвращать None


class LoginUseCase:
    def __init__(
        self,
        auth: AbstractAuthService,
        uow: AbstractUnitOfWork,
    ) -> None:
        self.auth = auth
        self.uow = uow

    async def __call__(
        self, email: str, password: str, ip: str, platform: str, browser: str
    ) -> tuple[str, str] | None:
        """
        Логика авторизации
        :param email: уникальный логин пользователя, почта.
        :param password: Пароль
        :param ip: Адрес с которого совершается запрос.
        :param platform: Платформа с которой совершается запрос.
        :param browser: Браузер из которого совершается запрос
        :return: Кортеж из access и refresh токенов или None если не удалось аутентифицироваться
        """
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(email=email))

            # Защищаемся от timing attack =)
            user_password = (
                user.password if user is not None else uuid.uuid4().hex.encode()
            )
            if self.auth.check_password(user_password, password) and user is not None:
                exist_refresh = await self._check_exists_tokens(
                    user, ip, platform, browser
                )
                access = self.auth.create_access_token(user)
                if exist_refresh is not None:
                    return access.token, exist_refresh
                else:
                    new_refresh = self.auth.create_refresh_token(user)
                    await uow.tokens.register(
                        subject=str(new_refresh.payload.sub),
                        token_id=new_refresh.payload.jti,
                        expiration=new_refresh.payload.exp,
                        token_meta=TokenMeta(
                            token=new_refresh.token,
                            ip=ip,
                            platform=platform,
                            browser=browser,
                            created_at=int(
                                datetime.datetime.now(datetime.UTC).timestamp()
                            ),
                        ),
                    )
                    return access.token, new_refresh.token
            return None

    async def _check_exists_tokens(
        self, user: User, ip: str, platform: str, browser: str
    ) -> str | None:
        """
        Проверяем существует ли у пользователя refresh токен
        """
        tokens_meta = await self.uow.tokens.get_active_all(str(user.id))
        if tokens_meta is None:
            return None
        for key, token_meta in tokens_meta.items():
            if token_meta.check(ip, platform, browser):
                return token_meta.token
        return None
