from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..config.settings import JWT_SECRET_KEY, JWT_ALGORITHM, TEMPLATES_DIR
from ..database import get_db
from ..schemas import UserCreate, Token
from ..services.user_service import UserService
from ..utils.security import create_access_token

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_service = UserService()

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@router.get("/register", response_class=HTMLResponse)
def show_register_form(request: Request, error: str = None):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": error}
    )

@router.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request, error: str = None, logout: str = None):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error, "logout": logout}
    )

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(None),
    password: str = Form(None),
    passwordSubmit: str = Form(None),
    user: UserCreate = None,
    db: Session = Depends(get_db)
):
    try:
        content_type = request.headers.get("content-type", "")
        
        if "form" in content_type:
            if not username or not password:
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": "Username and password required"},
                    status_code=400
                )
            
            if password != passwordSubmit:
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": "Passwords do not match"},
                    status_code=400
                )
                
            user_data = {"username": username, "password": password}
        else:
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request format"
                )
            user_data = user.model_dump()

        if user_service.create_user(db, user_data):
            if "form" in content_type:
                return RedirectResponse(
                    url="/login",
                    status_code=status.HTTP_303_SEE_OTHER
                )
            return {"message": "User created successfully"}
        else:
            if "form" in content_type:
                return templates.TemplateResponse(
                    "register.html",
                    {"request": request, "error": "Username already exists"},
                    status_code=400
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

    except Exception as e:
        if "form" in content_type:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": str(e)},
                status_code=500
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
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
        user = user_service.authenticate_user(db, username, password)
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

        access_token = create_access_token(data={"sub": user.username})
        
        if redirect_uri and response_type == "code":
            redirect_url = f"{redirect_uri}?code={access_token}"
            return RedirectResponse(
                url=redirect_url,
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
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

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def read_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception 