from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionResult:
    success: bool
    action: str
    status: str
    result: Any = None
    error: str | None = None


class AutonomousExecutor:

    def __init__(self, config=None):
        self.config = config

    def execute(
        self,
        objective: str,
        arguments: dict[str, Any] | None = None,
    ) -> ExecutionResult:

        text = objective.lower().strip()

        # --------------------------------------------------
        # Browser / website / publishing tasks
        # --------------------------------------------------

        browser_keywords = [
            "open youtube",
            "youtube studio",
            "publish",
            "upload",
            "login",
            "click",
            "browser",
            "website",
            "web page",
            "navigate",
        ]

        if any(keyword in text for keyword in browser_keywords):

            return ExecutionResult(
                success=True,
                action="browser",
                status="ready",
                result={
                    "type": "browser_execution",
                    "objective": objective,
                    "next_executor": "browser",
                },
            )

        # --------------------------------------------------
        # Content creation tasks
        # --------------------------------------------------

        content_keywords = [
            "create a video",
            "create youtube video",
            "create a youtube video",
            "youtube video",
            "video about",
            "write a script",
            "write an article",
            "create content",
            "content package",
            "generate content",
        ]

        if any(keyword in text for keyword in content_keywords):

            return ExecutionResult(
                success=True,
                action="content",
                status="ready",
                result={
                    "type": "content_execution",
                    "objective": objective,
                    "next_executor": "content_writer",
                },
            )

        # --------------------------------------------------
        # Research tasks
        # --------------------------------------------------

        research_keywords = [
            "research",
            "find information",
            "search for",
            "investigate",
            "latest developments",
        ]

        if any(keyword in text for keyword in research_keywords):

            return ExecutionResult(
                success=True,
                action="research",
                status="ready",
                result={
                    "type": "research_execution",
                    "objective": objective,
                    "next_executor": "research",
                },
            )

        # --------------------------------------------------
        # General execution
        # --------------------------------------------------

        return ExecutionResult(
            success=True,
            action="general",
            status="ready",
            result={
                "type": "general_execution",
                "objective": objective,
                "next_executor": None,
            },
        )
