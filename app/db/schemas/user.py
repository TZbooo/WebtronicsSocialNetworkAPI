from sqlmodel import SQLModel


class UserBase(SQLModel):
    username: str
    password: str


class UserAuth(UserBase):
    pass


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass