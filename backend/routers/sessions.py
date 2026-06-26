from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from database.models import User
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(tags=["Sessions"])

class SessionCreate(BaseModel):
    title: str = "New Chat"

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

@router.get("/")
async def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return sessions

@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_session = ChatSession(
        id=uuid4(),
        user_id=current_user.id,
        title=session_data.title,
        created_at=datetime.utcnow(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.delete("/{session_id}")
async def delete_session(session_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted successfully"}

@router.get("/{session_id}/messages")
async def list_messages(session_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/{session_id}/messages", response_model=MessageResponse)
async def create_message(session_id: UUID, message_data: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or not owned by user")
    new_message = ChatMessage(
        id=uuid4(),
        session_id=session_id,
        role=message_data.role,
        content=message_data.content,
        created_at=datetime.utcnow(),
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message