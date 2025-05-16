import pytest
from datetime import datetime, timezone
from auth_app.services.auth_service import AuthService
from auth_app.models import User
from auth_app.security.password import get_password_hash
from jose import jwt
from auth_app.config.settings import JWT_SECRET_KEY, JWT_ALGORITHM

def test_validate_token_with_invalid_token(db_session):
    service = AuthService(db_session)
    assert not service.validate_token("invalid_token")

def test_validate_token_with_expired_token(db_session):
    service = AuthService(db_session)
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    assert not service.validate_token(expired_token)

def test_validate_token_with_invalid_signature(db_session):
    service = AuthService(db_session)
    # Create a token with invalid signature
    token_data = {
        "sub": "testuser",
        "exp": 9999999999
    }
    invalid_token = jwt.encode(token_data, "wrong-secret-key", algorithm=JWT_ALGORITHM)
    assert not service.validate_token(invalid_token)

def test_validate_token_with_missing_claims(db_session):
    service = AuthService(db_session)
    # Create a token without required claims
    token_data = {
        "exp": 9999999999  # Missing 'sub' claim
    }
    invalid_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    assert not service.validate_token(invalid_token)

def test_refresh_token_with_invalid_token(db_session):
    service = AuthService(db_session)
    with pytest.raises(ValueError):
        service.refresh_token("invalid_token")

def test_refresh_token_with_expired_token(db_session):
    service = AuthService(db_session)
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    with pytest.raises(ValueError):
        service.refresh_token(expired_token)

def test_refresh_token_with_invalid_signature(db_session):
    service = AuthService(db_session)
    # Create a token with invalid signature
    token_data = {
        "sub": "testuser",
        "exp": 9999999999
    }
    invalid_token = jwt.encode(token_data, "wrong-secret-key", algorithm=JWT_ALGORITHM)
    with pytest.raises(ValueError):
        service.refresh_token(invalid_token)

def test_refresh_token_with_missing_claims(db_session):
    service = AuthService(db_session)
    # Create a token without required claims
    token_data = {
        "exp": 9999999999  # Missing 'sub' claim
    }
    invalid_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    with pytest.raises(ValueError):
        service.refresh_token(invalid_token)

def test_revoke_token_with_invalid_token(db_session):
    service = AuthService(db_session)
    assert not service.revoke_token("invalid_token")

def test_revoke_token_with_expired_token(db_session):
    service = AuthService(db_session)
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    assert not service.revoke_token(expired_token)

def test_revoke_token_with_invalid_signature(db_session):
    service = AuthService(db_session)
    # Create a token with invalid signature
    token_data = {
        "sub": "testuser",
        "exp": 9999999999
    }
    invalid_token = jwt.encode(token_data, "wrong-secret-key", algorithm=JWT_ALGORITHM)
    assert not service.revoke_token(invalid_token)

def test_revoke_token_with_missing_claims(db_session):
    service = AuthService(db_session)
    # Create a token without required claims
    token_data = {
        "exp": 9999999999  # Missing 'sub' claim
    }
    invalid_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    assert not service.revoke_token(invalid_token) 