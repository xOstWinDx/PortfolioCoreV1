from dataclasses import dataclass

from src.domain.entities.user import RolesEnum


@dataclass(frozen=True)
class AuthorizationContext:
    user_id: int | None
    role: RolesEnum
