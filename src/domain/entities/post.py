from dataclasses import dataclass
from datetime import datetime


@dataclass
class Comment:
    id: str
    text: str
    author_id: int
    author_name: str
    author_email: str
    author_photo_url: str
    parent_id: str
    post_id: str
    dislikes: set[int]  # id's of users who disliked
    likes: set[int]  # id's of users who liked
    answers_count: int
    created_at: datetime


@dataclass
class Post:
    id: str
    title: str
    content: str
    author_id: int
    author_name: str
    author_email: str
    author_photo_url: str
    dislikes: set[int]  # ids of users that disliked this post
    likes: set[int]  # ids of users that liked this post
    created_at: datetime | None
    comments_count: int
    recent_comments: list[Comment]
