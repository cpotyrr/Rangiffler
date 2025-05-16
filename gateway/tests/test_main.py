import pytest
from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt
from gateway.gateway_app.config.settings import settings
from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Rangiffler Gateway"}

def test_protected_route_with_valid_token():
    # Create a valid token
    token_data = {
        "sub": "testuser",
        "exp": 9999999999  # Far future expiration
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello testuser"}

def test_protected_route_without_token():
    response = client.get("/api/protected")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_protected_route_with_invalid_token():
    response = client.get("/api/protected", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}

def test_protected_route_with_expired_token():
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "exp": 0  # Expired token
    }
    expired_token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}

def test_protected_route_with_missing_sub():
    # Create a token without 'sub' claim
    token_data = {
        "exp": 9999999999  # No 'sub' claim
    }
    invalid_token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    response = client.get("/api/protected", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}

def test_protected_route_with_invalid_auth_header():
    # Test with invalid Authorization header format
    headers = {"Authorization": "InvalidFormat"}
    response = client.get("/api/protected", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_cors_headers():
    # Test CORS headers
    response = client.get("/", headers={"Origin": settings.FRONTEND_URL})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == settings.FRONTEND_URL
    assert response.headers.get("access-control-allow-credentials") == "true"