from sqlmodel import SQLModel


class PostSchema(SQLModel):
    content: str