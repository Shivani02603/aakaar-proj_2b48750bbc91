from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
import os
import fitz  # PyMuPDF for PDF text extraction
from pydantic import BaseModel, Field
from openai import OpenAIEmbeddings

from database.models import Document, DocumentChunk
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(tags=["Document Processing"])

# Pydantic schemas
class DocumentBase(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    file_path: str
    file_size: int
    status: str
    created_at: datetime
    processed_at: datetime | None

class DocumentResponse(DocumentBase):
    pass

class DocumentChunkBase(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: dict
    created_at: datetime

class DocumentChunkResponse(DocumentChunkBase):
    pass

class DocumentUploadRequest(BaseModel):
    file: UploadFile

# Helper functions
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    text = ""
    try:
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text from PDF: {str(e)}",
        )
    return text

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    tokens = text.split()
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(" ".join(chunk))
    return chunks

def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    """Generate embeddings for text chunks using OpenAI."""
    try:
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        embeddings = [embeddings_model.embed(chunk) for chunk in chunks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}",
        )
    return embeddings

# Routes
@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a document and process it."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    # Save the file locally
    file_path = f"uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)

    # Split text into chunks
    chunks = split_text_into_chunks(text)

    # Generate embeddings for chunks
    embeddings = generate_embeddings(chunks)

    # Create a new Document record
    document = Document(
        id=UUID(),
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        status="processed",
        created_at=datetime.utcnow(),
        processed_at=datetime.utcnow(),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Create DocumentChunk records
    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        document_chunk = DocumentChunk(
            id=UUID(),
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding,
            metadata={},
            created_at=datetime.utcnow(),
        )
        db.add(document_chunk)
    db.commit()

    return document

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents for the current user."""
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific document by ID."""
    document = db.query(Document).filter(
        Document.id == document_id, Document.user_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a specific document by ID."""
    document = db.query(Document).filter(
        Document.id == document_id, Document.user_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    # Delete associated chunks
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

    # Delete the document
    db.delete(document)
    db.commit()

    # Remove the file from the filesystem
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    return