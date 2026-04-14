from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.models.workout import Routine
from . import router, templates




@router.get("/routines", response_class=HTMLResponse)
async def routines_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()

    return templates.TemplateResponse(
        request=request,
        name="routines.html",
        context={
            "request": request,
            "user": user,
            "routines": routines
        }
    )



@router.get("/routines/{routine_id}", response_class=HTMLResponse)
async def routine_detail_view(
    routine_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    routine = db.get(Routine, routine_id)

    if not routine or routine.user_id != user.id:
        return RedirectResponse(url="/routines")

    return templates.TemplateResponse(
        request=request,
        name="routine_detail.html",
        context={
            "request": request,
            "user": user,
            "routine_id": routine_id
        }
    )