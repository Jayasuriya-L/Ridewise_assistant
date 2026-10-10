import time
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import get_db_connection
from .policy_retrieval import policy_retriever
from .llm import llm_client
from .schemas import ChatRequest, ChatResponse, HealthResponse
from .services import RideWiseService

app = FastAPI(
    title="RideWise Assist API",
    description="Intelligent AI Assistant for RideWise Mobility operations and policies",
    version="1.0.0"
)

# CORS configuration restricted to frontend origins
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Verify backend status, SQLite database connectivity, and policy indices."""
    db_ok = False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers;")
            db_ok = True
    except Exception as e:
        db_ok = False

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        database_connected=db_ok,
        policy_docs_indexed=len(policy_retriever.chunks),
        llm_configured=llm_client.is_configured(),
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Main conversational endpoint handling Customer and Support Agent queries.
    Enforces customer ownership, retrieves verified database & policy facts,
    and calls the NeoStats LLM wrapper.
    """
    try:
        response = RideWiseService.process_chat(req)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
