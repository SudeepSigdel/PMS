from jose import JWTError, jwt
from .config import settings
from fastapi.security.oauth2 import OAuth2PasswordBearer
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from .database import SessionLocal
from . import models

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
EXPIRATION_TIME = settings.expiration_time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_token(payload: dict):
    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION_TIME)
    payload.update({"exp": expire})
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token

def verify_token(token, credentials_error):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        user_id = payload["user_id"]
        if not user_id:
            raise credentials_error
    except JWTError:
        raise credentials_error
    return user_id

def get_current_user(db:SessionLocal, token = Depends(oauth2_scheme)):
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error", headers={"WWW-Authenticate":"Bearer"})

    user_id = verify_token(token, credentials_error)

    user = db.get(models.User, user_id)

    return user