from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel, model_validator, field_validator

from src.domain.entities.post import Post, Comment


class Author(BaseModel):
    id: int
    name: str
    email: str
    photo_url: str


class CreateCommentSchema(BaseModel):
    text: str

    def to_domain(self, post_id: str) -> Comment:
        return Comment(
            id=None,
            text=self.text,
            author=None,
            parent_id=None,
            post_id=post_id,
            dislikes=set(),
            likes=set(),
            answers_count=0,
            created_at=datetime.now(UTC),
        )


class CreateAnswerSchema(CreateCommentSchema):
    pass


class ReadCommentSchema(CreateCommentSchema):
    id: str
    author: Author
    post_id: str
    dislikes: int
    likes: int
    answers_count: int
    # parent_id: str | None = None
    created_at: datetime

    @field_validator("dislikes", mode="before")
    def validate_dislikes(cls, value: set[int]) -> int:
        return len(value)

    @field_validator("likes", mode="before")
    def validate_likes(cls, value: set[int]) -> int:
        return len(value)


class ReadAnswerSchema(ReadCommentSchema):
    parent_id: str


class CommentsResponseSchema(BaseModel):
    comments: list[ReadCommentSchema]
    last_id: str | None
    has_next: bool

    @model_validator(mode="before")
    def set_last_id(cls, values: dict[str, Any]) -> dict[str, Any]:
        last_id = values.get("last_id")
        if last_id:
            values["last_id"] = str(last_id)
            return values
        if len(values["comments"]) == 0:
            values["last_id"] = None
            return values
        values["last_id"] = values["comments"][-1].id
        return values


class AnswersResponseSchema(BaseModel):
    answers: list[ReadAnswerSchema]
    last_id: str | None
    has_next: bool

    @model_validator(mode="before")
    def set_last_id(cls, values: dict[str, Any]) -> dict[str, Any]:
        last_id = values.get("last_id")
        if last_id:
            values["last_id"] = str(last_id)
            return values
        if len(values["answers"]) == 0:
            values["last_id"] = None
            return values
        values["last_id"] = values["answers"][-1].id
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
            created_at=datetime.now(UTC),
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
    recent_comments: CommentsResponseSchema

    @field_validator("dislikes", mode="before")
    def validate_dislikes(cls, value: set[int]) -> int:
        return len(value)

    @field_validator("likes", mode="before")
    def validate_likes(cls, value: set[int]) -> int:
        return len(value)

    @model_validator(mode="before")
    def validate_recent_comments(cls, data: Post) -> Post:
        """Эта функция поправляет аттрибут "последних комментариев" что бы он включал в себя поле has_next"""
        recent_comments = {
            "comments": data.recent_comments,
            "has_next": data.comments_count > len(data.recent_comments),
        }
        data.recent_comments = recent_comments  # type: ignore[assignment] # noqa
        return data


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
