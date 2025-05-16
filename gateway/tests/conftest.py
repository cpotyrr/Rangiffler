import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from gateway.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def mock_jwt_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciJ9.dcLn5FnhcJgBz6D4u5f0v1Td3E4r5t6y7u8i9o0p1" 