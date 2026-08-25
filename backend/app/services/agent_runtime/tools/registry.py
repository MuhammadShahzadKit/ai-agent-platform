from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class AgentTool:
    """
    A capability available to an autonomous agent.
    """

    name: str

    description: str

    handler: Callable[..., Any]


class ToolRegistry:
    """
    Central registry of tools available to agents.
    """

    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(
        self,
        tool: AgentTool,
    ) -> None:

        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> AgentTool | None:

        return self._tools.get(name)

    def list_tools(self) -> list[AgentTool]:

        return list(self._tools.values())

    def descriptions(self) -> str:

        return "\n".join(
            f"- {tool.name}: {tool.description}"
            for tool in self._tools.values()
        )


registry = ToolRegistry()
