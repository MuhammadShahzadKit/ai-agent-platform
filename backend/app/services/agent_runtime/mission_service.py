from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.services.agent_runtime import (
    AgentRuntime,
    AgentRuntimeConfig,
)


def create_runtime_for_agent(
    agent: Agent,
) -> AgentRuntime:

    config = AgentRuntimeConfig(

        max_steps=10,

        allow_browser=True,

        allow_file_access=True,

        allow_document_search=getattr(
            agent,
            "use_rag",
            False,
        ),

        allow_scheduling=True,

        allow_tool_execution=True,

        require_confirmation_for_destructive_actions=True,

        memory_enabled=True,

        metadata={
            "agent_id": agent.id,
            "agent_name": agent.name,
        },
    )

    return AgentRuntime(
        config=config
    )


def run_agent_mission(
    db: Session,
    agent: Agent,
    objective: str,
):

    runtime = create_runtime_for_agent(
        agent
    )

    return runtime.run(
        objective=objective,
        agent_instructions=agent.system_prompt,
    )
