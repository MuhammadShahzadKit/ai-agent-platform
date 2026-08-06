from typing import Optional

from pydantic import BaseModel, ConfigDict


class AgentBase(BaseModel):
    name: str
    role: str
    description: Optional[str] = None
    system_prompt: str
    model: str = "qwen2.5:3b"
    temperature: int = 1


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[int] = None


class AgentResponse(AgentBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)