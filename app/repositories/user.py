from sqlmodel import Session, select, func
from app.models.user import UserBase, User
from app.utilities.pagination import Pagination
from app.schemas.user import UserUpdate
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: UserBase):
        try:
            user = User.model_validate(user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            self.db.rollback()
            raise

    def search_users(self, query: str, page=1, limit=10):
        offset = (page - 1) * limit
        db_qry = select(User)
        if query:
            db_qry = db_qry.where(
                User.username.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")
            )
        count = self.db.exec(select(func.count()).select_from(db_qry.subquery())).one()
        users = self.db.exec(db_qry.offset(offset).limit(limit)).all()
        return users, Pagination(total_count=count, current_page=page, limit=limit)

    def get_by_username(self, username: str):
        return self.db.exec(select(User).where(User.username == username)).one_or_none()

    def get_by_id(self, user_id: int):
        return self.db.get(User, user_id)

    def get_all_users(self):
        return self.db.exec(select(User)).all()

    def update_user(self, user_id: int, user_data: UserUpdate):
        user = self.db.get(User, user_id)
        if not user:
            raise Exception("User not found")
        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            self.db.rollback()
            raise

    def delete_user(self, user_id: int):
        user = self.db.get(User, user_id)
        if not user:
            raise Exception("User not found")
        try:
            self.db.delete(user)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            self.db.rollback()
            raise