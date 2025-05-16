import pytest
from fastapi import status
from auth_app.models import User, Authority
from auth_app.security.password import get_password_hash
from datetime import datetime, timezone
from jose import jwt
from auth_app.config.settings import JWT_SECRET_KEY, JWT_ALGORITHM

def test_register_user(client, db_session):
    # Test data
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    
    # Test registration
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]
    
    # Verify user was created in database
    user = db_session.query(User).filter(User.username == user_data["username"]).first()
    assert user is not None
    assert user.email == user_data["email"]

def test_login_user(client, db_session):
    # Create test user
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        created_date=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    # Test login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Verify token
    token = response.json()["access_token"]
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "testuser"

def test_login_invalid_credentials(client):
    login_data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

def test_register_duplicate_username(client, db_session):
    # Create initial user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    client.post("/register", json=user_data)
    
    # Try to register with same username
    duplicate_data = {
        "username": "testuser",
        "email": "another@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    response = client.post("/register", json=duplicate_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username already exists" in response.json()["detail"]

def test_register_duplicate_email(client, db_session):
    # Create initial user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    client.post("/register", json=user_data)
    
    # Try to register with same email
    duplicate_data = {
        "username": "anotheruser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    response = client.post("/register", json=duplicate_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email already exists" in response.json()["detail"]

def test_register_invalid_data(client):
    # Test with missing required fields
    invalid_data = {
        "username": "testuser"
        # missing email and password
    }
    response = client.post("/register", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_invalid_data(client):
    # Test with missing required fields
    invalid_data = {
        "username": "testuser"
        # missing password
    }
    response = client.post("/login", data=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_password_mismatch(client):
    # Test with mismatched passwords
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "differentpass"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "passwords do not match" in response.json()["detail"].lower()

def test_register_empty_fields(client):
    # Test with empty username
    user_data = {
        "username": "",
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username and password required" in response.json()["detail"].lower()

    # Test with empty password
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "",
        "password_submit": ""
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username and password required" in response.json()["detail"].lower()

def test_register_invalid_email(client):
    # Test with invalid email format
    user_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_disabled_user(client, db_session):
    # Create disabled user
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        enabled=False,
        created_date=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_locked_user(client, db_session):
    # Create locked user
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        account_non_locked=False,
        created_date=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

def test_register_with_invalid_email_format(client):
    user_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_with_missing_required_fields(client):
    user_data = {
        "username": "testuser"
        # missing email and password
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_with_missing_credentials(client):
    login_data = {
        "username": "testuser"
        # missing password
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_with_invalid_token_format(client):
    response = client.get("/protected", headers={"Authorization": "InvalidToken"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_with_expired_token(client):
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    response = client.get("/protected", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_with_invalid_token_signature(client):
    # Create a token with invalid signature
    token_data = {
        "sub": "testuser",
        "exp": 9999999999
    }
    invalid_token = jwt.encode(token_data, "wrong-secret-key", algorithm=JWT_ALGORITHM)
    
    response = client.get("/protected", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_with_missing_token_claims(client):
    # Create a token without required claims
    token_data = {
        "exp": 9999999999  # Missing 'sub' claim
    }
    invalid_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    response = client.get("/protected", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_register_with_special_characters(client):
    user_data = {
        "username": "test@user!",
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_register_with_very_long_fields(client):
    user_data = {
        "username": "a" * 256,  # Too long username
        "email": "test@example.com",
        "password": "testpass123",
        "password_submit": "testpass123"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_with_disabled_user(client, db_session):
    # Create a disabled user
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        enabled=False,
        created_date=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_with_locked_user(client, db_session):
    # Create a locked user
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        account_non_locked=False,
        created_date=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 