from datetime import datetime, timedelta, timezone
from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config.jwt_config import JWT_PRIVATE_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models import User
from app.security.password import verify_password

class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password):
            return None
        return user

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM)

    def get_current_user(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, JWT_PRIVATE_KEY, algorithms=[JWT_ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise ValueError("Could not validate credentials")
            return {"username": username}
        except JWTError:
            raise ValueError("Could not validate credentials") 