from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.config.settings import TEMPLATES_DIR
from app.schemas import UserCreate, Token, UserRegistrationDTO
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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
    user_service: UserService = Depends()
):
    try:
        content_type = request.headers.get("content-type", "")
        
        if "form" in content_type:
            registration_data = UserRegistrationDTO(
                username=username,
                password=password,
                password_submit=passwordSubmit
            )
        else:
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request format"
                )
            registration_data = UserRegistrationDTO(
                username=user.username,
                password=user.password,
                password_submit=user.password
            )

        new_user = user_service.create_user(registration_data)

        if "form" in content_type:
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
        return new_user

    except ValueError as e:
        if "form" in content_type:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": str(e)},
                status_code=400
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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

@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def read_current_user(auth_service: AuthService = Depends()):
    try:
        return auth_service.get_current_user()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) 