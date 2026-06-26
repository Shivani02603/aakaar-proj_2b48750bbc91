import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, Depends, UploadFile
from sqlalchemy.orm import Session
from database.models import Document, User
from database.config import SessionLocal

class DocumentUploadService:
    def __init__(self, db: Session = Depends(SessionLocal)):
        self.db = db

    def create_document(self, user_id: uuid.UUID, file: UploadFile) -> Document:
        try:
            # Validate file type
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

            # Generate unique file path
            file_id = uuid.uuid4()
            file_path = f"uploads/{file_id}.pdf"

            # Save file to disk
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            # Create document record
            document = Document(
                id=file_id,
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                status="uploaded",
                created_at=datetime.utcnow(),
                processed_at=None,
            )
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            return document
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

    def get_document_by_id(self, document_id: uuid.UUID) -> Document:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        return document

    def list_user_documents(self, user_id: uuid.UUID) -> List[Document]:
        documents = self.db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    def update_document_status(self, document_id: uuid.UUID, status: str) -> Document:
        document = self.get_document_by_id(document_id)
        document.status = status
        document.processed_at = datetime.utcnow() if status == "processed" else None
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_document(self, document_id: uuid.UUID) -> None:
        document = self.get_document_by_id(document_id)
        try:
            # Delete file from disk
            if os.path.exists(document.file_path):
                os.remove(document.file_path)

            # Delete document record
            self.db.delete(document)
            self.db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")