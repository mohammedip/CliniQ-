from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class QueryResponse(BaseModel):
    id: int
    user_id: Optional[int]
    query: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True


class RAGRequest(BaseModel):
    question: str