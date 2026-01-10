from sqlmodel import SQLModel, Field, Integer, Column, ForeignKey
from pydantic import EmailStr
from datetime import date, datetime
from enum import StrEnum
from sqlalchemy import CheckConstraint

class RoomStatus(StrEnum):
    AVAILABLE= "available"
    OCCUPIED= "occupied"
    MAINTENANCE= "maintenance"

class ReservationStatus(StrEnum):
    RESERVED= "reserved"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class Roles(StrEnum):
    ADMIN = "admin"
    STAFF= "staff"

class Room(SQLModel, table=True):
    __tablename__="rooms" #type: ignore
    id: int| None = Field(default=None, primary_key=True)
    room_number: int = Field(unique=True)
    room_type: str
    capacity: int
    price: float
    status: RoomStatus

class Guest(SQLModel, table=True):
    __tablename__="guests" #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    name: str
    phone: str
    email: EmailStr = Field(unique=True)

class Reservation(SQLModel, table=True):
    __tablename__="reservations" #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    guest_id: int = Field(sa_column=Column(Integer, ForeignKey("guests.id", ondelete="CASCADE")))
    room_id: int = Field(sa_column=Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE")))
    check_in: date
    check_out: date
    no_of_guests: int
    per_night_rate: float
    status: ReservationStatus
    created_at: datetime | None = Field(default_factory=datetime.utcnow)

    __table_args__ = tuple(
        CheckConstraint("check_in< check_out", name="check_check_in_before_check_out")
    )

class Bill(SQLModel, table= True):
    __tablename__="bills" #type: ignore
    id: int | None = Field(default = None, primary_key=True)
    reservation_id: int = Field(sa_column=Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE")))
    total_amount: float
    paid: bool | None = Field(default=False)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)

class User(SQLModel, table=True):
    __tablename__ = "users" #type: ignore
    id: int | None= Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    role: Roles