from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.conversation import Conversation
from app.services.ai_service import chat_with_ai
from app.services.agent_service import get_agent

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    agent_id: int
    prompt: str


@router.post("/")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    agent = get_agent(
        db,
        request.agent_id,
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    response = chat_with_ai(
        prompt=request.prompt,
        model=agent.model,
        system_prompt=agent.system_prompt,
        temperature=agent.temperature,
    )

    conversation = Conversation(
        user_message=request.prompt,
        ai_response=response,
        agent_id=agent.id,
    )

    db.add(conversation)
    db.commit()

    return {
        "agent": agent.name,
        "response": response,
    }