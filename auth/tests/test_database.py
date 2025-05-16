import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from auth_app.database import Base, get_db, engine, SessionLocal
from auth_app.models import User

def test_database_connection():
    # Test that we can create tables
    Base.metadata.create_all(bind=engine)
    
    # Test that we can create a session
    db = SessionLocal()
    assert db is not None
    
    # Test that we can perform a simple query
    result = db.execute("SELECT 1").scalar()
    assert result == 1
    
    db.close()

def test_get_db():
    # Test that get_db returns a session
    db = next(get_db())
    assert db is not None
    
    # Test that the session is working
    result = db.execute("SELECT 1").scalar()
    assert result == 1
    
    db.close()

def test_database_operations():
    # Create a test engine and session
    test_engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        # Test creating a user
        user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password",
            enabled=True,
            account_non_expired=True,
            account_non_locked=True,
            credentials_non_expired=True
        )
        db.add(user)
        db.commit()
        
        # Test retrieving the user
        saved_user = db.query(User).filter(User.username == "testuser").first()
        assert saved_user is not None
        assert saved_user.username == "testuser"
        assert saved_user.email == "test@example.com"
        
        # Test updating the user
        saved_user.email = "updated@example.com"
        db.commit()
        
        updated_user = db.query(User).filter(User.username == "testuser").first()
        assert updated_user.email == "updated@example.com"
        
        # Test deleting the user
        db.delete(saved_user)
        db.commit()
        
        deleted_user = db.query(User).filter(User.username == "testuser").first()
        assert deleted_user is None
        
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

def test_database_rollback():
    # Create a test engine and session
    test_engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        # Test rollback on error
        user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password"
        )
        db.add(user)
        db.commit()
        
        # Try to create a user with the same username (should fail)
        duplicate_user = User(
            username="testuser",
            email="another@example.com",
            password="hashed_password"
        )
        db.add(duplicate_user)
        
        try:
            db.commit()
        except Exception:
            db.rollback()
        
        # Verify that the duplicate user was not added
        users = db.query(User).filter(User.username == "testuser").all()
        assert len(users) == 1
        
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine) 