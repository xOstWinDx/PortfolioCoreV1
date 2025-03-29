from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from src.domain.entities.user import User, RolesEnum
from src.infrastructure.abstract import InfraStructureEntity
from src.infrastructure.models.base import Base


class UserModel(Base, InfraStructureEntity[User]):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    username: Mapped[str]
    role: Mapped["RoleModel"] = ForeignKey("roles.id")

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            password=self.password,
            username=self.username,
            role=RolesEnum(self.role.id),
            created_at=self.created_at,
        )


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
