from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    AUTH_SERVICE_URL: str = "http://auth_service:9000"
    FRONTEND_URL: str = "http://localhost:3000"

settings = Settings() 