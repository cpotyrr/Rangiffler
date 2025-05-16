# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import FRONTEND_URL, STATIC_DIR
from app.controllers.auth_controller import router as auth_router
from app.controllers.oauth_controller import router as oauth_router
from app.database import engine
from app.models import Base

# Создаём таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(oauth_router)
