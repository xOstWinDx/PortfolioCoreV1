from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class AccessTokenPayload:
    iss: str
    sub: int | None
    role: int
    exp: int
    type: TokenType


@dataclass(frozen=True)
class RefreshTokenPayload:
    iss: str
    sub: int | None
    exp: int
    iat: int
    jti: str
    type: TokenType


@dataclass(frozen=True)
class RefreshToken:
    token: str
    payload: RefreshTokenPayload


@dataclass(frozen=True)
class AccessToken:
    token: str
    payload: AccessTokenPayload


class JwtCredentials:
    def __init__(self, access_token: str, refresh_token: str) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_raw_data(self) -> dict[str, str]:
        return {"access_token": self.access_token, "refresh_token": self.refresh_token}

    def get_authorize(self) -> str:
        return self.access_token

    def get_authenticate(self) -> str:
        return self.refresh_token
