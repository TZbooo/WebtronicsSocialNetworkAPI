from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.db.models.user import (
    User,
    get_user_by_username,
    authenticate_user,
    get_current_user
)
from app.db.schemas.user import UserAuth
from app.db.session import get_session
from app.utils import get_password_hash, create_access_token


router = APIRouter(
    prefix='/user'
)


@router.post('/signup')
def signup(data: UserAuth, db: Session = Depends(get_session)):
    if get_user_by_username(db, data.username) is not None:
        raise HTTPException(
            status_code=409,
            detail='User already exists'
        )
    user = User(
        username=data.username,
        password=get_password_hash(data.password)
    )
    db.add(user)
    db.commit()
    

@router.post('/login')
async def login_for_access_token(db: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(
        data={'sub': user.username}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me')
def get_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user