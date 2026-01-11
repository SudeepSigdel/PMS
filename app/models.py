from sqlmodel import SQLModel, Field, Integer, Column, ForeignKey, Numeric, Relationship
from pydantic import EmailStr
from datetime import date, datetime
from enum import StrEnum
from sqlalchemy import CheckConstraint
from decimal import Decimal
from typing import List

class RoomStatus(StrEnum):
    AVAILABLE= "available"
    OCCUPIED= "occupied"
    MAINTENANCE= "maintenance"
    INACTIVE = "inactive"

class ReservationStatus(StrEnum):
    RESERVED= "reserved"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class Roles(StrEnum):
    ADMIN = "admin"
    STAFF= "staff"

class RoomType(StrEnum):
    SINGLE = "single"
    DOUBLE = "double"

class Room(SQLModel, table=True):
    __tablename__="rooms" #type: ignore
    id: int| None = Field(default=None, primary_key=True)
    room_number: int = Field(unique=True)
    room_type: RoomType
    capacity: int
    price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    status: RoomStatus
    is_active: bool | None = Field(default=True)
    reservation: List["Reservation"] = Relationship(back_populates="room")

    __table_args__ = (
        CheckConstraint("capacity > 0", name="check_capacity_more_than_zero"),
        CheckConstraint("price > 0", name="check_price_more_than_zero")
    )

class Guest(SQLModel, table=True):
    __tablename__="guests" #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    name: str
    phone: str
    email: EmailStr = Field(unique=True)
    reservation: List["Reservation"] = Relationship(back_populates="guest")

class Reservation(SQLModel, table=True):
    __tablename__="reservations" #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    guest_id: int = Field(sa_column=Column(Integer, ForeignKey("guests.id", ondelete="CASCADE")))
    room_id: int = Field(sa_column=Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE")))
    check_in: date
    check_out: date
    no_of_guests: int
    per_night_rate: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    status: ReservationStatus
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    
    guest: List["Guest"] = Relationship(back_populates="reservations")
    room: List["Room"] = Relationship(back_populates="reservations")
    bill: List["Bill"] = Relationship(back_populates="reservations")

    __table_args__ = (
        CheckConstraint("check_in < check_out", name="check_check_in_before_check_out"),
        CheckConstraint("per_night_rate > 0", name="check_per_night_rate_is_not_zero"),
        CheckConstraint("no_of_guests > 0", name= "check_no_of_guest_not_zero")
    )

class Bill(SQLModel, table= True):
    __tablename__="bills" #type: ignore
    id: int | None = Field(default = None, primary_key=True)
    reservation_id: int = Field(sa_column=Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE")))
    total_amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    paid: bool | None = Field(default=False)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    reservation: List["Reservation"] = Relationship(
        back_populates="bill"
    )

class User(SQLModel, table=True):
    __tablename__ = "users" #type: ignore
    id: int | None= Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    role: Roles