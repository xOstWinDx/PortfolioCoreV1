from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from src.application.authorize import UseCaseGuard

from src.application.interfaces.credentials import Credentials  # noqa: F401
from src.application.usecases.add_project import CreateProjectUseCase
from src.container import container
from src.domain.exceptions.base import ConflictException


from src.domain.value_objects.auth import AuthorizationContext  # noqa: F401
from src.infrastructure.schemas.project import ProjectResponse, ProjectSchema
from src.presentation.http.dependencies import credentials_schema

router = APIRouter(prefix="/projects", tags=["projects"])


# TODO [31.03.2025 | High]
# Assigned to: stark
# Description: Обновлять токены если декоратор создал новые
# Steps:
#   - Доработать декоратор, что бы возвращал новые креды с результатом функции
#   - Создать базовую схему ответов от апи (возможно нет)
#   - создать мидлвейр, который ставит куки если находит в респонсе токены
# ────────────────


@router.post("/", status_code=201, response_model=None)
@inject
async def create_project(
    project: ProjectSchema,
    credentials: Annotated[credentials_schema, Depends()],  # type: ignore
    guard: UseCaseGuard[CreateProjectUseCase] = Depends(
        Provide["create_project_use_case"]
    ),
) -> ProjectResponse:
    try:
        guard.configure(credentials=credentials, creds_holder=credentials)
        async with guard as (use_case, context, creds):  # type: (CreateProjectUseCase, AuthorizationContext, Credentials)
            res = await use_case(
                project=project.to_domain(),
                credentials=credentials,
            )
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return ProjectResponse.model_validate(res, from_attributes=True)


container.wire(modules=[__name__])  # должен быть внизу
