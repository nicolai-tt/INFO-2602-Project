from app.repositories.routine import RoutineRepository
from app.schemas.workout import RoutineCreate, RoutineUpdate, RoutineWorkoutCreate, RoutineWorkoutUpdate


class RoutineService:
    def __init__(self, repo: RoutineRepository):
        self.repo = repo

    def get_user_routines(self, user_id: int):
        return self.repo.get_user_routines(user_id)

    def get_routine_detail(self, routine_id: int):
        return self.repo.get_routine_detail(routine_id)

    def create(self, user_id: int, data: RoutineCreate):
        return self.repo.create(user_id, data)

    def update(self, routine_id: int, data: RoutineUpdate):
        return self.repo.update(routine_id, data)

    def delete(self, routine_id: int):
        return self.repo.delete(routine_id)

    def add_workout(self, routine_id: int, data: RoutineWorkoutCreate):
        return self.repo.add_workout(routine_id, data)

    def update_routine_workout(self, rw_id: int, data: RoutineWorkoutUpdate):
        return self.repo.update_routine_workout(rw_id, data)

    def remove_workout(self, rw_id: int):
        return self.repo.remove_workout(rw_id)