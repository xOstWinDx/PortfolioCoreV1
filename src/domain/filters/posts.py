from dataclasses import dataclass


@dataclass
class PostsFilter:
    post_id: str
    author_id: int
