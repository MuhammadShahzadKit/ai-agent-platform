from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


def create_agent(
    db: Session,
    agent: AgentCreate,
    user_id: int,
):
    db_agent = Agent(
        **agent.model_dump(),
        user_id=user_id,
    )

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    return db_agent


def get_agents(db: Session):
    return db.query(Agent).all()


def get_user_agents(
    db: Session,
    user_id: int,
):
    return db.query(Agent).filter(
        Agent.user_id == user_id
    ).all()


def get_agent(
    db: Session,
    agent_id: int,
):
    return db.query(Agent).filter(
        Agent.id == agent_id
    ).first()


def update_agent(
    db: Session,
    agent_id: int,
    agent: AgentUpdate,
):
    db_agent = get_agent(
        db,
        agent_id,
    )

    if not db_agent:
        return None

    update_data = agent.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_agent,
            key,
            value,
        )

    db.commit()
    db.refresh(db_agent)

    return db_agent


def delete_agent(
    db: Session,
    agent_id: int,
):
    db_agent = get_agent(
        db,
        agent_id,
    )

    if not db_agent:
        return None

    db.delete(db_agent)
    db.commit()

    return db_agent