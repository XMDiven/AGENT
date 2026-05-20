from dataclasses import dataclass

from agent_app.tools import ToolDefinition, get_tool


@dataclass(frozen=True)
class AgentPlan:
    tool: ToolDefinition
    reason: str


def plan_tool(needs_retrieval: bool) -> AgentPlan:
    if needs_retrieval:
        return AgentPlan(
            tool=get_tool("retrieval_tool"),
            reason="question requires knowledge retrieval",
        )

    return AgentPlan(
        tool=get_tool("fallback_tool"),
        reason="question does not require retrieval",
    )
