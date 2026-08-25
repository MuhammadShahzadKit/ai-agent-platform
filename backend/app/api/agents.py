from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
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
    data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_agent(
        db,
        data,
        current_user.id,
    )


@router.get(
    "/",
    response_model=list[AgentResponse],
)
def read_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_agents(
        db,
        current_user.id,
    )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
)
def read_one(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = get_agent(
        db,
        agent_id,
        current_user.id,
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
    current_user: User = Depends(get_current_user),
):
    agent = update_agent(
        db,
        agent_id,
        data,
        current_user.id,
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent


@router.delete(
    "/{agent_id}",
)
def delete(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = delete_agent(
        db,
        agent_id,
        current_user.id,
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return {
        "message": "Agent deleted successfully"
    }