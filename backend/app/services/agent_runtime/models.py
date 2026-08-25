from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MissionStatus(str, Enum):
    PLANNING = "planning"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentRuntimeConfig:

    max_steps: int = 10

    allow_browser: bool = True

    allow_file_access: bool = True

    allow_document_search: bool = True

    allow_scheduling: bool = True

    allow_tool_execution: bool = True

    require_confirmation_for_destructive_actions: bool = True

    memory_enabled: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class MissionStep:

    id: int

    description: str

    tool: str

    arguments: dict[str, Any] = field(
        default_factory=dict
    )

    status: StepStatus = StepStatus.PENDING

    result: Any = None

    error: str | None = None


@dataclass
class MissionPlan:

    objective: str

    status: MissionStatus = MissionStatus.PLANNING

    steps: list[MissionStep] = field(
        default_factory=list
    )

    result: Any = None

    error: str | None = None
