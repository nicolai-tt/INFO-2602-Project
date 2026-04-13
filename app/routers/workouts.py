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

@api_router.get('/workouts', response_model=list[Workout])
async def list_workouts(db:SessionDep, muscle_grp: Optional[str] = None):
    db_query = select(Workout)
    if muscle_grp:
        db_query = db_query.where(Workout.muscle_group == muscle_grp)
    
    results = db.exec(db_query).all()
    return results


@api_router.get('/workouts/{workout_id}', response_model=Workout)
async def get_workout(db:SessionDep, workout_id: int):
    workout = db.get(Workout, workout_id)

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    return workout

@api_router.get('/workouts/{workout_id}/alternative', response_model=list[Workout])
async def get_alternative_workout(db:SessionDep, workout_id: int):
    workout = db.get(Workout, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    alt_workout = db.exec(select(Workout).where(Workout.muscle_group == workout.muscle_group, Workout.id != workout_id)).all() 
    return alt_workout

@api_router.post('/workout', status_code=status.HTTP_201_CREATED)
async def create_workout(db:SessionDep, user: AdminDep, workout: WorkoutCreate):
    new_workout = Workout.model_validate(workout)

    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    return new_workout


@api_router.delete('/workout/{workout_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(db:SessionDep, user:AdminDep, workout_id: int):
    workout = db.get(Workout, workout_id)

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout does not exist",
        )
    
    try:
        db.delete(workout)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occured while trying to delete workout"
        )