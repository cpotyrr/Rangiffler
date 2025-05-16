import os

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Templates directory
TEMPLATES_DIR = "auth/main/resources/templates"
STATIC_DIR = "auth/main/resources/static" 