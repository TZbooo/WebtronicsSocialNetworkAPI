from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, Session

from app.utils import get_hashed_password
from .links import LikedPostsLink, DislikedPostsLink
from .post import get_post
from ..schemas.user import UserSchema


if TYPE_CHECKING:
    from .post import PostModel


class UserModel(UserSchema, table=True):
    id: int | None = Field(default=None, primary_key=True)
    posts: list['PostModel'] = Relationship(back_populates='user')
    liked_posts: list['PostModel'] = Relationship(
        back_populates='likers',
        link_model=LikedPostsLink
    )
    disliked_posts: list['PostModel'] = Relationship(
        back_populates='dislikers',
        link_model=DislikedPostsLink
    )


def like_post(db: Session, post_id: int, username: str) -> int:
    liker = get_user(db, username)
    post = get_post(db, post_id)
    if post in liker.disliked_posts:
        remove_dislike(
            db=db,
            post_id=post_id,
            username=username
        )
    liker.liked_posts.append(post)
    db.add(liker)
    db.commit()
    return len(liker.liked_posts)


def remove_like(db: Session, post_id: int, username: str) -> int:
    user = get_user(db, username)
    post = get_post(db, post_id)
    user.liked_posts.remove(post)
    db.add(user)
    db.commit()
    return len(user.liked_posts)


def dislike_post(db: Session, post_id: int, username: str) -> int:
    disliker = get_user(db, username)
    post = get_post(db, post_id)
    if post in disliker.liked_posts:
        remove_like(
            db=db,
            post_id=post_id,
            username=username
        )
    disliker.disliked_posts.append(post)
    db.add(disliker)
    db.commit()
    return len(disliker.disliked_posts)


def remove_dislike(db: Session, post_id: int, username: str) -> int:
    user = get_user(db, username)
    post = get_post(db, post_id)
    user.disliked_posts.remove(post)
    db.add(user)
    db.commit()
    return len(user.disliked_posts)


def get_user(db: Session, username: str) -> UserModel:
    return db.query(UserModel).filter_by(
        username=username
    ).one_or_none()


def create_user(db: Session, username: str, password: str) -> UserModel:
    user = UserModel(
        username=username,
        password=get_hashed_password(password)
    )
    db.add(user)
    db.commit()
    return user
