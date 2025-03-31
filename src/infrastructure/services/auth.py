import logging
import uuid
from datetime import datetime, UTC, timedelta
from typing import Any

import bcrypt
import jwt

from src.application.interfaces.credentials import Credentials
from src.application.interfaces.services.auth import AbstractAuthService
from src.config import CONFIG
from src.domain.entities.user import User, RolesEnum
from src.domain.exceptions.auth import TokenError, AuthError
from src.domain.utils import safe_as_dict
from src.domain.value_objects.auth import AuthorizationContext
from src.infrastructure.credentials import (
    JwtCredentials,
    RefreshTokenPayload,
    TokenType,
    AccessTokenPayload,
)

logger = logging.getLogger("auth_service")


class JwtAuthService(AbstractAuthService):
    async def authenticate(
        self, email: str, password: str, user: User | None
    ) -> Credentials:
        # TODO: изменить работу с токенами, возможно не стоит брать существующий, возможно стоит хранить их по связи с IP
        user_password = user.password if user is not None else uuid.uuid4().bytes
        if self.check_password(user_password, password) and user is not None:
            exist_refresh = await self._check_exists_tokens(user)
            access = self.create_access_token(user)

            if exist_refresh is not None:
                return JwtCredentials(authorize=access[0], authenticate=exist_refresh)
            else:
                new_refresh = self.create_refresh_token(user)
                await self.auth_repo.register(
                    subject=str(new_refresh[1].sub),
                    credentials_id=new_refresh[1].jti,
                    expiration=new_refresh[1].exp,
                    payload=new_refresh[0],
                )

                return JwtCredentials(authorize=access[0], authenticate=new_refresh[0])
        raise AuthError()

    async def authorize(self, credentials: Credentials | None) -> AuthorizationContext:
        if credentials is None:
            return AuthorizationContext(user_id=None, role=RolesEnum.GUEST)
        payload = self.decode_token(credentials.get_authorize())
        if not payload or payload.type != TokenType.ACCESS:
            raise TokenError()
        if not isinstance(payload, AccessTokenPayload):
            raise TokenError("Invalid token type")
        return AuthorizationContext(
            user_id=int(payload.sub), role=RolesEnum(payload.role)
        )

    async def renew_credentials(
        self, credentials: Credentials, user: User
    ) -> Credentials:
        payload = self.decode_token(credentials.get_authenticate())
        if not payload or not isinstance(payload, RefreshTokenPayload):
            raise TokenError()
        if await self.auth_repo.is_banned(str(payload.sub), payload.jti):
            raise TokenError("Token is banned")

        token = await self.auth_repo.get_active_one(str(payload.sub), payload.jti)
        if token is None:
            raise TokenError("Unknown token")
        if payload.sub is None:
            raise TokenError("Unknown user")

        return JwtCredentials(
            authorize=self.create_access_token(user=user)[0],
            authenticate=credentials.get_authenticate(),
        )

    async def _check_exists_tokens(self, user: User) -> str | None:
        tokens = await self.auth_repo.get_active_all(subject=str(user.id))
        if not tokens:
            return None
        return tokens[0]

    @staticmethod
    def check_password(user_password: bytes, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), user_password)  # type: ignore

    def create_access_token(self, user: User) -> tuple[str, AccessTokenPayload]:
        payload = AccessTokenPayload(
            iss="portfolio_backend",
            sub=str(user.id),
            role=user.role.value,
            exp=int((datetime.now(UTC) + timedelta(minutes=30)).timestamp()),
            type=TokenType.ACCESS,
        )
        return self._create_token(payload), payload

    def create_refresh_token(self, user: User) -> tuple[str, RefreshTokenPayload]:
        jti = uuid.uuid4().hex
        payload = RefreshTokenPayload(
            iss="portfolio_backend",
            sub=str(user.id),
            exp=int((datetime.now(UTC) + timedelta(days=180)).timestamp()),
            iat=int(datetime.now(UTC).timestamp()),
            jti=jti,
            type=TokenType.REFRESH,
        )
        return self._create_token(payload), payload

    @staticmethod
    def hash_password(password: str) -> bytes:
        hash_pass: bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hash_pass

    @staticmethod
    def _create_token(payload: RefreshTokenPayload | AccessTokenPayload) -> str:
        token: str = jwt.encode(
            payload=safe_as_dict(payload),
            key=CONFIG.JWT_PRIVATE_KEY.read_text(encoding="utf-8"),
            algorithm="RS256",
        )
        return token

    @staticmethod
    def decode_token(token: str) -> RefreshTokenPayload | AccessTokenPayload | None:
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                key=CONFIG.JWT_PUBLIC_KEY.read_text(encoding="utf-8"),
                algorithms=["RS256"],
            )
            match payload["type"]:
                case TokenType.ACCESS:
                    return AccessTokenPayload(**payload)
                case TokenType.REFRESH:
                    return RefreshTokenPayload(**payload)
                case _:
                    return None
        except jwt.PyJWTError as e:
            logger.warning(f"Failed to decode token: {e}")
            return None
        except TypeError:
            logger.warning(f"Wrong payload: {payload}")  # noqa
        return None

    def validate_refresh_token(self, token: str) -> RefreshTokenPayload:
        payload = self.decode_token(token)
        if not payload or payload.type != TokenType.REFRESH:
            raise TokenError()
        if not isinstance(payload, RefreshTokenPayload):
            raise TokenError("Invalid token type")
        return payload

    def validate_access_token(self, token: str) -> AccessTokenPayload:
        payload = self.decode_token(token)
        if not payload or payload.type != TokenType.ACCESS:
            raise TokenError()
        if not isinstance(payload, AccessTokenPayload):
            raise TokenError("Invalid token type")
        return payload

    def get_subject_id(self, credentials: Credentials) -> int:
        try:
            return int(self.decode_token(credentials.get_authenticate()).sub)  # type: ignore
        except (TokenError, AttributeError) as e:
            logger.warning(
                f"Invalid token: {credentials.get_authenticate()}", exc_info=e
            )
            raise TokenError(f"Invalid token: {credentials.get_authenticate()}")
