import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from auth_app.utils.security import get_password_hash, verify_password, create_access_token
from auth_app.config.settings import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

def test_password_hashing():
    # Test password hashing
    password = "testpass123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    
    # Hash should be a string
    assert isinstance(hashed, str)
    
    # Hash should be longer than original password
    assert len(hashed) > len(password)

def test_password_verification():
    # Test password verification
    password = "testpass123"
    hashed = get_password_hash(password)
    
    # Correct password should verify
    assert verify_password(password, hashed)
    
    # Wrong password should not verify
    assert not verify_password("wrongpass", hashed)
    
    # Different hash for same password should not verify
    different_hash = get_password_hash(password)
    assert not verify_password(password, different_hash)

def test_access_token_creation():
    # Test access token creation
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    
    # Token should be decodable
    decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    
    # Token should contain original data
    assert decoded["sub"] == data["sub"]
    
    # Token should have expiration
    assert "exp" in decoded
    
    # Expiration should be in the future
    exp_time = datetime.fromtimestamp(decoded["exp"], timezone.utc)
    now = datetime.now(timezone.utc)
    assert exp_time > now
    
    # Expiration should be approximately JWT_ACCESS_TOKEN_EXPIRE_MINUTES in the future
    expected_exp = now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    time_diff = abs((exp_time - expected_exp).total_seconds())
    assert time_diff < 60  # Allow 1 minute difference for test execution time

def test_access_token_with_additional_data():
    # Test access token with additional data
    data = {
        "sub": "testuser",
        "custom_field": "custom_value",
        "roles": ["user", "admin"]
    }
    token = create_access_token(data)
    decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    
    # All original data should be preserved
    assert decoded["sub"] == data["sub"]
    assert decoded["custom_field"] == data["custom_field"]
    assert decoded["roles"] == data["roles"]

def test_access_token_expiration():
    # Test token expiration
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # Token should be valid initially
    decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["sub"] == data["sub"]
    
    # Token should be invalid after expiration
    # We can't easily test this directly, but we can verify the expiration time
    exp_time = datetime.fromtimestamp(decoded["exp"], timezone.utc)
    now = datetime.now(timezone.utc)
    assert exp_time > now 