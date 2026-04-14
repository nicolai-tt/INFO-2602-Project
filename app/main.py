import uvicorn
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import templates, static_files, router, api_router
from app.config import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import create_db_and_tables, get_cli_session
    from app.models.user import User
    from app.models.workout import Workout
    from app.utilities.security import encrypt_password
    from app.cli import sample_workouts, create_user_if_missing
    from sqlmodel import select

    create_db_and_tables()

    with get_cli_session() as db:
        create_user_if_missing(db, "bob",   "bob@mail.com",   "bobpass",   "regular_user")
        create_user_if_missing(db, "admin", "admin@mail.com", "adminpass", "admin")

        current_workouts = db.exec(select(Workout)).all()
        if not current_workouts:
            for data in sample_workouts:
                db.add(Workout(
                    name=data["name"],
                    description=data["description"],
                    muscle_group=data["muscle_group"],
                    difficulty=data["difficulty"]
                ))
        db.commit()

    yield



app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
],
    lifespan=lifespan
)   

app.include_router(router)
app.include_router(api_router)
app.mount("/static", static_files, name="static")

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request, 
        name="401.html",
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=get_settings().app_host, port=get_settings().app_port, reload=get_settings().env.lower()!="production")