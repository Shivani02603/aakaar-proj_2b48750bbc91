import os
import tempfile
from fastapi import UploadFile
import tiktoken
from pypdf import PdfReader
from .embeddings import get_embedding
from pgvector.asyncpg import VectorStore

async def chunk(text: str, chunk_size: int = 1000, overlap: int = 200):
    enc = tiktoken.get_encoding('cl100k_base')
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - overlap
    return chunks

async def ingest_pdf(file: UploadFile, session_id: str, user_id: str):
    contents = await file.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or '')[1])
    tmp.write(contents)
    tmp.flush()
    file_path = tmp.name

    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        original_filename = file.filename
        chunks = await chunk(text)
        metadata_list = []
        embeddings = []

        for i, chunk_text in enumerate(chunks):
            metadata = {
                'source_filename': original_filename,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'page_or_row': f"Page {i + 1}"
            }
            embedding = await get_embedding(chunk_text)
            metadata_list.append(metadata)
            embeddings.append(embedding)

        vector_store = VectorStore(os.getenv("PGVECTOR_CONNECTION_STRING"))
        await vector_store.insert(embeddings, metadata_list)

    finally:
        os.unlink(file_path)