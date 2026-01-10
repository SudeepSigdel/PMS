from sqlmodel import create_engine, Session
from .config import settings
from typing import Annotated
from fastapi import Depends

DATABASE_URL = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

SessionLocal = Annotated[Session, Depends(get_session)]