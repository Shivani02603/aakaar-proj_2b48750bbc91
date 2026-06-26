import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
from openai import OpenAI
from database.models import Document, DocumentChunk
from database.config import SessionLocal

class DocumentProcessingService:
    def __init__(self):
        self.embedding_model = "text-embedding-3-small"
        self.chunk_size = 1000
        self.chunk_overlap = 200

    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

    def split_text_into_chunks(self, text: str) -> List[str]:
        tokens = text.split()
        chunks = []
        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk = tokens[i:i + self.chunk_size]
            chunks.append(" ".join(chunk))
        return chunks

    def generate_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        try:
            embeddings = []
            for chunk in text_chunks:
                response = OpenAI().Embedding.create(input=chunk, model=self.embedding_model)
                embeddings.append(response["data"][0]["embedding"])
            return embeddings
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")

    def create_document(self, db: Session, user_id: uuid.UUID, filename: str, file_path: str, file_size: int) -> Document:
        try:
            document = Document(
                id=uuid.uuid4(),
                user_id=user_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                status="processing",
                created_at=datetime.utcnow(),
                processed_at=None
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            return document
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating document: {str(e)}")

    def process_document(self, db: Session, document_id: uuid.UUID):
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        try:
            text = self.extract_text_from_pdf(document.file_path)
            chunks = self.split_text_into_chunks(text)
            embeddings = self.generate_embeddings(chunks)

            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                document_chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding,
                    metadata={},
                    created_at=datetime.utcnow()
                )
                db.add(document_chunk)

            document.status = "processed"
            document.processed_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    def get_document_by_id(self, db: Session, document_id: uuid.UUID) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    def list_all_documents(self, db: Session, user_id: uuid.UUID) -> List[Document]:
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    def update_document(self, db: Session, document_id: uuid.UUID, **kwargs) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)

        document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(document)
        return document

    def delete_document(self, db: Session, document_id: uuid.UUID):
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        db.delete(document)
        db.commit()