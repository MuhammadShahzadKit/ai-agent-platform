from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolDefinition:

    name: str

    description: str

    handler: Callable[..., Any]

    destructive: bool = False


class ToolRegistry:

    def __init__(self) -> None:

        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        tool: ToolDefinition,
    ) -> None:

        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> ToolDefinition | None:

        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:

        return list(
            self._tools.values()
        )

    def descriptions(self) -> str:

        if not self._tools:
            return "No tools are currently available."

        return "\n".join(
            f"- {tool.name}: {tool.description}"
            for tool in self._tools.values()
        )
