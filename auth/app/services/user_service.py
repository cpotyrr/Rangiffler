from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..interfaces.user_service import IUserService
from ..models import User
from ..utils.security import get_password_hash, verify_password

class UserService(IUserService):
    def create_user(self, db: Session, user_data: dict) -> bool:
        # Проверка существующего пользователя
        if self.get_user_by_username(db, user_data["username"]):
            return False
        
        # Создание нового пользователя
        hashed_password = get_password_hash(user_data["password"])
        new_user = User(
            username=user_data["username"],
            password=hashed_password,
            enabled=True,
            account_non_expired=True,
            account_non_locked=True,
            credentials_non_expired=True,
            created_date=datetime.now(timezone.utc)
        )

        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return True
        except Exception:
            db.rollback()
            return False

    def authenticate_user(self, db: Session, username: str, password: str):
        user = self.get_user_by_username(db, username)
        if not user or not verify_password(password, user.password):
            return None
        return user

    def get_user_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first() 