from dataclasses import dataclass
from typing import Any

from agent_app.executor import ToolResult, execute_plan
from agent_app.planner import AgentPlan, plan_tool


@dataclass(frozen=True)
class AgentRunResult:
    plan: AgentPlan
    tool_result: ToolResult


def run_agent(question: str, needs_retrieval: bool) -> AgentRunResult:
    plan = plan_tool(needs_retrieval=needs_retrieval)

    tool_result = execute_plan(
        plan=plan,
        tool_input={
            "question": question,
        },
    )

    return AgentRunResult(
        plan=plan,
        tool_result=tool_result,
    )

