from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy.orm import Session
from ..interfaces.user_service import IUserService
from ..models import User
from ..schemas import UserRegistrationDTO
from ..security.password import get_password_hash, verify_password
from app.database import get_db

class UserService(IUserService):
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def validate_registration(self, registration_data: UserRegistrationDTO) -> None:
        if not registration_data.username or not registration_data.password:
            raise ValueError("Username and password required")
            
        if registration_data.password != registration_data.password_submit:
            raise ValueError("Passwords do not match")
            
        if self.db.query(User).filter(User.username == registration_data.username).first():
            raise ValueError("Username already exists")

    def create_user(self, registration_data: UserRegistrationDTO) -> User:
        self.validate_registration(registration_data)
        
        # Создание нового пользователя
        hashed_password = get_password_hash(registration_data.password)
        new_user = User(
            username=registration_data.username,
            password=hashed_password,
            enabled=True,
            account_non_expired=True,
            account_non_locked=True,
            credentials_non_expired=True,
            created_date=datetime.now(timezone.utc)
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error creating user: {str(e)}")

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user.password):
            return None
        return user

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first() 