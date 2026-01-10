from sqlmodel import SQLModel
from .models import Roles

class UserResponse(SQLModel):
    id: int
    username: str
    role: str

class UserCreate(SQLModel):
    username: str
    password: str
    role: Roles

class TokenResponse(SQLModel):
    access_token: str
    token_type: str