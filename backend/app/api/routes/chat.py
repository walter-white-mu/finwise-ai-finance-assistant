from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.ai.service import OllamaUnavailable, chat, clear_conversation
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["AI Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(data: ChatRequest, db: Session = Depends(get_db)):
    try:
        return await chat(data.message, data.conversation_id, db)
    except OllamaUnavailable as exc:
        raise HTTPException(status_code=503, detail="Local Ollama is unavailable. Start Ollama and ensure the configured model is installed.") from exc


@router.delete("/chat/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat_endpoint(conversation_id: str):
    clear_conversation(conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
