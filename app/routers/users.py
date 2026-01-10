from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, utils, rbac, database
from sqlmodel import select
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.UserResponse)
def create_user(db: database.SessionLocal, user_data: schemas.UserCreate, current_user: models.User = Depends(rbac.require_roles(["admin"]))):
    user = db.exec(select(models.User).where(models.User.username == user_data.username)).first()

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with {user_data.username} already exists!")
    
    password = utils.hash(user_data.password)
    user = models.User(hashed_password=password, **user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: database.SessionLocal,user: models.User = Depends(rbac.require_roles(["admin"]))):
    users = db.exec(select(models.User)).all()

    return users