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
    safe_as_dict,
    TokenType,
    AccessToken,
    RefreshToken,
)

logger = logging.getLogger("auth_service")


class AuthService(AbstractAuthService):
    def check_password(self, username: str, password: str) -> bool:
        return username == CONFIG.ADMIN_USERNAME and password == CONFIG.ADMIN_PASSWORD

    def create_access_token(self, username: str) -> AccessToken:
        payload = AccessTokenPayload(
            iss="portfolio_backend",
            sub=username,
            scope="all",
            exp=int((datetime.now(UTC) + timedelta(minutes=30)).timestamp()),
            type=TokenType.ACCESS,
        )
        return AccessToken(token=self._create_token(payload), payload=payload)

    def create_refresh_token(self, username: str) -> RefreshToken:
        """
        Генерирует рефреш токен и возвращает сам токен + его айди
        :param username:
        :return: Кортеж токен + айди токена
        """
        jti = uuid.uuid4().hex
        payload = RefreshTokenPayload(
            iss="portfolio_backend",
            sub=username,
            exp=int((datetime.now(UTC) + timedelta(days=180)).timestamp()),
            iat=int(datetime.now(UTC).timestamp()),
            jti=jti,
            type=TokenType.REFRESH,
        )
        return RefreshToken(token=self._create_token(payload), payload=payload)

    def hash_password(self, password: str) -> bytes:
        hash: bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hash

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
            logger.warning(f"Wrong payload: {payload}")
        return None
