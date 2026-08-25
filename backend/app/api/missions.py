from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.agent_service import get_agent
from app.services.agent_runtime.mission_service import (
    run_agent_mission,
)


router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
)


class MissionRequest(BaseModel):
    objective: str


@router.post("/{agent_id}")
def run_mission(
    agent_id: int,
    request: MissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an autonomous mission for an agent.

    The agent receives an objective, creates a plan,
    and executes the available tools.
    """

    objective = request.objective.strip()

    if not objective:
        raise HTTPException(
            status_code=400,
            detail="Mission objective cannot be empty.",
        )

    agent = get_agent(
        db,
        agent_id,
        current_user.id,
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found.",
        )

    try:
        plan = run_agent_mission(
            db=db,
            agent=agent,
            objective=objective,
        )

    except Exception as exc:
        print(
            f"MISSION ERROR: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Mission execution failed: {exc}",
        )

    return {
        "success": plan.status.value == "completed",

        "agent": {
            "id": agent.id,
            "name": agent.name,
        },

        "mission": {
            "objective": plan.objective,
            "status": plan.status.value,
            "result": plan.result,
            "error": plan.error,
        },

        "steps": [
            {
                "id": step.id,
                "description": step.description,
                "tool": step.tool,
                "arguments": step.arguments,
                "status": step.status.value,
                "result": step.result,
                "error": step.error,
            }
            for step in plan.steps
        ],
    }
