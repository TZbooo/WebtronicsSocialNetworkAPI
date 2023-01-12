from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.models.post import Post
from app.db.models.user import User, get_current_user
from app.db.schemas.post import PostCreate, PostUpdate
from app.db.session import get_session


router = APIRouter(
    prefix='/post'
)


@router.get('/all')
async def get_all_posts(
    offset: int | None = None,
    limit: int | None = None,
    db: Session = Depends(get_session)
) -> list[Post]:
    return db.query(Post).offset(offset).limit(limit).all()


@router.get('/{id}')
async def get_post_detail(id: int, db: Session = Depends(get_session)) -> Post:
    return db.get(Post, id)


@router.post('/create')
def create_new_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Post:
    post = Post(
        content=post.content,
        user=current_user
    )
    db.add(post)
    db.commit()
    return post


@router.patch('/{id}/update')
async def update_post_by_id(
    id: int,
    post: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Post:
    post_for_update = db.get(Post, id)
    if not post_for_update:
        raise HTTPException(
            status_code=404,
            detail='post does not exists'
        )
    if not post_for_update.user_id == current_user.id:
        return HTTPException(
            status_code=304,
            detail='only the author of the post can change it'
        )
    post_for_update.content = post.content
    db.add(post_for_update)
    db.commit()
    return post_for_update


@router.post('/{id}/like')
async def like_post_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    liked_post = db.get(Post, id)

    if not liked_post:
        return HTTPException(
            status_code=404,
            detail='post for like does not exists'
        )
    if current_user == liked_post.user:
        return HTTPException(
            status_code=304,
            detail='author can not like his posts'
        )
    if current_user in liked_post.likers:
        likes = current_user.remove_like(
            db=db,
            post_id=id
        )
        return {'likes': likes}
    
    likes = current_user.like_post(
        db=db,
        post_id=id
    )
    return {'likes': likes}


@router.post('/{id}/dislike')
async def like_post_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    disliked_post = db.get(Post, id)

    if not disliked_post:
        raise HTTPException(
            status_code=404,
            detail='post for dislike does not exists'
        )
    if current_user == disliked_post.user:
        raise HTTPException(
            status_code=304,
            detail='author can not dislike his posts'
        )
    if current_user in disliked_post.dislikers:
        dislikes = current_user.remove_dislike(
            db=db,
            post_id=id
        )
        return {'dislikes': dislikes}

    dislikes = current_user.dislike_post(
        db=db,
        post_id=id
    )
    return {'dislikes': dislikes}