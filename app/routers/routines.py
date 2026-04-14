from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import select
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.models.workout import Routine, RoutineWorkout, Workout
from app.schemas.workout import RoutineCreate, RoutineUpdate, RoutineWorkoutCreate, RoutineWorkoutUpdate
from fastapi import status
from . import api_router


@api_router.get("/routines")
async def list_routines(
    user: AuthDep,
    db: SessionDep
):
    routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()

    result = []
    for r in routines:
        count = len(db.exec(select(RoutineWorkout).where(RoutineWorkout.routine_id == r.id)).all())
        result.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "user_id": r.user_id,
            "workout_count": count
        })

    return result



@api_router.get("/routines/{routine_id}")
async def get_routine(
    routine_id: int,
    user: AuthDep,
    db: SessionDep
):
    routine = db.get(Routine, routine_id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    if routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="That routine doesn't belong to you")

    rws = db.exec(select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)).all()

    workouts = [
        {
            "id": rw.id,
            "routine_id": rw.routine_id,
            "workout_id": rw.workout_id,
            "sets": rw.sets,
            "reps": rw.reps,
            "workout": db.get(Workout, rw.workout_id)
        }
        for rw in rws
    ]

    return {
        "id": routine.id,
        "name": routine.name,
        "description": routine.description,
        "user_id": routine.user_id,
        "workouts": workouts
    }



@api_router.post("/routines", status_code=status.HTTP_201_CREATED)
async def create_routine(
    data: RoutineCreate,
    user: AuthDep,
    db: SessionDep
):
    routine = Routine(name=data.name, description=data.description, user_id=user.id)
    db.add(routine)
    db.commit()
    db.refresh(routine)

    return routine



@api_router.put("/routines/{routine_id}")
async def update_routine(
    routine_id: int,
    data: RoutineUpdate,
    user: AuthDep,
    db: SessionDep
):
    routine = db.get(Routine, routine_id)

    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="That routine doesn't belong to you")

    if data.name is not None:
        routine.name = data.name

    if data.description is not None:
        routine.description = data.description

    db.add(routine)
    db.commit()
    db.refresh(routine)

    return routine



@api_router.delete("/routines/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routine(
    routine_id: int,
    user: AuthDep,
    db: SessionDep
):
    routine = db.get(Routine, routine_id)

    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="That routine doesn't belong to you")

    for rw in db.exec(select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)).all():
        db.delete(rw)

    db.delete(routine)
    db.commit()



@api_router.post("/routines/{routine_id}/workouts", status_code=status.HTTP_201_CREATED)
async def add_workout_to_routine(
    routine_id: int,
    data: RoutineWorkoutCreate,
    user: AuthDep,
    db: SessionDep
):
    routine = db.get(Routine, routine_id)

    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="That routine doesn't belong to you")

    rw = RoutineWorkout(routine_id=routine_id, workout_id=data.workout_id, sets=data.sets, reps=data.reps)
    db.add(rw)
    db.commit()
    db.refresh(rw)

    return rw



@api_router.put("/routines/{routine_id}/workouts/{rw_id}")
async def update_routine_workout(
    routine_id: int,
    rw_id: int,
    data: RoutineWorkoutUpdate,
    user: AuthDep,
    db: SessionDep
):
    routine = db.get(Routine, routine_id)

    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="That routine doesn't belong to you")

    rw = db.get(RoutineWorkout, rw_id)

    if not rw:
        raise HTTPException(status_code=404, detail="Entry not found")

    if data.workout_id is not None:
        rw.workout_id = data.workout_id

    if data.sets is not None:
        rw.sets = data.sets

    if data.reps is not None:
        rw.reps = data.reps

    db.add(rw)
    db.commit()
    db.refresh(rw)

    return rw



@api_router.delete("/routines/{routine_id}/workouts/{rw_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_workout_from_routine(
    routine_id: int,
    rw_id: int,
    user: AuthDep,
    db: SessionDep
):
    routine = db.get(Routine, routine_id)

    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="That routine doesn't belong to you")

    rw = db.get(RoutineWorkout, rw_id)

    if not rw:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(rw)
    db.commit()