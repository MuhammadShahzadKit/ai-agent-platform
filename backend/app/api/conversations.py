from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.conversation import Conversation

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get("/{agent_id}")
def get_conversations(
    agent_id: int,
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.agent_id == agent_id)
        .all()
    )

    return conversations