from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User query or message")
    role: str = Field(default="CUSTOMER", description="'CUSTOMER' or 'SUPPORT_AGENT'")
    customer_id: Optional[str] = Field(default=None, description="Required for CUSTOMER role (e.g. CUST0001)")
    booking_id: Optional[str] = Field(default=None, description="Optional booking context (e.g. B-0001)")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation turns")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Assistant response text")
    role: str = Field(..., description="Role processed")
    query_type: str = Field(..., description="Routing category: DATABASE, POLICY, HYBRID, or GENERAL")
    sources: List[str] = Field(default=[], description="Retrieved source document names or database tables")
    data_context: Optional[Dict[str, Any]] = Field(default=None, description="Structured data context retrieved")

class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    policy_docs_indexed: int
    llm_configured: bool
    timestamp: str
