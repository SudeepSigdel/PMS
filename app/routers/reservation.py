from fastapi import APIRouter, Depends, HTTPException, status, Response
from .. import models, rbac, oauth2, schemas, database

router = APIRouter(
    prefix="/reservations",
    tags=['Reservations']
)

@router.post("/", response_model=models.Reservation)
def create_reservation(db: database.SessionLocal, reservation_data):
    pass

#THIS IS NOT TOUGH