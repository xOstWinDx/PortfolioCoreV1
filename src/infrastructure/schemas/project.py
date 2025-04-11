from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.domain.entities.project import Project
from src.infrastructure.abstract import InfraStructureEntity
from src.infrastructure.schemas.user import Author


class CreateProjectSchema(BaseModel, InfraStructureEntity[Project]):
    title: str = Field(max_length=128)
    description: str
    tags: list[str]
    stack: list[str]
    created_at: datetime
    model_config = ConfigDict()

    @field_validator("tags", mode="after")
    def validate_tags(cls, value: list[str]) -> list[str]:
        unique_tags = set()
        for tag in value:
            if len(tag) > 16:
                raise ValueError(f"Tag name too long: {tag}, max length is 16")
            # Проверка длины и уникальности тегов
            tag = tag.strip().lower()  # Удаляем лишние пробелы и стандартизируем
            if not tag:
                raise ValueError("Tag cannot be empty")
            if len(tag) > 16:
                raise ValueError(f"Tag name too long: {tag}, max length is 16")
            if tag in unique_tags:
                raise ValueError(f"Duplicate tag: {tag}")
            unique_tags.add(tag)

        # Возвращаем нормализованные теги
        return list(unique_tags)

    @field_validator("stack", mode="after")
    def validate_stack(cls, value: list[str]) -> list[str]:
        unique_techs = set()
        for tech in value:
            if len(tech) > 16:
                raise ValueError(f"Tech name too long: {tech}, max length is 16")
            # Проверка длины и уникальности Технологий
            tech = tech.strip().lower()  # Удаляем лишние пробелы и стандартизируем
            if not tech:
                raise ValueError("Tech cannot be empty")
            if len(tech) > 16:
                raise ValueError(f"Tech name too long: {tech}, max length is 16")
            if tech in unique_techs:
                raise ValueError(f"Duplicate tech: {tech}")
            unique_techs.add(tech)
        return list(unique_techs)

    @field_validator("title", mode="after")
    def validate_title(cls, value: str) -> str:
        return value.strip().capitalize()

    def to_domain(self) -> Project:
        return Project(
            id=None,  # type: ignore
            title=self.title,
            description=self.description,
            tags=self.tags,
            stack=self.stack,
            created_at=self.created_at,
            author=None,
        )


class ReadProjectSchema(CreateProjectSchema):
    id: int
    author: Author


class ProjectsResponse(BaseModel):
    projects: list[ReadProjectSchema]
    has_next: bool
