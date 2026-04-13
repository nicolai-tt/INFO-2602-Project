from sqlmodel import SQLModel
from typing import Optional


class WorkoutCreate(SQLModel):
    name: str
    description: str = ""
    muscle_group: str
    difficulty: str = "beginner"


class WorkoutResponse(SQLModel):
    id: int
    name: str
    description: str
    muscle_group: str
    difficulty: str


class RoutineCreate(SQLModel):
    name: str
    description: str = ""


class RoutineUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoutineResponse(SQLModel):
    id: int
    name: str
    description: str
    user_id: int
    workout_count: int = 0


class RoutineWorkoutCreate(SQLModel):
    workout_id: int
    sets: int = 3
    reps: int = 10


class RoutineWorkoutUpdate(SQLModel):
    workout_id: Optional[int] = None  # used for the remix/swap feature
    sets: Optional[int] = None
    reps: Optional[int] = None


class RoutineWorkoutResponse(SQLModel):
    id: int
    routine_id: int
    workout_id: int
    sets: int
    reps: int
    workout: Optional[WorkoutResponse] = None