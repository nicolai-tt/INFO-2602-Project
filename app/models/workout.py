from sqlmodel import Field, SQLModel
from typing import Optional


class Workout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = ""
    muscle_group: str  # chest, back, legs, shoulders, arms, core, cardio
    difficulty: str = "beginner"  # beginner, intermediate, advanced


class Routine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    user_id: int = Field(foreign_key="user.id")


class RoutineWorkout(SQLModel, table=True):
    __tablename__ = "routine_workout"

    id: Optional[int] = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routine.id")
    workout_id: int = Field(foreign_key="workout.id")
    sets: int = 3
    reps: int = 10