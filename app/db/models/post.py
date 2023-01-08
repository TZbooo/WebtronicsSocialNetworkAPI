from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, Session

from .links import LikedPostsLink, DislikedPostsLink
from ..schemas.post import PostSchema


if TYPE_CHECKING:
    from .user import UserModel


class PostModel(PostSchema, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='usermodel.id')
    user: 'UserModel' = Relationship(back_populates='posts')
    likers: list['UserModel'] = Relationship(
        back_populates='liked_posts',
        link_model=LikedPostsLink
    )
    dislikers: list['UserModel'] = Relationship(
        back_populates='disliked_posts',
        link_model=DislikedPostsLink
    )


def get_post_list(db: Session, offset: int | None, limit: int | None) -> list[PostModel]:
    posts = db.query(PostModel)
    if offset:
        posts = posts.offset(offset)
    if limit:
        posts = posts.limit(limit)
    return posts


def get_post(db: Session, id: int) -> PostModel:
    return db.query(PostModel).filter_by(
        id=id
    ).one_or_none()


def create_post(db: Session, content: str, user: 'UserModel') -> PostModel:
    post = PostModel(content=content, user_id=user.id)
    db.add(post)
    db.commit()
    return post


def update_post(db: Session, content: str, id: int) -> PostModel:
    post = db.query(PostModel).filter_by(id=id).first()
    post.content = content
    db.add(post)
    db.commit()
    return post