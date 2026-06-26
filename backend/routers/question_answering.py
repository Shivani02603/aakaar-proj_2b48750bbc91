from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

from database.models import DocumentChunk, Document, User
from database.config import get_db
from backend.services.auth import get_current_user
from backend.services.question_answering_service import generate_answer_with_citations

router = APIRouter(tags=["Question Answering"])

# Pydantic schemas for request and response
class QueryRequest(BaseModel):
    query: str

class ChunkCitation(BaseModel):
    chunk_id: UUID
    content: str
    document_id: UUID
    filename: str

class AnswerResponse(BaseModel):
    answer: str
    citations: List[ChunkCitation]

# Endpoint to handle question answering
@router.post("/answer", response_model=AnswerResponse)
async def answer_query(
    query_request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts a user query, retrieves the top-5 most relevant chunks, and generates a concise answer
    using a large language model with citations to the source chunks.
    """
    query = query_request.query

    # Retrieve top-5 relevant chunks based on the query
    try:
        relevant_chunks = (
            db.query(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(Document.user_id == current_user.id)
            .order_by(DocumentChunk.embedding.distance(query))  # Assuming distance method exists
            .limit(5)
            .all()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving relevant chunks.",
        )

    if not relevant_chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No relevant chunks found for the query.",
        )

    # Prepare citations
    citations = [
        ChunkCitation(
            chunk_id=chunk.id,
            content=chunk.content,
            document_id=chunk.document_id,
            filename=db.query(Document).filter(Document.id == chunk.document_id).first().filename,
        )
        for chunk in relevant_chunks
    ]

    # Generate answer using the LLM
    try:
        answer = await generate_answer_with_citations(query, citations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating answer using the language model.",
        )

    return AnswerResponse(answer=answer, citations=citations)