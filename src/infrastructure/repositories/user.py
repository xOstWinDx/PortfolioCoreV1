import uuid
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import bcrypt
import jwt

from src.application.interfaces.services.auth import AbstractAuthService
from src.config import CONFIG


class AuthService(AbstractAuthService):
    def check_password(self, username: str, password: str) -> bool:
        return username == CONFIG.ADMIN_USERNAME and password == CONFIG.ADMIN_PASSWORD

    def create_access_token(self, username: str) -> str:
        payload = {
            "iss": "portfolio_backend",
            "sub": username,
            "scope": "all",
            "exp": datetime.now(ZoneInfo("UTC")) + timedelta(minutes=30),
        }
        return self._create_token(payload)

    def create_refresh_token(self, username: str) -> str:
        payload = {
            "iss": "portfolio_backend",
            "sub": username,
            "exp": datetime.now(ZoneInfo("UTC")) + timedelta(days=180),
            "iat": datetime.now(ZoneInfo("UTC")),
            "jti": uuid.uuid4().hex,
        }
        return self._create_token(payload)

    def hash_password(self, password: str) -> bytes:
        hash: bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hash

    @staticmethod
    def _create_token(payload: dict[str, Any]) -> str:
        token: str = jwt.encode(
            payload=payload,
            key=CONFIG.JWT_PRIVATE_KEY.read_text(encoding="utf-8"),
            algorithm="RS256",
        )
        return token

    def decode_token(self, token: str) -> bool | dict[str, Any]:
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                key=CONFIG.JWT_PUBLIC_KEY.read_text(encoding="utf-8"),
                algorithms=["RS256"],
            )
            return payload
        except jwt.PyJWTError:
            return False
