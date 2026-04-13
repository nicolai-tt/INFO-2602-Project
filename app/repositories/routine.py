from sqlmodel import Session, select
from app.models.workout import Routine, RoutineWorkout, Workout
from app.schemas.workout import RoutineCreate, RoutineUpdate, RoutineWorkoutCreate, RoutineWorkoutUpdate
import logging

logger = logging.getLogger(__name__)


class RoutineRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_routines(self, user_id):
        routines = self.db.exec(select(Routine).where(Routine.user_id == user_id)).all()
        result = []
        for r in routines:
            count = len(self.db.exec(select(RoutineWorkout).where(RoutineWorkout.routine_id == r.id)).all())
            result.append({"id": r.id, "name": r.name, "description": r.description, "user_id": r.user_id, "workout_count": count})
        return result

    def get_by_id(self, routine_id):
        return self.db.get(Routine, routine_id)

    def get_routine_detail(self, routine_id):
        routine = self.db.get(Routine, routine_id)
        if not routine:
            return None

        rws = self.db.exec(select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)).all()
        workouts = [
            {"id": rw.id, "routine_id": rw.routine_id, "workout_id": rw.workout_id,
             "sets": rw.sets, "reps": rw.reps, "workout": self.db.get(Workout, rw.workout_id)}
            for rw in rws
        ]

        return {"id": routine.id, "name": routine.name, "description": routine.description,
                "user_id": routine.user_id, "workouts": workouts}

    def create(self, user_id, data: RoutineCreate):
        try:
            routine = Routine(name=data.name, description=data.description, user_id=user_id)
            self.db.add(routine)
            self.db.commit()
            self.db.refresh(routine)
            return routine
        except Exception as e:
            logger.error(f"Error creating routine: {e}")
            self.db.rollback()
            raise

    def update(self, routine_id, data: RoutineUpdate):
        routine = self.db.get(Routine, routine_id)
        if not routine:
            raise Exception("Routine not found")
        if data.name is not None:
            routine.name = data.name
        if data.description is not None:
            routine.description = data.description
        try:
            self.db.add(routine)
            self.db.commit()
            self.db.refresh(routine)
            return routine
        except Exception as e:
            logger.error(f"Error updating routine: {e}")
            self.db.rollback()
            raise

    def delete(self, routine_id):
        routine = self.db.get(Routine, routine_id)
        if not routine:
            raise Exception("Routine not found")
        try:
            for rw in self.db.exec(select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)).all():
                self.db.delete(rw)
            self.db.delete(routine)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting routine: {e}")
            self.db.rollback()
            raise

    def add_workout(self, routine_id, data: RoutineWorkoutCreate):
        try:
            rw = RoutineWorkout(routine_id=routine_id, workout_id=data.workout_id, sets=data.sets, reps=data.reps)
            self.db.add(rw)
            self.db.commit()
            self.db.refresh(rw)
            return rw
        except Exception as e:
            logger.error(f"Error adding workout to routine: {e}")
            self.db.rollback()
            raise

    def update_routine_workout(self, rw_id, data: RoutineWorkoutUpdate):
        rw = self.db.get(RoutineWorkout, rw_id)
        if not rw:
            raise Exception("Entry not found")
        if data.workout_id is not None:
            rw.workout_id = data.workout_id
        if data.sets is not None:
            rw.sets = data.sets
        if data.reps is not None:
            rw.reps = data.reps
        try:
            self.db.add(rw)
            self.db.commit()
            self.db.refresh(rw)
            return rw
        except Exception as e:
            logger.error(f"Error updating routine workout: {e}")
            self.db.rollback()
            raise

    def remove_workout(self, rw_id):
        rw = self.db.get(RoutineWorkout, rw_id)
        if not rw:
            raise Exception("Entry not found")
        try:
            self.db.delete(rw)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error removing workout: {e}")
            self.db.rollback()
            raise