from sqlalchemy.orm import Session

from app.models.conversation import Conversation


def get_memory(
    db: Session,
    agent_id: int,
):
    """
    Return every conversation for an agent.
    """

    return (
        db.query(Conversation)
        .filter(
            Conversation.agent_id == agent_id
        )
        .order_by(Conversation.id.asc())
        .all()
    )


def delete_memory(
    db: Session,
    agent_id: int,
):
    """
    Delete every conversation for an agent.
    """

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.agent_id == agent_id
        )
        .all()
    )

    for conversation in conversations:
        db.delete(conversation)

    db.commit()