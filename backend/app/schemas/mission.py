from typing import Optional

from pydantic import BaseModel, ConfigDict


class MissionCreate(BaseModel):
    title: str
    objective: str
    agent_id: int


class MissionUpdate(BaseModel):
    title: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None
    result: Optional[str] = None


class MissionResponse(BaseModel):
    id: int
    title: str
    objective: str
    status: str
    result: Optional[str] = None
    agent_id: int

    model_config = ConfigDict(
        from_attributes=True
    )