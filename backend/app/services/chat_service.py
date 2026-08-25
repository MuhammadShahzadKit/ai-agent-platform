from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.conversation import Conversation
from app.services.ollama_service import ask_ollama


def chat_with_agent(
    db: Session,
    agent_id: int,
    message: str,
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    if not agent:
        raise Exception("Agent not found")

    # Load previous conversation
    history = (
        db.query(Conversation)
        .filter(Conversation.agent_id == agent_id)
        .order_by(Conversation.id.asc())
        .all()
    )

    messages = [
        {
            "role": "system",
            "content": agent.system_prompt,
        }
    ]

    for item in history:
        messages.append(
            {
                "role": "user",
                "content": item.user_message,
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": item.agent_response,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    response = ask_ollama(
        model=agent.model,
        messages=messages,
    )

    conversation = Conversation(
        agent_id=agent.id,
        user_message=message,
        agent_response=response,
    )

    db.add(conversation)
    db.commit()

    return {
        "agent": agent.name,
        "response": response,
    }