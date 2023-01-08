from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.models.post import get_post_list, get_post, create_post, update_post
from app.db.models.user import get_user, like_post, remove_like, dislike_post, remove_dislike
from app.db.schemas.post import PostSchema
from app.db.session import get_session
from . import AuthJWT


router = APIRouter(
    prefix='/post'
)


@router.get('/all')
async def get_all_posts(offset: int | None, limit: int | None, db: Session = Depends(get_session)):
    posts = get_post_list(
        db=db,
        offset=offset,
        limit=limit
    )
    posts = [post.dict() for post in posts]
    return {'posts': posts}


@router.get('/{id}')
async def get_post_detail(id: int, db: Session = Depends(get_session)):
    post = get_post(
        db=db,
        id=id
    )
    return {
        'post': post.dict(),
        'likes': len(post.likers),
        'dislikes': len(post.dislikers)
    }


@router.post('/create')
async def create_new_post(post: PostSchema, Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)):
    Authorize.jwt_required()

    author_username = Authorize.get_jwt_subject()
    created_post = create_post(
        db=db,
        content=post.content,
        user=get_user(
            db=db,
            username=author_username
        )
    )
    return {'post': create_post.dict()}


@router.patch('/{id}/update')
async def update_post_by_id(id: int, post: PostSchema, Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)):
    Authorize.jwt_required()

    current_user = get_user(
        db=db,
        username=Authorize.get_jwt_subject()
    )
    post_for_update = get_post(
        db=db,
        id=id
    )

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

    new_post = update_post(
        db=db,
        content=post.content,
        id=id
    )
    return {'post': new_post.dict()}


@router.post('/{id}/like')
async def like_post_by_id(id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)):
    Authorize.jwt_required()

    liked_post = get_post(db, id)
    liker = get_user(db, Authorize.get_jwt_subject())

    if not liked_post:
        return HTTPException(
            status_code=404,
            detail='post for like does not exists'
        )
    if liker == liked_post.user:
        return HTTPException(
            status_code=304,
            detail='author can not like his posts'
        )
    if liker in liked_post.likers:
        likes = remove_like(
            db=db,
            post_id=id,
            username=liker.username
        )
        return {'likes': likes}
    
    likes = like_post(
        db=db,
        post_id=id,
        username=liker.username
    )
    return {'likes': likes}


@router.post('/{id}/dislike')
async def like_post_by_id(id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)):
    Authorize.jwt_required()

    disliked_post = get_post(db, id)
    disliker = get_user(db, Authorize.get_jwt_subject())

    if not disliked_post:
        raise HTTPException(
            status_code=404,
            detail='post for dislike does not exists'
        )
    if disliker == disliked_post.user:
        raise HTTPException(
            status_code=304,
            detail='author can not dislike his posts'
        )
    if disliker in disliked_post.dislikers:
        dislikes = remove_dislike(
            db=db,
            post_id=id,
            username=disliker.username
        )
        return {'dislikes': dislikes}

    dislikes = dislike_post(
        db=db,
        post_id=id,
        username=disliker.username
    )
    return {'dislikes': dislikes}