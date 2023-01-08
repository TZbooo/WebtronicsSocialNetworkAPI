import os

from fastapi_jwt_auth import AuthJWT
from sqlmodel import SQLModel


class Settings(SQLModel):
    authjwt_secret_key: str = os.getenv('JWT_SECRET')


@AuthJWT.load_config
def get_config():
    return Settings()