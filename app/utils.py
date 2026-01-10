from passlib.context import CryptContext
from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def calculate_bill_total(reservation: models.Reservation):
    total = (reservation.check_in - reservation.check_out).days * reservation.per_night_rate
    return total