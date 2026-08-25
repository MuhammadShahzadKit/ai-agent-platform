from app.services.agent_runtime.tools.registry import (
    AgentTool,
    registry,
)


def think_tool(
    objective: str,
    arguments: dict | None = None,
    config=None,
) -> dict:
    return {
        "success": True,
        "type": "thinking",
        "objective": objective,
    }


def finish_tool(
    objective: str,
    arguments: dict | None = None,
    config=None,
) -> dict:
    result = (
        (arguments or {}).get("result")
        or objective
    )

    return {
        "success": True,
        "type": "final",
        "result": result,
    }


def execute_action(
    objective: str,
    arguments: dict | None = None,
    config=None,
) -> str:
    return f"General execution prepared for: {objective}"


def write_content(
    objective: str,
    arguments: dict | None = None,
    config=None,
) -> str:
    return f"Content creation task prepared for: {objective}"


def research_task(
    objective: str,
    arguments: dict | None = None,
    config=None,
) -> str:
    return f"Research task prepared for: {objective}"


def browser_task(
    objective: str,
    arguments: dict | None = None,
    config=None,
) -> str:
    return f"Browser automation task prepared for: {objective}"


def register_core_tools() -> None:

    registry.register(
        AgentTool(
            name="think",
            description="Analyze an objective and determine what should happen next.",
            handler=think_tool,
        )
    )

    registry.register(
        AgentTool(
            name="finish",
            description="Finish the current mission and return the final result.",
            handler=finish_tool,
        )
    )

    registry.register(
        AgentTool(
            name="execute",
            description="Execute a general autonomous action.",
            handler=execute_action,
        )
    )

    registry.register(
        AgentTool(
            name="content_writer",
            description="Create content for a requested task.",
            handler=write_content,
        )
    )

    registry.register(
        AgentTool(
            name="research",
            description="Research and collect information for a task.",
            handler=research_task,
        )
    )

    registry.register(
        AgentTool(
            name="browser",
            description="Perform browser-based automation.",
            handler=browser_task,
        )
    )


register_core_tools()
