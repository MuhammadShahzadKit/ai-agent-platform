from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MissionStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class MissionStep:
    """
    One executable step in an autonomous mission.
    """

    id: int

    description: str

    tool: str | None = None

    arguments: dict[str, Any] = field(default_factory=dict)

    status: MissionStatus = MissionStatus.PENDING

    result: Any = None

    error: str | None = None


@dataclass
class MissionPlan:
    """
    Complete plan produced by the agent planner.
    """

    objective: str

    steps: list[MissionStep] = field(default_factory=list)

    status: MissionStatus = MissionStatus.PENDING

    result: Any = None

    error: str | None = None
