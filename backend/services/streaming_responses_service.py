import uuid
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import ChatMessage
from database.config import get_db


class StreamingResponsesService:
    @staticmethod
    def create(chat_message: ChatMessage, db: Session = Depends(get_db)) -> ChatMessage:
        try:
            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)
            return chat_message
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating chat message: {str(e)}")

    @staticmethod
    def get_by_id(message_id: uuid.UUID, db: Session = Depends(get_db)) -> ChatMessage:
        chat_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not chat_message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        return chat_message

    @staticmethod
    def list_all(session_id: uuid.UUID, db: Session = Depends(get_db)) -> List[ChatMessage]:
        try:
            chat_messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
            return chat_messages
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving chat messages: {str(e)}")

    @staticmethod
    def update(message_id: uuid.UUID, updated_data: dict, db: Session = Depends(get_db)) -> ChatMessage:
        chat_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not chat_message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        try:
            for key, value in updated_data.items():
                setattr(chat_message, key, value)
            db.commit()
            db.refresh(chat_message)
            return chat_message
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating chat message: {str(e)}")

    @staticmethod
    def delete(message_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
        chat_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not chat_message:
            raise HTTPException(status_code=404, detail="Chat message not found")
        try:
            db.delete(chat_message)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting chat message: {str(e)}")

    @staticmethod
    def stream_response_tokens(session_id: uuid.UUID, db: Session = Depends(get_db)) -> str:
        """
        Simulates streaming response tokens for a given chat session.
        This method would typically interact with an AI model to generate tokens in real-time.
        """
        chat_messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
        if not chat_messages:
            raise HTTPException(status_code=404, detail="No chat messages found for the session")

        # Simulate streaming tokens (replace with actual AI model integration)
        try:
            for message in chat_messages:
                yield f"Streaming token for message: {message.content}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error streaming response tokens: {str(e)}")