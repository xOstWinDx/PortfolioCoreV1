from abc import ABC, abstractmethod
from typing import Literal

from src.domain.entities.post import Post, Comment


class AbstractPostsRepository(ABC):
    @abstractmethod
    async def get_posts(
        self,
        last_id: str | None = None,
        limit: int = 20,
        sort: Literal["asc", "desc"] = "desc",
    ) -> list[Post]:
        raise NotImplementedError

    @abstractmethod
    async def create_post(self, post: Post) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def like_post(self, post_id: str, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def dislike_post(self, post_id: str, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_comments(
        self,
        post_id: str,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> list[Comment]:
        raise NotImplementedError

    @abstractmethod
    async def create_comment(self, comment: Comment) -> Comment:
        raise NotImplementedError

    @abstractmethod
    async def like_comment(self, comment_id: str, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def dislike_comment(self, comment_id: str, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create_answer(self, answer: Comment, comment_id: str) -> Comment:
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
