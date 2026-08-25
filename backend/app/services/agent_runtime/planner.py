from __future__ import annotations

from app.services.agent_runtime.models import (
    MissionPlan,
    MissionStep,
)


class AgentPlanner:

    def plan(
        self,
        objective: str,
        agent_instructions: str,
        available_tools: str,
        max_steps: int,
    ) -> MissionPlan:

        steps = self._build_plan(
            objective=objective,
            max_steps=max_steps,
        )

        return MissionPlan(
            objective=objective,
            steps=steps,
        )

    def _build_plan(
        self,
        objective: str,
        max_steps: int,
    ) -> list[MissionStep]:

        text = objective.lower()

        steps: list[MissionStep] = []

        browser_requested = any(
            word in text
            for word in [
                "youtube studio",
                "publish",
                "upload",
                "browser",
                "website",
                "open youtube",
                "login",
                "click",
            ]
        )

        content_requested = any(
            phrase in text
            for phrase in [
                "create a video",
                "create youtube video",
                "create a youtube video",
                "youtube video",
                "video package",
                "create content",
                "write a script",
                "generate content",
            ]
        )

        research_requested = any(
            word in text
            for word in [
                "research",
                "latest",
                "recent",
                "developments",
                "find information",
                "investigate",
            ]
        )

        # --------------------------------------------------
        # YouTube content mission
        #
        # A YouTube creation/publishing mission should
        # automatically research the subject first so that
        # the content writer receives useful context.
        # --------------------------------------------------

        youtube_content_mission = (
            content_requested
            and any(
                word in text
                for word in [
                    "youtube",
                    "video",
                ]
            )
        )

        if youtube_content_mission:
            research_requested = True

        # --------------------------------------------------
        # Research
        # --------------------------------------------------

        if research_requested:

            steps.append(
                MissionStep(
                    id=len(steps) + 1,
                    description=(
                        "Research information relevant to "
                        "the objective."
                    ),
                    tool="research",
                    arguments={
                        "objective": objective,
                    },
                )
            )

        # --------------------------------------------------
        # Content creation
        # --------------------------------------------------

        if content_requested:

            steps.append(
                MissionStep(
                    id=len(steps) + 1,
                    description=(
                        "Create the requested content package."
                    ),
                    tool="content_writer",
                    arguments={
                        "objective": objective,
                    },
                )
            )

        # --------------------------------------------------
        # Browser execution
        # --------------------------------------------------

        if browser_requested:

            steps.append(
                MissionStep(
                    id=len(steps) + 1,
                    description=(
                        "Perform the requested browser operation."
                    ),
                    tool="browser",
                    arguments={
                        "objective": objective,
                    },
                )
            )

        # --------------------------------------------------
        # General task
        # --------------------------------------------------

        if not steps:

            steps.append(
                MissionStep(
                    id=1,
                    description=(
                        "Analyze and execute the objective."
                    ),
                    tool="execute",
                    arguments={
                        "objective": objective,
                    },
                )
            )

        return steps[:max_steps]
