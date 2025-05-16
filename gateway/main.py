# main.py
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

app = FastAPI()

# Настройки из переменных окружения
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
AUTH_SERVICE_URL = f"http://{os.getenv('AUTH_SERVICE_HOST')}:{os.getenv('AUTH_SERVICE_PORT')}"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_SERVICE_URL}/token")


# Проверка токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# Корень
@app.get("/")
def home():
    return {"message": "Welcome to Rangiffler!"}


# Пример защищённого эндпоинта
@app.get("/protected")
def protected_route(username: str = Depends(get_current_user)):
    return {"message": f"Hello {username}, you are authorized!"}
