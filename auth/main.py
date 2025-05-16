# main.py
import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config.settings import FRONTEND_URL, STATIC_DIR
from app.controllers.auth_controller import router as auth_router
from app.database import engine, get_db
from app.models import Base, User
from app.schemas import UserCreate, Token

# Создаём таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройки JWT из переменных окружения
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="auth/main/resources/templates")

# Корень
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/register", response_class=HTMLResponse)
def show_register_form(request: Request, error: str = None):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": error}
    )

@app.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request, error: str = None, logout: str = None):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error, "logout": logout}
    )

# OAuth2 endpoints
@app.get("/oauth2/authorize")
async def authorize(
    request: Request,
    response_type: str,
    client_id: str,
    scope: str,
    redirect_uri: str,
    code_challenge: str = None,
    code_challenge_method: str = None
):
    if response_type != "code" or client_id != "client":
        raise HTTPException(
            status_code=400,
            detail="Invalid request parameters"
        )
    
    # Показываем форму логина, добавляя все параметры OAuth2
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "oauth2_params": {
                "response_type": response_type,
                "client_id": client_id,
                "scope": scope,
                "redirect_uri": redirect_uri,
                "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method
            }
        }
    )

# Хеширование пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Аутентификация пользователя
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

# Создание JWT-токена
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Регистрация пользователя (работает и с формами, и с JSON)
@app.post("/register")
async def register(
        request: Request,
        username: str = Form(None),
        password: str = Form(None),
        passwordSubmit: str = Form(None),
        user: UserCreate = None,
        db: Session = Depends(get_db)
):
    try:
        # Определяем тип контента
        content_type = request.headers.get("content-type", "")

        # Обработка form-data
        if "form" in content_type:
            if not username or not password:
                return templates.TemplateResponse(
                    "register.html",
                    {
                        "request": request,
                        "error": "Username and password required"
                    },
                    status_code=400
                )
            
            if password != passwordSubmit:
                return templates.TemplateResponse(
                    "register.html",
                    {
                        "request": request,
                        "error": "Passwords do not match"
                    },
                    status_code=400
                )
                
            user_data = {
                "username": username,
                "password": password
            }

        # Обработка JSON
        else:
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request format"
                )
            user_data = user.model_dump()

        # Проверка существующего пользователя
        db_user = db.query(User).filter(
            User.username == user_data["username"]
        ).first()

        if db_user:
            if "form" in content_type:
                return templates.TemplateResponse(
                    "register.html",
                    {
                        "request": request,
                        "error": "Username already exists"
                    },
                    status_code=400
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Создание нового пользователя
        hashed_password = get_password_hash(user_data["password"])
        new_user = User(
            username=user_data["username"],
            password=hashed_password,
            enabled=True,
            account_non_expired=True,
            account_non_locked=True,
            credentials_non_expired=True,
            created_date=datetime.now(timezone.utc)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Ответ в зависимости от типа запроса
        if "form" in content_type:
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
        return new_user

    except Exception as e:
        db.rollback()
        if "form" in content_type:
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "error": str(e)
                },
                status_code=500
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/login")
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    response_type: str = Form(None),
    client_id: str = Form(None),
    scope: str = Form(None),
    redirect_uri: str = Form(None),
    code_challenge: str = Form(None),
    code_challenge_method: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Аутентификация пользователя
        user = authenticate_user(db, username, password)
        if not user:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Incorrect username or password",
                    "oauth2_params": {
                        "response_type": response_type,
                        "client_id": client_id,
                        "scope": scope,
                        "redirect_uri": redirect_uri,
                        "code_challenge": code_challenge,
                        "code_challenge_method": code_challenge_method
                    }
                },
                status_code=401
            )

        # Создание токена
        access_token = create_access_token(data={"sub": user.username})
        
        if redirect_uri and response_type == "code":
            # Для OAuth2 flow добавляем токен как code в redirect_uri
            redirect_url = f"{redirect_uri}?code={access_token}"
            return RedirectResponse(
                url=redirect_url,
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            # Для обычного логина редиректим на фронтенд с токеном в cookie
            response = RedirectResponse(
                url="http://127.0.0.1:3001",
                status_code=status.HTTP_303_SEE_OTHER
            )
            response.set_cookie(
                key="id_token",
                value=access_token,
                httponly=False,
                secure=False,
                samesite="lax",
                max_age=1800
            )
            return response

    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": str(e),
                "oauth2_params": {
                    "response_type": response_type,
                    "client_id": client_id,
                    "scope": scope,
                    "redirect_uri": redirect_uri,
                    "code_challenge": code_challenge,
                    "code_challenge_method": code_challenge_method
                }
            },
            status_code=500
        )

# Получение токена через API
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Проверка токена
@app.get("/users/me")
def read_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception

# Подключаем роуты
app.include_router(auth_router)
