from fastapi import APIRouter, Depends, HTTPException, status, Response
from .. import models, rbac, schemas, database, oauth2
from sqlmodel import select, asc
from typing import List, Optional

router = APIRouter(
    prefix="/rooms",
    tags=['Room']
)

#FOR ANYONE USING THIS CODE: SessionLocal is an annotated type so it does not require Depends. I know the name is confusing but this is not an error. AI MIGHT SHOW IT AS AN ERROR, JUST IGNORE IT OR PROVIDE WITH THE LOGIC IN database.py


@router.post("/", response_model=models.Room)
def add_new_room(room_data: schemas.RoomCreate, db: database.SessionLocal, current_user:models.User = Depends(rbac.require_roles(['admin']))):
    room = db.exec(select(models.Room).where(models.Room.room_number == room_data.room_number)).first()

    if room:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Room:{room_data.room_number} Already Exists!")
    
    room = models.Room(**room_data.model_dump())

    db.add(room)
    db.commit()
    db.refresh(room)

    return room


@router.get("/", response_model=List[models.Room])
def get_all_rooms(db: database.SessionLocal,
                  query_status: Optional[models.RoomStatus] = None,
                  include_inactive: Optional[bool] = False,
                current_user: models.User = Depends(oauth2.get_current_user)
                ):
    query = select(models.Room).order_by(asc(models.Room.room_number))
    if include_inactive and current_user.role not in ["admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view inactive rooms!")

    if not include_inactive:  
        query = query.where(models.Room.is_active == True)

    if query_status:
        query = query.where(models.Room.status == query_status)
    rooms = db.exec(query).all()
    return rooms

@router.get("/{id}", response_model=models.Room)
def get_a_room(id: int, db: database.SessionLocal, current_user: models.User = Depends(oauth2.get_current_user)):
    room = db.get(models.Room, id)

    if not room or (current_user.role not in ["admin"] and not room.is_active):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id:{id} not found")
    
    return room


# SINCE WE HAVE A SOFT DELETE SYSTEM WE REALLY DON'T NEED THIS BUT WE CAN KEEP THIS JUST IN CASE WE DECIDE TO UPDATE IT IN FUTURE
# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_room(db: database.SessionLocal, id: int, current_user: models.User = Depends(rbac.require_roles(['admin']))):
#     room = db.get(models.Room, id)

#     if not room:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id:{id} Not found")
    
#     db.delete(room)
#     db.commit()
    
#     return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/{id}/soft", response_model=models.Room)
def soft_delete_room(id: int, db: database.SessionLocal, current_user: models.User = Depends(rbac.require_roles(['admin']))):
    room = db.get(models.Room, id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id:{id} Not found")
    room.is_active = False
    room.status = models.RoomStatus.INACTIVE
    db.commit()
    db.refresh(room)
    return room

@router.patch("/{id}/restore", response_model=models.Room)
def restore_deleted_room(id: int, db: database.SessionLocal, current_user: models.User = Depends(rbac.require_roles(["admin"]))):
    room = db.get(models.Room, id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id:{id} Not found")
    
    room.is_active = True
    room.status = models.RoomStatus.AVAILABLE
    db.commit()
    db.refresh(room)

    return room

@router.patch("/{id}", response_model=models.Room)
def update_room_info(updated_room: schemas.RoomUpdate, db: database.SessionLocal, id: int, current_user = Depends(rbac.require_roles(["admin"]))):
    room = db.get(models.Room, id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id:{id} Not Found!")
    
    if updated_room.room_number:
        existing = db.exec(select(models.Room).where(models.Room.room_number == updated_room.room_number, models.Room.id != id)).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Room:{updated_room.room_number} Already Exists!")
    
    if not room.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restore Room before updating!")

    room_info = updated_room.model_dump(exclude_unset=True)
    for key, value in room_info.items():
        setattr(room, key, value)

    db.commit()
    db.refresh(room)

    return room

@router.patch("/{id}/status", response_model=models.Room)
def update_room_status(id: int, new_status: schemas.RoomStatusUpdate, db: database.SessionLocal, current_user: models.User = Depends(oauth2.get_current_user)):
    room = db.get(models.Room, id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id:{id} not found")

    if not room.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update status for inactive room")

    room.status = new_status.status
    
    db.commit()
    db.refresh(room)

    return room