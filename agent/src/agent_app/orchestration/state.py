from dataclasses import dataclass
from typing import Any

from agent_app.orchestration.executor import ToolResult
from agent_app.orchestration.planner import AgentPlan


@dataclass(frozen=True)
class AgentState:
    question: str
    analysis: Any
    plan: AgentPlan
    tool_result: ToolResult
    trace: list[dict[str, Any]]
