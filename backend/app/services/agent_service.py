from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


def create_agent(
    db: Session,
    data: AgentCreate,
    user_id: int,
):
    agent = Agent(
        name=data.name,
        role=data.role,
        description=data.description,
        system_prompt=data.system_prompt,
        model=data.model,
        temperature=data.temperature,
        use_rag=data.use_rag,
        user_id=user_id,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


def get_agents(
    db: Session,
    user_id: int,
):
    return (
        db.query(Agent)
        .filter(
            Agent.user_id == user_id
        )
        .all()
    )


def get_agent(
    db: Session,
    agent_id: int,
    user_id: int,
):
    return (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.user_id == user_id,
        )
        .first()
    )


def update_agent(
    db: Session,
    agent_id: int,
    data: AgentUpdate,
    user_id: int,
):
    agent = get_agent(
        db,
        agent_id,
        user_id,
    )

    if not agent:
        return None

    if data.name is not None:
        agent.name = data.name

    if data.role is not None:
        agent.role = data.role

    if data.description is not None:
        agent.description = data.description

    if data.system_prompt is not None:
        agent.system_prompt = data.system_prompt

    if data.model is not None:
        agent.model = data.model

    if data.temperature is not None:
        agent.temperature = data.temperature

    if data.use_rag is not None:
        agent.use_rag = data.use_rag

    db.commit()
    db.refresh(agent)

    return agent


def delete_agent(
    db: Session,
    agent_id: int,
    user_id: int,
):
    agent = get_agent(
        db,
        agent_id,
        user_id,
    )

    if not agent:
        return None

    db.delete(agent)
    db.commit()

    return agent