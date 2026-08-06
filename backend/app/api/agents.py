from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_username
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
)
from app.services.agent_service import (
    create_agent,
    get_agents,
    get_agent,
    get_user_agents,
    update_agent,
    delete_agent,
)

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.post(
    "/",
    response_model=AgentResponse,
)
def create(
    agent: AgentCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    return create_agent(
        db=db,
        agent=agent,
        user_id=user.id,
    )


@router.get(
    "/",
    response_model=list[AgentResponse],
)
def read_all(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    return get_user_agents(
        db,
        user.id,
    )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
)
def read_one(
    agent_id: int,
    db: Session = Depends(get_db),
):
    agent = get_agent(
        db,
        agent_id,
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return agent


@router.put(
    "/{agent_id}",
    response_model=AgentResponse,
)
def update(
    agent_id: int,
    data: AgentUpdate,
    db: Session = Depends(get_db),
):
    agent = update_agent(
        db,
        agent_id,
        data,
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return agent


@router.delete(
    "/{agent_id}",
)
def remove(
    agent_id: int,
    db: Session = Depends(get_db),
):
    agent = delete_agent(
        db,
        agent_id,
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return {
        "message": "Agent deleted"
    }