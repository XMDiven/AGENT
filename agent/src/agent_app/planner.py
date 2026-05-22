from dataclasses import dataclass

from agent_app.tools import ToolDefinition, get_tool


@dataclass(frozen=True)
class AgentPlan:
    tool: ToolDefinition
    reason: str


def plan_tool(question_type: str) -> AgentPlan:
    if question_type == "empty":
        return AgentPlan(
            tool=get_tool("fallback_tool"),
            reason="question does not require retrieval",
        )

    if question_type == "summary":
        return AgentPlan(
            tool=get_tool("summary_tool"),
            reason="question asks for summarization",
        )

    return AgentPlan(
        tool=get_tool("retrieval_tool"),
        reason="question requires knowledge retrieval",
    )
