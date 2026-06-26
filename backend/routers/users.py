from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from database.models import User
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(tags=["Users"])

@router.get("/")
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/{id}")
async def get_user(id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{id}")
async def update_user(id: UUID, user_data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for key, value in user_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{id}")
async def delete_user(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}