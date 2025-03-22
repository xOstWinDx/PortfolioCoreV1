from src.domain.entities.project import Project
from src.infrastructure.models.project import ProjectModel, TagModel, TechnologyModel


def to_model(
    project: Project, tags: list[TagModel], stack: list[TechnologyModel]
) -> ProjectModel:
    return ProjectModel(
        id=project.id,
        created_at=project.created_at,
        title=project.title,
        description=project.description,
        tags=tags,
        stack=stack,
    )
