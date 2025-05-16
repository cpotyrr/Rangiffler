from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config.settings import TEMPLATES_DIR, FRONTEND_URL
from app.services.auth_service import AuthService
from app.config.jwt_config import JWT_JWK
from app.security.jwks import create_jwks

router = APIRouter(tags=["oauth"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/.well-known/jwks.json")
async def jwks():
    return JSONResponse(content=create_jwks(JWT_JWK))

@router.get("/oauth2/authorize")
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
    auth_service: AuthService = Depends()
):
    try:
        user = auth_service.authenticate_user(username, password)
        
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

        access_token = auth_service.create_access_token({"sub": user.username})
        
        if redirect_uri and response_type == "code":
            redirect_url = f"{redirect_uri}?code={access_token}"
            return RedirectResponse(
                url=redirect_url,
                status_code=status.HTTP_303_SEE_OTHER
            )
        
        response = RedirectResponse(
            url=FRONTEND_URL,
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