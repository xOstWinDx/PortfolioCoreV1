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


@dataclass
class AccessTokenPayload:
    iss: str
    sub: str
    scope: str
    exp: int
    type: TokenType


@dataclass
class RefreshTokenPayload:
    iss: str
    sub: str
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
class Token:
    token: str
    payload: RefreshTokenPayload | AccessTokenPayload
