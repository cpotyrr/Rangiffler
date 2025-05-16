from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from ..schemas import UserCreate

class IUserService(ABC):
    @abstractmethod
    def create_user(self, db: Session, user_data: dict) -> bool:
        pass

    @abstractmethod
    def authenticate_user(self, db: Session, username: str, password: str):
        pass

    @abstractmethod
    def get_user_by_username(self, db: Session, username: str):
        pass 