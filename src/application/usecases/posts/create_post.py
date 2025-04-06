from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.services.posts import PostsService
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.post import Post


class CreatePostUseCase(AbstractUseCase):
    def __init__(
        self, auth: AbstractAuthService, uow: AbstractUnitOfWork, posts: PostsService
    ):
        super().__init__(auth=auth, uow=uow)
        self.posts = posts

    async def __call__(self, post: Post) -> Post:
        return await self.posts.create_post(post=post)
