from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.memory_service import (
    get_memory,
    delete_memory,
)

router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


@router.get("/{agent_id}")
def read_memory(
    agent_id: int,
    db: Session = Depends(get_db),
):
    return get_memory(
        db,
        agent_id,
    )


@router.delete("/{agent_id}")
def clear_memory(
    agent_id: int,
    db: Session = Depends(get_db),
):
    delete_memory(
        db,
        agent_id,
    )

    return {
        "message": "Memory cleared successfully"
    }