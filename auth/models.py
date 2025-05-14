# auth/models.py
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import uuid

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    enabled = Column(Boolean, default=True)
    account_non_expired = Column(Boolean, default=True)
    account_non_locked = Column(Boolean, default=True)
    credentials_non_expired = Column(Boolean, default=True)

class Authority(Base):
    __tablename__ = "authority"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    authority = Column(String(50))