from dataclasses import dataclass, is_dataclass, asdict
from enum import StrEnum
from typing import TypeVar, Any

T = TypeVar("T")


def safe_as_dict(obj: T) -> dict[str, Any]:
    assert is_dataclass(obj), "Объект должен быть дата-классом"
    return asdict(obj)  # type: ignore


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class AccessTokenPayload:
    iss: str
    sub: int | None
    scope: str
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


@dataclass(frozen=True)
class TokenMeta:
    ip: str
    platform: str
    browser: str
    token: str
    created_at: int  # timestamp

    def check(self, ip: str, platform: str, browser: str) -> bool:
        return (
            self.ip == ip
            and self.platform == platform
            and self.browser == browser
            and isinstance(self.token, str)
        )
