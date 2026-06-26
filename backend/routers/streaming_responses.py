from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from jose import JWTError, jwt

from database.models import ChatSession, ChatMessage, User
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(tags=["Streaming Responses"])

# Pydantic schemas
class StreamingRequest(BaseModel):
    session_id: UUID
    prompt: str

class StreamingResponseSchema(BaseModel):
    token: str
    is_final: bool

# Helper function to simulate token streaming
async def token_generator(prompt: str):
    tokens = prompt.split()  # Simulate tokenization
    for token in tokens:
        yield f"{token} "
        await asyncio.sleep(0.1)  # Simulate delay for streaming

# Endpoint to stream responses
@router.post("/stream", response_model=StreamingResponseSchema)
async def stream_response(
    request: StreamingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate session existence
    session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
    
    # Simulate streaming response
    async def stream():
        async for token in token_generator(request.prompt):
            yield f"data: {token}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")