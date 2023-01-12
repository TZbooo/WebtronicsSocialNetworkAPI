from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.models.user import UserModel, get_user, create_user
from app.db.schemas.user import UserSchema
from app.db.session import get_session
from .auth import AuthJWT


router = APIRouter(
    prefix='/user'
)


@router.post('/signup')
def signup(user: UserSchema, Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)):
    create_user(
        db=db,
        username=user.username,
        password=user.password
    )
    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


@router.post('/login')
def login(user: UserSchema, Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)):
    if not get_user(
        db=db,
        username=user.username
    ):
        raise HTTPException(
            status_code=400,
            detail='Bad username or password'
        )

    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


@router.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {'access_token': new_access_token}


@router.get('/me')
def get_current_user(Authorize: AuthJWT = Depends(), db: Session = Depends(get_session)) -> UserModel:
    Authorize.jwt_required()

    current_user = get_user(
        db=db,
        username=Authorize.get_jwt_subject()
    )
    return current_user