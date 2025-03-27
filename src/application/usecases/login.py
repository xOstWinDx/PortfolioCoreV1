import datetime
import uuid

from src.application.interfaces.clients.cache import AbstractCacheClient
from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.uow.users import AbstractUsersUnitOfWork
from src.domain.entities.user import User
from src.domain.filters.users import UserFilter


# TODO: вынести создание key для хранение токенов в отдельный класс, возможно в AuthService


class LoginUseCase:
    def __init__(
        self,
        auth: AbstractAuthService,
        cache: AbstractCacheClient,
        users_uow: AbstractUsersUnitOfWork,
    ) -> None:
        self.cache = cache
        self.auth = auth
        self.users_uow = users_uow

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
        async with self.users_uow as uow:
            user = await uow.users.get_user(UserFilter(email=email))

        # Защищаемся от timing attack =)
        user_password = user.password if user is not None else uuid.uuid4().hex.encode()
        if self.auth.check_password(user_password, password) and user is not None:
            async with self.cache:
                exist_refresh = await self._check_exists_tokens(
                    user, ip, platform, browser
                )
                access = self.auth.create_access_token(user)
                if exist_refresh is not None:
                    return access.token, exist_refresh
                else:
                    new_refresh = self.auth.create_refresh_token(user)
                    await self.cache.set(
                        key=f"white:{new_refresh.payload.sub}:{new_refresh.payload.jti}",
                        expiration=new_refresh.payload.exp,
                        token=new_refresh.token,
                        ip=ip,
                        platform=platform,
                        browser=browser,
                        created_at=int(datetime.datetime.now(datetime.UTC).timestamp()),
                    )
                    return access.token, new_refresh.token
        return None

    async def _check_exists_tokens(
        self, user: User, ip: str, platform: str, browser: str, max_tokens: int = 5
    ) -> str | None:
        """
        Проверяем существует ли у пользователя refresh токен
        :param user: Никнейм пользователя.
        :param ip: IP с которого совершается запрос.
        :param platform: Платформа например Windows или Mac.
        :param browser: Браузер, например "chrome", "firefox"
        :param max_tokens: Максимальное количество токенов для пользователя.
        :return: Refresh токен или None
        """
        pattern = f"white:{user.id}:*"
        keys = await self.cache.keys(pattern)
        key_token = []
        for key in keys:
            token_meta = await self.cache.get(key)
            if token_meta is None:
                continue
            # Если ключ для пользователя существует возвращаем его
            if (
                token_meta["ip"] == ip
                and token_meta["platform"] == platform
                and token_meta["browser"] == browser
                and token_meta.get("token")
            ):
                return token_meta["token"]  # type: ignore
            key_token.append((key, token_meta))

        # Ограничиваем пользователя по количеству токенов удаляя самые старые
        if len(keys) >= max_tokens:
            key_token.sort(key=lambda t: t[1]["created_at"])
            to_delete = key_token[max_tokens - 1 :]
            for key, _ in to_delete:
                await self.cache.delete(key)

        return None
