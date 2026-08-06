from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import chat_with_ai

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(data: ChatRequest):
    answer = chat_with_ai(data.prompt)

    return {
        "response": answer,
    }