from dataclasses import dataclass
from enum import StrEnum
from typing import NamedTuple


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class AccessTokenPayload:
    iss: str
    sub: str
    role: int
    exp: int
    type: TokenType


@dataclass(frozen=True)
class RefreshTokenPayload:
    iss: str
    sub: str
    exp: int
    iat: int
    jti: str
    type: TokenType


class JwtCredentials:
    def __init__(self, authorize: str, authenticate: str) -> None:
        self.access_token = authorize
        self.refresh_token = authenticate

    def get_raw_data(self) -> dict[str, str]:
        return {"access_token": self.access_token, "refresh_token": self.refresh_token}

    def get_authorize(self) -> str:
        return self.access_token

    def get_authenticate(self) -> str:
        return self.refresh_token


Refresh = NamedTuple("Refresh", [("token", str), ("payload", RefreshTokenPayload)])
Access = NamedTuple("Access", [("token", str), ("payload", AccessTokenPayload)])
