from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.entities.project import Project
from src.infrastructure.abstract import InfraStructureEntity


class ProjectSchema(BaseModel, InfraStructureEntity[Project]):
    title: str = Field(max_length=128)
    description: str
    tags: list[str]
    stack: list[str]
    created_at: datetime

    def to_domain(self) -> Project:
        return Project(
            id=None,
            title=self.title,
            description=self.description,
            tags=self.tags,
            stack=self.stack,
            created_at=self.created_at,
        )


class ProjectResponse(ProjectSchema):
    id: int
