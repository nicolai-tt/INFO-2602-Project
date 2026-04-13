from sqlmodel import Session, select
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate
import logging

logger = logging.getLogger(__name__)


class WorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, muscle_group=None):
        query = select(Workout)
        if muscle_group:
            query = query.where(Workout.muscle_group == muscle_group)
        return self.db.exec(query).all()

    def get_by_id(self, workout_id):
        return self.db.get(Workout, workout_id)

    def get_alternatives(self, workout_id):
        workout = self.db.get(Workout, workout_id)
        if not workout:
            return []
        return self.db.exec(
            select(Workout).where(Workout.muscle_group == workout.muscle_group, Workout.id != workout_id)
        ).all()

    def create(self, data: WorkoutCreate):
        try:
            workout = Workout.model_validate(data)
            self.db.add(workout)
            self.db.commit()
            self.db.refresh(workout)
            return workout
        except Exception as e:
            logger.error(f"Error creating workout: {e}")
            self.db.rollback()
            raise

    def delete(self, workout_id):
        workout = self.db.get(Workout, workout_id)
        if not workout:
            raise Exception("Workout not found")
        try:
            self.db.delete(workout)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting workout: {e}")
            self.db.rollback()
            raise