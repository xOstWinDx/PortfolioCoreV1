from sqlalchemy import ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.project import Project
from src.infrastructure.abstract import InfraStructureEntity
from src.infrastructure.database import Str128
from src.infrastructure.models.base import Base


class ProjectModel(Base, InfraStructureEntity[Project]):
    __tablename__ = "projects"

    title: Mapped[Str128]
    description: Mapped[str]
    tags: Mapped[list] = mapped_column(ARRAY(String(15)))
    stack: Mapped[list] = mapped_column(ARRAY(String(15)))

    def to_domain(self) -> Project:
        return Project(
            id=self.id,
            created_at=self.created_at,
            title=self.title,
            description=self.description,
            tags=self.tags,
            stack=self.stack,
        )
