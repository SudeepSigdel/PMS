from sqlmodel import SQLModel, Field, Column, Integer, ForeignKey
from datetime import datetime
from enum import StrEnum

class RoomStatus(StrEnum):
    CLEAN = "clean"
    DIRTY = "dirty"
    OUT_OF_ORDER = "out_of_order"

class Hotel(SQLModel, table=True):
    __tablename__ = "hotels" #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    name: str =Field(nullable=False)
    address: str =Field(nullable=False)
    timezone: str

class Room_type(SQLModel, table=True):
    __tablename__ = "room_types" #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    hotel_id: int = Field(sa_column=Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE")))
    name: str
    max_occupancy: int
    base_price: float

class Room(SQLModel, table=True):
    __tablename__ = "rooms" #type: ignore
    id: int | None = Field(default=None, primary_key=True)
    hotel_id: int = Field(sa_column=Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE")))
    room_type_id: int = Field(sa_column=Column(Integer, ForeignKey("room_types.id", ondelete="CASCADE")))
    room_number: str
    floor_number: int
    status: RoomStatus