from abc import ABC, abstractmethod
from typing import Literal

from src.domain.entities.post import Post, Comment
from src.domain.filters.posts import PostsFilter


class AbstractPostsRepository(ABC):
    @abstractmethod
    async def get_posts(
        self,
        post_filter: PostsFilter,
        last_id: str | None = None,
        limit: int = 20,
        sort: Literal["asc", "desc"] = "desc",
    ) -> list[Post]:
        raise NotImplementedError

    @abstractmethod
    async def create_post(self, post: Post) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def like_post(self, post_id: str, user_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def dislike_post(self, post_filter: PostsFilter, user_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_comments(
        self,
        post_filter: PostsFilter,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> list[Comment]:
        raise NotImplementedError

    @abstractmethod
    async def create_comment(self, comment: Comment, post_id: str) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def like_comment(self, comment_id: str, user_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def dislike_comment(self, comment_id: str, user_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def answer_comment(self, comment: Comment, comment_id: str) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def get_answers(
        self,
        comment_id: str,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> list[Comment]:
        raise NotImplementedError
