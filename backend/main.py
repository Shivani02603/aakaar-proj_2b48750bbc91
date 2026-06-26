import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import ValidationError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from backend.routers.auth import router as auth_router
from backend.routers.chat_history import router as chat_history_router
from backend.routers.document_processing import router as document_processing_router
from backend.routers.document_upload import router as document_upload_router
from backend.routers.question_answering import router as question_answering_router
from backend.routers.sessions import router as sessions_router
from backend.routers.streaming_responses import router as streaming_responses_router
from backend.routers.users import router as users_router
from backend.routers.vector_storage import router as vector_storage_router
from database.config import init_db

# Initialize the FastAPI app
app = FastAPI(
    title="Aakaar Project",
    description="Backend for AI-powered web application",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse({"detail": str(exc)}, status_code=429)


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# Mount routers
app.include_router(auth_router, prefix='/api/auth', tags=['Auth'])
app.include_router(chat_history_router, prefix='/api/chat', tags=['Chat History'])
app.include_router(document_processing_router, prefix='/api/documents', tags=['Document Processing'])
app.include_router(document_upload_router, prefix='/api/documents', tags=['Document Upload'])
app.include_router(question_answering_router, prefix='/api', tags=['Question Answering'])
app.include_router(sessions_router, prefix='/api/chat/sessions', tags=['Sessions'])
app.include_router(streaming_responses_router, prefix='/api', tags=['Streaming Responses'])
app.include_router(users_router, prefix='/api/ai/query', tags=['Users'])
app.include_router(vector_storage_router, prefix='/api/ai/query', tags=['Vector Storage'])

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    yield
    # Shutdown logic
    pass


app.router.lifespan_context = lifespan

# AI_ROUTER_INJECTION_POINT — do not remove this line
# AI layer — mounted by Agent 8B
from ai.routes import router as ai_router
app.include_router(ai_router, prefix='/api/ai', tags=['AI'])
