import os

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Frontend settings
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:3001")
FRONTEND_REDIRECT_URL = f"{FRONTEND_URL}"

# Static files and templates
STATIC_DIR = "auth/main/resources/static"
TEMPLATES_DIR = "auth/main/resources/templates"

# Database settings
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://rangiffler:rangiffler@localhost:5432/auth_db"
) 