from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.services.posts import PostsService, HasNext
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.post import Post


class GetPostsUseCase(AbstractUseCase):
    def __init__(
        self, auth: AbstractAuthService, uow: AbstractUnitOfWork, posts: PostsService
    ):
        super().__init__(auth=auth, uow=uow)
        self.posts = posts

    async def __call__(
        self, last_id: str | None = None, limit: int = 20
    ) -> tuple[list[Post], HasNext] | None:
        async with self.posts:
            return await self.posts.get_posts(last_id=last_id, limit=limit)
