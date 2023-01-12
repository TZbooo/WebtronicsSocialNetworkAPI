from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from sqlmodel import Field, Relationship, Session
from jose import JWTError, jwt

from app.db.session import get_session
from app.utils import oauth2_scheme, verify_password
from app.settings import (
    SECRET_KEY,
    ALGORITHM
)
from .links import LikedPostsLink, DislikedPostsLink
from ..schemas.user import UserBase



if TYPE_CHECKING:
    from .post import Post


class User(UserBase, table=True):
    __tablename__ = 'users'

    id: int | None = Field(default=None, primary_key=True)
    posts: list['Post'] = Relationship(back_populates='user')
    liked_posts: list['Post'] = Relationship(
        back_populates='likers',
        link_model=LikedPostsLink
    )
    disliked_posts: list['Post'] = Relationship(
        back_populates='dislikers',
        link_model=DislikedPostsLink
    )

    def like_post(self, db: Session, post_id: int) -> int:
        post = db.get(Post, post_id)
        if post in self.disliked_posts:
            self.remove_dislike(
                db=db,
                post_id=post_id,
            )
        self.liked_posts.append(post)
        db.add(self)
        db.commit()
        return len(self.liked_posts)

    def dislike_post(self, db: Session, post_id: int) -> int:
        post = db.get(Post, post_id)
        if post in self.liked_posts:
            self.remove_like(
                db=db,
                post_id=post_id,
            )
        self.disliked_posts.append(post)
        db.add(self)
        db.commit()
        return len(self.disliked_posts)

    def remove_like(self, db: Session, post_id: int) -> int:
        post = db.get(Post, post_id)
        self.liked_posts.remove(post)
        db.add(self)
        db.commit()
        return len(self.liked_posts)

    def remove_dislike(self, db: Session, post_id: int) -> int:
        post = db.get(Post, post_id)
        self.disliked_posts.remove(post)
        db.add(self)
        db.commit()
        return len(self.disliked_posts)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter_by(
        username=username
    ).one_or_none()


async def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(db, username: str, password: str) -> User:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.password):
        raise HTTPException(
            status_code=400,
            detail='Bad username or password'
        )
    return user


async def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user