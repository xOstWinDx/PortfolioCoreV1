from sqlalchemy import Select, Delete, Update

from src.application.interfaces.repositories.users import AbstractUsersRepository
from src.domain.entities.user import User
from src.domain.filters.users import UserFilter
from src.infrastructure.models.user import UserModel, RoleModel
from src.infrastructure.repositories.alchemy_mixin import SQLAlchemyMixin


class SQLUsersRepository(AbstractUsersRepository, SQLAlchemyMixin):
    model = UserModel

    async def register(self, user: User) -> User:
        role = RoleModel(id=user.role.value, name=user.role.name)
        self.session.add(role)
        user_model = UserModel(
            email=user.email, password=user.password, username=user.username, role=role
        )
        self.session.add(user_model)
        await self.session.flush()
        return user_model.to_domain()

    async def get_user(self, user_filter: UserFilter) -> User | None:
        query = Select(self.model)
        if user_filter.email:
            query = query.where(self.model.email == user_filter.email)
        if user_filter.username:
            query = query.where(self.model.username == user_filter.username)
        if user_filter.id:
            query = query.where(self.model.id == user_filter.id)
        res = await self.session.execute(query)
        return res.scalars().one_or_none().to_domain()  # type: ignore

    async def delete(self, user_filter: UserFilter) -> bool:
        stmt = Delete(self.model)
        if user_filter.email:
            stmt = stmt.where(self.model.email == user_filter.email)
        if user_filter.username:
            stmt = stmt.where(self.model.username == user_filter.username)
        if user_filter.id:
            stmt = stmt.where(self.model.id == user_filter.id)
        res = await self.session.execute(stmt.returning(self.model))
        return bool(res.scalars().all())

    async def update(
        self, user_filter: UserFilter, update_data: dict[str, object]
    ) -> User:
        self._validate_update_data(update_data)
        stmt = Update(self.model).values(update_data).returning(self.model)
        if user_filter.email:
            stmt = stmt.where(self.model.email == user_filter.email)
        if user_filter.username:
            stmt = stmt.where(self.model.username == user_filter.username)
        if user_filter.id:
            stmt = stmt.where(self.model.id == user_filter.id)
        res = await self.session.execute(stmt)
        return res.scalars().one().to_domain()  # type: ignore
