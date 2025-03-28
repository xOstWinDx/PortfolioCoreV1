import logging
import uuid
from datetime import datetime, UTC, timedelta
from typing import Any

import bcrypt
import jwt

from src.application.interfaces.services.auth import AbstractAuthService
from src.config import CONFIG
from src.domain.entities.tokens import (
    AccessTokenPayload,
    RefreshTokenPayload,
    TokenType,
    AccessToken,
    RefreshToken,
)
from src.domain.utils import safe_as_dict
from src.domain.entities.user import User

logger = logging.getLogger("auth_service")


class AuthService(AbstractAuthService):
    def check_password(self, user_password: bytes, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), user_password)  # type: ignore

    def create_access_token(self, user: User) -> AccessToken:
        payload = AccessTokenPayload(
            iss="portfolio_backend",
            sub=user.id,
            scope="all",
            exp=int((datetime.now(UTC) + timedelta(minutes=30)).timestamp()),
            type=TokenType.ACCESS,
        )
        return AccessToken(token=self._create_token(payload), payload=payload)

    def create_refresh_token(self, user: User) -> RefreshToken:
        """
        Генерирует рефреш токен и возвращает сам токен + его айди
        :param user:
        :return: Кортеж токен + айди токена
        """
        jti = uuid.uuid4().hex
        payload = RefreshTokenPayload(
            iss="portfolio_backend",
            sub=user.id,
            exp=int((datetime.now(UTC) + timedelta(days=180)).timestamp()),
            iat=int(datetime.now(UTC).timestamp()),
            jti=jti,
            type=TokenType.REFRESH,
        )
        return RefreshToken(token=self._create_token(payload), payload=payload)

    def hash_password(self, password: str) -> bytes:
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

    def decode_token(
        self, token: str
    ) -> RefreshTokenPayload | AccessTokenPayload | None:
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
        except jwt.PyJWTError:
            return None
        except TypeError:
            logger.warning(f"Wrong payload: {payload}")  # noqa
        return None
