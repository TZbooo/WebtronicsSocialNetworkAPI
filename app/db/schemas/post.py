from sqlmodel import SQLModel


class PostBase(SQLModel):
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass