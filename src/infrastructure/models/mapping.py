from src.domain.entities.project import Project
from src.infrastructure.models.project import ProjectModel


def to_model(project: Project) -> ProjectModel:
    return ProjectModel(
        id=project.id,
        created_at=project.created_at,
        title=project.title,
        description=project.description,
    )
