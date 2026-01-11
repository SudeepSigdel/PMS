from fastapi import FastAPI
from .routers import auth, user, room, reservation

app = FastAPI()

@app.get("/")
def index():
    return {"Hello":"World"}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(room.router)
app.include_router(reservation.router)