from fastapi import APIRouter, Depends, File, Form, UploadFile, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.services.auth import get_current_user
from ai.ingest import ingest_pdf
from ai.rag import answer_question
from ai.streaming import stream_answer

router = APIRouter()

# Pydantic models for request and response
class QueryRequest(BaseModel):
    question: str
    session_id: str | None = None

class QueryResponse(BaseModel):
    answer: str
    citations: list[str]

# Route: POST /ingest
@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    current_user = Depends(get_current_user)
):
    await ingest_pdf(file, session_id, current_user.id)
    return {"status": "success", "message": "File ingested successfully"}

# Route: POST /query
@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    current_user = Depends(get_current_user)
):
    result = await answer_question(request.question, request.session_id or '', current_user.id)
    return {"answer": result['answer'], "citations": result['sources']}

# Route: GET /stream
@router.get("/stream")
async def stream(
    query: str = Query(...),
    session_id: str = Query(...),
    current_user = Depends(get_current_user)
):
    return StreamingResponse(stream_answer(query, session_id, current_user.id), media_type='text/event-stream')