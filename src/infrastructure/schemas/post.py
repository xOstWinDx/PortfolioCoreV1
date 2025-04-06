from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator, field_validator

from src.domain.entities.post import Post


class Author(BaseModel):
    id: int
    name: str
    email: str
    photo_url: str


class ReadCommentSchema(BaseModel):
    id: str
    text: str
    author: Author
    parent_id: str
    post_id: str
    dislikes: set[int]  # id's of users who disliked
    likes: set[int]  # id's of users who liked
    answers_count: int
    created_at: datetime


class CommentsResponseSchema(BaseModel):
    comments: list[ReadCommentSchema]
    last_id: str

    @model_validator(mode="before")
    def set_last_id(cls, values: dict[str, Any]) -> dict[str, Any]:
        last_id = values.get("last_id")
        if last_id:
            values["last_id"] = str(last_id)
            return values
        values["last_id"] = values["comments"][-1].id
        return values


class CreatePostSchema(BaseModel):
    title: str
    content: str

    def to_domain(self) -> Post:
        return Post(
            id=None,
            title=self.title,
            content=self.content,
            author=None,
            dislikes=set(),
            likes=set(),
            created_at=datetime.now(),
            comments_count=0,
            recent_comments=[],
        )


class ReadPostSchema(CreatePostSchema):
    id: str
    title: str
    content: str
    author: Author
    dislikes: int  # set[int] id's of users who disliked
    likes: int  # set[int] id's of users who liked
    created_at: datetime
    comments_count: int
    recent_comments: list[CommentsResponseSchema]

    @field_validator("dislikes", mode="before")
    def validate_dislikes(cls, value: set[int]) -> int:
        return len(value)

    @field_validator("likes", mode="before")
    def validate_likes(cls, value: set[int]) -> int:
        return len(value)


class PostsResponseSchema(BaseModel):
    posts: list[ReadPostSchema]
    last_id: str | None
    has_next: bool

    @model_validator(mode="before")
    def set_last_id(cls, values: dict[str, Any]) -> dict[str, Any]:
        last_id = values.get("last_id")
        if last_id:
            values["last_id"] = str(last_id)
            return values
        if len(values["posts"]) == 0:
            values["last_id"] = None
            return values
        values["last_id"] = values["posts"][-1].id
        return values
