from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.domain.entities.project import Project
from src.infrastructure.abstract import InfraStructureEntity
from src.infrastructure.database import Str128, Str16
from src.infrastructure.models.base import Base


class TagModel(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Str16] = mapped_column(unique=True)


class TechnologyModel(Base):
    __tablename__ = "technologies"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Str16] = mapped_column(unique=True)


class ProjectModel(Base, InfraStructureEntity[Project]):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[Str128] = mapped_column(unique=True)
    description: Mapped[str]
    tags: Mapped[list[TagModel]] = relationship(TagModel, secondary="projects_tags")
    stack: Mapped[list[TechnologyModel]] = relationship(
        TechnologyModel, secondary="projects_technologies"
    )

    def to_domain(self) -> Project:
        return Project(
            id=self.id,
            created_at=self.created_at,
            title=self.title,
            description=self.description,
            tags=[tag.name for tag in self.tags],
            stack=[tech.name for tech in self.stack],
        )


class ProjectToTagModel(Base):
    __tablename__ = "projects_tags"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class ProjectToTechnologyModel(Base):
    __tablename__ = "projects_technologies"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    technology_id: Mapped[int] = mapped_column(
        ForeignKey("technologies.id"), primary_key=True
    )
