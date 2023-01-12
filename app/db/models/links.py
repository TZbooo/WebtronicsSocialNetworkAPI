from sqlmodel import SQLModel, Field


class LikedPostsLink(SQLModel, table=True):
    liker_id: int | None = Field(
        default=None,
        foreign_key='users.id', 
        primary_key=True
    )
    liked_post_id: int | None = Field(
        default=None,
        foreign_key='posts.id',
        primary_key=True
    )


class DislikedPostsLink(SQLModel, table=True):
    disliker_id: int | None = Field(
        default=None,
        foreign_key='users.id', 
        primary_key=True
    )
    disliked_post_id: int | None = Field(
        default=None,
        foreign_key='posts.id',
        primary_key=True
    )