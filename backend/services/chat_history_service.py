import uuid
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import ChatSession, ChatMessage
from database.config import get_db


class ChatHistoryService:
    @staticmethod
    def create_chat_session(user_id: uuid.UUID, document_id: uuid.UUID, title: str, db: Session = Depends(get_db)) -> ChatSession:
        try:
            new_session = ChatSession(
                id=uuid.uuid4(),
                user_id=user_id,
                document_id=document_id,
                title=title,
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            return new_session
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")

    @staticmethod
    def get_chat_session_by_id(session_id: uuid.UUID, db: Session = Depends(get_db)) -> ChatSession:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session

    @staticmethod
    def list_all_chat_sessions(user_id: uuid.UUID, db: Session = Depends(get_db)) -> List[ChatSession]:
        try:
            sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
            return sessions
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve chat sessions: {str(e)}")

    @staticmethod
    def update_chat_session(session_id: uuid.UUID, title: Optional[str], db: Session = Depends(get_db)) -> ChatSession:
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")
            if title:
                session.title = title
            db.commit()
            db.refresh(session)
            return session
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update chat session: {str(e)}")

    @staticmethod
    def delete_chat_session(session_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")
            db.delete(session)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete chat session: {str(e)}")

    @staticmethod
    def create_chat_message(session_id: uuid.UUID, role: str, content: str, chunk_ids: Optional[List[uuid.UUID]], db: Session = Depends(get_db)) -> ChatMessage:
        try:
            new_message = ChatMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                role=role,
                content=content,
                chunk_ids=chunk_ids or [],
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return new_message
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create chat message: {str(e)}")

    @staticmethod
    def get_chat_messages_by_session(session_id: uuid.UUID, db: Session = Depends(get_db)) -> List[ChatMessage]:
        try:
            messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
            return messages
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve chat messages: {str(e)}")

    @staticmethod
    def delete_chat_message(message_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        try:
            message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                raise HTTPException(status_code=404, detail="Chat message not found")
            db.delete(message)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete chat message: {str(e)}")