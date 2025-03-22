from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import config
from src.infrastructure.uow.project import ProjectsUnitOfWork
from src.application.usecases.add_project import AddNewProjectUseCase


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_async_engine, url=config.DEV_DATABASE_URL)

    session_factory = providers.Factory(
        async_sessionmaker, bind=engine, expire_on_commit=False
    )

    projects_uow = providers.Factory(
        ProjectsUnitOfWork, session_factory=session_factory
    )

    create_project_use_case = providers.Factory(AddNewProjectUseCase, uow=projects_uow)
