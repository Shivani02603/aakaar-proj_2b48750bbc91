import uuid
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import DocumentChunk
from database.config import SessionLocal


class VectorStorageService:
    @staticmethod
    def create_chunk(
        db: Session,
        document_id: uuid.UUID,
        chunk_index: int,
        content: str,
        embedding: List[float],
        metadata: Optional[dict] = None,
    ) -> DocumentChunk:
        try:
            new_chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                chunk_index=chunk_index,
                content=content,
                embedding=embedding,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
            )
            db.add(new_chunk)
            db.commit()
            db.refresh(new_chunk)
            return new_chunk
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating document chunk: {str(e)}")

    @staticmethod
    def get_chunk_by_id(db: Session, chunk_id: uuid.UUID) -> DocumentChunk:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        return chunk

    @staticmethod
    def list_all_chunks(db: Session, document_id: Optional[uuid.UUID] = None) -> List[DocumentChunk]:
        try:
            query = db.query(DocumentChunk)
            if document_id:
                query = query.filter(DocumentChunk.document_id == document_id)
            return query.all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving document chunks: {str(e)}")

    @staticmethod
    def update_chunk(
        db: Session,
        chunk_id: uuid.UUID,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[dict] = None,
    ) -> DocumentChunk:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")

        try:
            if content is not None:
                chunk.content = content
            if embedding is not None:
                chunk.embedding = embedding
            if metadata is not None:
                chunk.metadata = metadata
            chunk.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(chunk)
            return chunk
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating document chunk: {str(e)}")

    @staticmethod
    def delete_chunk(db: Session, chunk_id: uuid.UUID) -> None:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")

        try:
            db.delete(chunk)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting document chunk: {str(e)}")


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()