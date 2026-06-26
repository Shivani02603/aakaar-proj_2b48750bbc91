from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os
from datetime import datetime

from database.models import Document, User
from database.config import get_db
from backend.services.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(tags=["Document Upload"])

# Pydantic Schemas
class DocumentBase(BaseModel):
    filename: str
    file_path: str
    file_size: int
    status: str
    created_at: datetime
    processed_at: datetime | None = None

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID

class DocumentCreate(BaseModel):
    filename: str = Field(..., example="example.pdf")
    file_size: int = Field(..., example=1024)

# Routes
@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document for processing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )

    # Save file to disk
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the file."
        )

    # Create document record in the database
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        status="uploaded",
        created_at=datetime.utcnow(),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get("/", response_model=List[DocumentResponse])
def get_user_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all documents uploaded by the authenticated user.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_by_id(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific document by its ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id, Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a specific document by its ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id, Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    # Remove file from disk
    try:
        os.remove(document.file_path)
    except FileNotFoundError:
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete the file from disk."
        )

    # Remove record from database
    db.delete(document)
    db.commit()

    return