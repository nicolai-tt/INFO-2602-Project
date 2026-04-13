from app.repositories.workout import WorkoutRepository
from app.schemas.workout import WorkoutCreate
from typing import Optional


class WorkoutService:
    def __init__(self, repo: WorkoutRepository):
        self.repo = repo

    def get_all(self, muscle_group: Optional[str] = None):
        return self.repo.get_all(muscle_group)

    def get_by_id(self, workout_id: int):
        return self.repo.get_by_id(workout_id)

    def get_alternatives(self, workout_id: int):
        return self.repo.get_alternatives(workout_id)

    def create(self, data: WorkoutCreate):
        return self.repo.create(data)

    def delete(self, workout_id: int):
        return self.repo.delete(workout_id)