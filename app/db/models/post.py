from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .links import LikedPostsLink, DislikedPostsLink
from ..schemas.post import PostBase


if TYPE_CHECKING:
    from .user import User


class Post(PostBase, table=True):
    __tablename__ = 'posts'

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.id')
    user: 'User' = Relationship(back_populates='posts')
    likers: list['User'] = Relationship(
        back_populates='liked_posts',
        link_model=LikedPostsLink
    )
    dislikers: list['User'] = Relationship(
        back_populates='disliked_posts',
        link_model=DislikedPostsLink
    )