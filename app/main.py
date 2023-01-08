from fastapi import FastAPI

from .v1 import user, post
from .db.session import init_db, wait_for_db


app = FastAPI()
app.include_router(user.router)
app.include_router(post.router)


@app.on_event('startup')
def on_startup():
    wait_for_db()
    init_db()