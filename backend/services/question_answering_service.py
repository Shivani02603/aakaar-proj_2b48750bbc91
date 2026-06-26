import uuid
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from openai import OpenAI
from database.models import DocumentChunk
from database.config import get_db


class QuestionAnsweringService:
    @staticmethod
    def create_chunk(db: Session, document_id: uuid.UUID, chunk_index: int, content: str, embedding: List[float], metadata: dict) -> DocumentChunk:
        try:
            new_chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                chunk_index=chunk_index,
                content=content,
                embedding=embedding,
                metadata=metadata,
                created_at=datetime.utcnow()
            )
            db.add(new_chunk)
            db.commit()
            db.refresh(new_chunk)
            return new_chunk
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating chunk: {str(e)}")

    @staticmethod
    def get_chunk_by_id(db: Session, chunk_id: uuid.UUID) -> DocumentChunk:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        return chunk

    @staticmethod
    def list_all_chunks(db: Session, document_id: uuid.UUID) -> List[DocumentChunk]:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        if not chunks:
            raise HTTPException(status_code=404, detail="No chunks found for the given document")
        return chunks

    @staticmethod
    def update_chunk(db: Session, chunk_id: uuid.UUID, content: Optional[str] = None, metadata: Optional[dict] = None) -> DocumentChunk:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        if content:
            chunk.content = content
        if metadata:
            chunk.metadata = metadata
        
        try:
            db.commit()
            db.refresh(chunk)
            return chunk
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating chunk: {str(e)}")

    @staticmethod
    def delete_chunk(db: Session, chunk_id: uuid.UUID) -> None:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        try:
            db.delete(chunk)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting chunk: {str(e)}")

    @staticmethod
    def answer_question(db: Session, query: str, document_id: uuid.UUID) -> dict:
        # Retrieve top-5 most relevant chunks based on embeddings
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index).limit(5).all()
        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant chunks found for the given document")

        # Prepare content for the LLM
        context = "\n".join([chunk.content for chunk in chunks])
        citations = [{"chunk_index": chunk.chunk_index, "metadata": chunk.metadata} for chunk in chunks]

        # Generate answer using LLM
        try:
            llm = OpenAI()  # Replace with actual LLM client initialization
            response = llm.generate_answer(query=query, context=context)
            return {
                "answer": response,
                "citations": citations
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")