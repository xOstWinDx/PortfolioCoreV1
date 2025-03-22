from typing import Mapping

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.base import Base


class SQLAlchemyMixin:
    model: type[Base]

    def __init__(self, session: AsyncSession):
        self.session = session

    def _validate_update_data(self, updated_data: Mapping[str, object]) -> None:
        valid_keys = set(self.model.__table__.columns.keys())  # {'id', 'name', 'tags'}

        # Проверяем, есть ли в updated_data недопустимые ключи
        invalid_keys = set(updated_data.keys()) - valid_keys
        if invalid_keys:
            raise ValueError(f"Invalid keys for ProjectModel: {invalid_keys}")
