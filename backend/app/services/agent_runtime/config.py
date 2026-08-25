from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentRuntimeConfig:
    """
    Runtime configuration for an autonomous AI agent.

    This is intentionally separate from the database Agent model.
    The database stores what the agent IS.
    The runtime controls how the agent OPERATES.
    """

    max_steps: int = 10

    allow_browser: bool = True

    allow_file_access: bool = True

    allow_document_search: bool = True

    allow_scheduling: bool = True

    allow_tool_execution: bool = True

    require_confirmation_for_destructive_actions: bool = True

    memory_enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)
