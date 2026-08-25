from __future__ import annotations

from app.services.agent_runtime.models import (
    MissionPlan,
    MissionStatus,
    StepStatus,
)

from app.services.agent_runtime.planner import AgentPlanner

from app.services.agent_runtime.tool_registry import (
    ToolRegistry,
)

from app.services.agent_runtime.mission_context import (
    MissionContext,
)


class AgentRuntime:

    def __init__(
        self,
        config,
        tool_registry: ToolRegistry | None = None,
    ) -> None:

        self.config = config

        self.registry = (
            tool_registry
            or ToolRegistry()
        )

        self.planner = AgentPlanner()

        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:

        from app.services.agent_runtime.tools import (
            reason_about_task,
            execute_action,
            write_content,
            research_task,
            browser_task,
        )

        from app.services.agent_runtime.tool_registry import (
            ToolDefinition,
        )

        self.registry.register(
            ToolDefinition(
                name="reason",
                description=(
                    "Analyze an objective and determine "
                    "the next action."
                ),
                handler=reason_about_task,
            )
        )

        self.registry.register(
            ToolDefinition(
                name="execute",
                description=(
                    "Execute a general autonomous action."
                ),
                handler=execute_action,
            )
        )

        self.registry.register(
            ToolDefinition(
                name="content_writer",
                description=(
                    "Create content for a requested task."
                ),
                handler=write_content,
            )
        )

        self.registry.register(
            ToolDefinition(
                name="research",
                description=(
                    "Research and collect current information."
                ),
                handler=research_task,
            )
        )

        if self.config.allow_browser:

            self.registry.register(
                ToolDefinition(
                    name="browser",
                    description=(
                        "Perform browser-based automation."
                    ),
                    handler=browser_task,
                )
            )

    def run(
        self,
        objective: str,
        agent_instructions: str = "",
    ) -> MissionPlan:

        plan = self.planner.plan(
            objective=objective,
            agent_instructions=agent_instructions,
            available_tools=self.registry.descriptions(),
            max_steps=self.config.max_steps,
        )

        plan.status = MissionStatus.RUNNING

        context = MissionContext()

        execution_results: list[dict] = []

        try:

            for step in plan.steps:

                step.status = StepStatus.RUNNING

                tool = self.registry.get(
                    step.tool
                )

                if tool is None:

                    step.status = StepStatus.FAILED

                    step.error = (
                        f"Tool '{step.tool}' is not available."
                    )

                    plan.status = MissionStatus.FAILED
                    plan.error = step.error

                    return plan

                if (
                    tool.destructive
                    and self.config.require_confirmation_for_destructive_actions
                ):

                    step.status = StepStatus.FAILED

                    step.error = (
                        "Destructive action requires confirmation."
                    )

                    plan.status = MissionStatus.FAILED
                    plan.error = step.error

                    return plan

                try:

                    arguments = dict(
                        step.arguments or {}
                    )

                    arguments[
                        "previous_results"
                    ] = context.get_previous_results()

                    arguments[
                        "previous_context"
                    ] = context.build_context_text()

                    result = tool.handler(
                        objective=objective,
                        arguments=arguments,
                        config=self.config,
                    )

                    step.result = result

                    step.status = StepStatus.COMPLETED

                    context.add_result(
                        step_id=step.id,
                        tool=step.tool,
                        description=step.description,
                        result=result,
                    )

                    execution_results.append(
                        {
                            "step": step.id,
                            "tool": step.tool,
                            "description": step.description,
                            "result": result,
                        }
                    )

                except Exception as exc:

                    step.status = StepStatus.FAILED

                    step.error = str(exc)

                    plan.status = MissionStatus.FAILED
                    plan.error = str(exc)

                    return plan

            plan.status = MissionStatus.COMPLETED

            plan.result = execution_results

            return plan

        except Exception as exc:

            plan.status = MissionStatus.FAILED

            plan.error = str(exc)

            return plan
