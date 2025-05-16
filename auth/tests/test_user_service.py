import pytest
from datetime import datetime, timezone
from auth_app.services.user_service import UserService
from auth_app.schemas import UserRegistrationDTO
from auth_app.models import User
from auth_app.security.password import get_password_hash

def test_create_user(db_session):
    service = UserService(db_session)
    user_data = UserRegistrationDTO(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        password_submit="testpass123"
    )
    user = service.create_user(user_data)
    assert user.username == user_data.username
    assert user.email == user_data.email
    assert user.password != user_data.password  # Password should be hashed

def test_validate_registration(db_session):
    service = UserService(db_session)
    user_data = UserRegistrationDTO(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        password_submit="testpass123"
    )
    
    # Should not raise any exceptions
    service.validate_registration(user_data)

def test_validate_registration_empty_fields(db_session):
    service = UserService(db_session)
    user_data = UserRegistrationDTO(
        username="",
        email="test@example.com",
        password="testpass123",
        password_submit="testpass123"
    )
    
    with pytest.raises(ValueError, match="Username and password required"):
        service.validate_registration(user_data)

def test_validate_registration_password_mismatch(db_session):
    service = UserService(db_session)
    user_data = UserRegistrationDTO(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        password_submit="differentpass"
    )
    
    with pytest.raises(ValueError, match="Passwords do not match"):
        service.validate_registration(user_data)

def test_validate_registration_duplicate_username(db_session):
    service = UserService(db_session)
    
    # Create initial user
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        created_date=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to register with same username
    user_data = UserRegistrationDTO(
        username="testuser",
        email="another@example.com",
        password="testpass123",
        password_submit="testpass123"
    )
    
    with pytest.raises(ValueError, match="Username already exists"):
        service.validate_registration(user_data)

def test_validate_registration_duplicate_email(db_session):
    service = UserService(db_session)
    
    # Create initial user
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        created_date=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to register with same email
    user_data = UserRegistrationDTO(
        username="anotheruser",
        email="test@example.com",
        password="testpass123",
        password_submit="testpass123"
    )
    
    with pytest.raises(ValueError, match="Email already exists"):
        service.validate_registration(user_data)

def test_authenticate_user(db_session):
    service = UserService(db_session)
    
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
    
    # Test successful authentication
    authenticated_user = service.authenticate_user("testuser", "testpass123")
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    
    # Test failed authentication
    assert service.authenticate_user("testuser", "wrongpass") is None
    assert service.authenticate_user("nonexistent", "testpass123") is None

def test_get_user_by_username(db_session):
    service = UserService(db_session)
    
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
    
    # Test getting existing user
    found_user = service.get_user_by_username("testuser")
    assert found_user is not None
    assert found_user.username == "testuser"
    
    # Test getting non-existent user
    assert service.get_user_by_username("nonexistent") is None

def test_get_user_by_email(db_session):
    service = UserService(db_session)
    
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
    
    # Test getting existing user
    found_user = service.get_user_by_email("test@example.com")
    assert found_user is not None
    assert found_user.email == "test@example.com"
    
    # Test getting non-existent user
    assert service.get_user_by_email("nonexistent@example.com") is None

def test_username_exists(db_session):
    service = UserService(db_session)
    
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
    
    # Test existing username
    assert service.username_exists("testuser") is True
    
    # Test non-existent username
    assert service.username_exists("nonexistent") is False

def test_email_exists(db_session):
    service = UserService(db_session)
    
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
    
    # Test existing email
    assert service.email_exists("test@example.com") is True
    
    # Test non-existent email
    assert service.email_exists("nonexistent@example.com") is False

def test_update_user(db_session):
    service = UserService(db_session)
    
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
    
    # Update user
    updated_data = {
        "email": "updated@example.com",
        "enabled": False
    }
    updated_user = service.update_user("testuser", updated_data)
    assert updated_user.email == "updated@example.com"
    assert updated_user.enabled is False

def test_delete_user(db_session):
    service = UserService(db_session)
    
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
    
    # Delete user
    service.delete_user("testuser")
    assert service.get_user_by_username("testuser") is None

def test_lock_user(db_session):
    service = UserService(db_session)
    
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
    
    # Lock user
    service.lock_user("testuser")
    locked_user = service.get_user_by_username("testuser")
    assert locked_user.account_non_locked is False

def test_unlock_user(db_session):
    service = UserService(db_session)
    
    # Create test user
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
    
    # Unlock user
    service.unlock_user("testuser")
    unlocked_user = service.get_user_by_username("testuser")
    assert unlocked_user.account_non_locked is True

def test_disable_user(db_session):
    service = UserService(db_session)
    
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
    
    # Disable user
    service.disable_user("testuser")
    disabled_user = service.get_user_by_username("testuser")
    assert disabled_user.enabled is False

def test_enable_user(db_session):
    service = UserService(db_session)
    
    # Create test user
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
    
    # Enable user
    service.enable_user("testuser")
    enabled_user = service.get_user_by_username("testuser")
    assert enabled_user.enabled is True

def test_is_user_enabled(db_session):
    service = UserService(db_session)
    
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
    
    # Check enabled status
    assert service.is_user_enabled("testuser") is True
    
    # Disable user
    service.disable_user("testuser")
    assert service.is_user_enabled("testuser") is False

def test_is_user_locked(db_session):
    service = UserService(db_session)
    
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
    
    # Check locked status
    assert service.is_user_locked("testuser") is False
    
    # Lock user
    service.lock_user("testuser")
    assert service.is_user_locked("testuser") is True 