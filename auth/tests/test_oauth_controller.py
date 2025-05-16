import pytest
from fastapi import status
from auth_app.models import User
from auth_app.security.password import get_password_hash
from datetime import datetime, timezone
from jose import jwt
from auth_app.config.settings import JWT_SECRET_KEY, JWT_ALGORITHM

def test_oauth_login_redirect(client):
    response = client.get("/oauth/login")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert "oauth" in response.headers["location"].lower()

def test_oauth_callback_without_code(client):
    response = client.get("/oauth/callback")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_oauth_callback_with_invalid_code(client):
    response = client.get("/oauth/callback?code=invalid_code")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_oauth_token_refresh_without_token(client):
    response = client.post("/oauth/refresh")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_refresh_with_invalid_token(client):
    response = client.post("/oauth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_refresh_with_expired_token(client):
    # Create an expired refresh token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    response = client.post("/oauth/refresh", json={"refresh_token": expired_token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_revoke_without_token(client):
    response = client.post("/oauth/revoke")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_revoke_with_invalid_token(client):
    response = client.post("/oauth/revoke", json={"token": "invalid_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_revoke_with_expired_token(client):
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    response = client.post("/oauth/revoke", json={"token": expired_token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_introspect_without_token(client):
    response = client.post("/oauth/introspect")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_introspect_with_invalid_token(client):
    response = client.post("/oauth/introspect", json={"token": "invalid_token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_oauth_token_introspect_with_expired_token(client):
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    response = client.post("/oauth/introspect", json={"token": expired_token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 