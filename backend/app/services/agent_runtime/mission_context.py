from __future__ import annotations

from typing import Any


class MissionContext:

    def __init__(self) -> None:

        self.results: list[dict[str, Any]] = []

    def add_result(
        self,
        step_id: int,
        tool: str,
        result: Any,
        description: str = "",
    ) -> None:

        self.results.append(
            {
                "step": step_id,
                "tool": tool,
                "description": description,
                "result": result,
            }
        )

    def get_previous_results(self) -> list[dict[str, Any]]:

        return list(self.results)

    def get_last_result(self) -> dict[str, Any] | None:

        if not self.results:
            return None

        return self.results[-1]

    def build_context_text(self) -> str:

        if not self.results:
            return ""

        parts: list[str] = []

        for item in self.results:

            parts.append(
                f"""
[PREVIOUS STEP]
STEP: {item.get("step")}
TOOL: {item.get("tool")}
DESCRIPTION: {item.get("description", "")}

RESULT:
{item.get("result")}
"""
            )

        return "\n".join(parts)
