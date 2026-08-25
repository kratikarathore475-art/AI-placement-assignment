from fastapi import APIRouter
from pydantic import BaseModel

from services.rag_service import get_answer

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    top_k: int = 4
    topic_filter: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/ask", response_model=ChatResponse)
def ask_question(request: ChatRequest):
    result = get_answer(
        query=request.query,
        top_k=request.top_k,
        topic_filter=request.topic_filter,
    )
    return result