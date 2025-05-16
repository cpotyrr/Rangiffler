# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from auth_app.config.settings import FRONTEND_URL, STATIC_DIR
from auth_app.controllers.auth_controller import router as auth_router
from auth_app.controllers.oauth_controller import router as oauth_router
from auth_app.database import get_db

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

# Создаём таблицы при запуске приложения
@app.on_event("startup")
async def startup_event():
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
