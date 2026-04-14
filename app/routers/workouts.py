from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import select
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep, AdminDep
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate
from typing import Optional
from fastapi import status
from . import api_router




@api_router.get("/workouts")
async def list_workouts(
    db: SessionDep,
    muscle_group: Optional[str] = None
):
    query = select(Workout)

    if muscle_group:
        query = query.where(Workout.muscle_group == muscle_group)

    return db.exec(query).all()



@api_router.get("/workouts/{workout_id}")
async def get_workout(
    workout_id: int,
    db: SessionDep
):
    workout = db.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return workout



@api_router.get("/workouts/{workout_id}/alternatives")
async def get_alternatives(
    workout_id: int,
    db: SessionDep
):
    workout = db.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return db.exec(
        select(Workout).where(
            Workout.muscle_group == workout.muscle_group,
            Workout.id != workout_id
        )
    ).all()



@api_router.post("/workouts", status_code=status.HTTP_201_CREATED)
async def create_workout(
    data: WorkoutCreate,
    db: SessionDep,
    user: AdminDep
):
    workout = Workout.model_validate(data)
    db.add(workout)
    db.commit()
    db.refresh(workout)

    return workout



@api_router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    db: SessionDep,
    user: AdminDep
):
    workout = db.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()