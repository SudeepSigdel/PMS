from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schemas, oauth2, models, database, utils
from sqlmodel import select

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.TokenResponse)
def login(db: database.SessionLocal, user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = db.exec(select(models.User).where(models.User.username == user_credentials.username)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Credential!")
    
    if not utils.verify(user_credentials.password ,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Credential!")
    
    token = oauth2.create_token({"user_id":user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }