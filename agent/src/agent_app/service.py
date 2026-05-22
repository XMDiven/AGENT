from dataclasses import dataclass
from typing import Any

from rag_app.retrieval.query_analyzer import analyze_query

from agent_app.executor import ToolResult, execute_plan
from agent_app.planner import AgentPlan, plan_tool
from agent_app.state import AgentState


@dataclass(frozen=True)
class AgentRunResult:
    plan: AgentPlan
    tool_result: ToolResult
    trace: list[dict[str, Any]]


def run_agent(question: str) -> AgentRunResult:
    analysis = analyze_query(question)

    plan = plan_tool(question_type=analysis.question_type)

    tool_result = execute_plan(
        plan=plan,
        tool_input={
            "question": question,
            "text": question,
        },
    )

    trace = [
        {
            "step": "analyze_question",
            "status": "completed",
            "detail": {
                "needs_retrieval": analysis.needs_retrieval,
                "question_type": analysis.question_type,
                "reason": analysis.reason,
            },
        },
        {
            "step": "plan_tool",
            "status": "completed",
            "detail": {
                "tool_name": plan.tool.name,
                "reason": plan.reason,
            },
        },
        {
            "step": "execute_tool",
            "status": tool_result.status,
            "detail": {
                "tool_name": tool_result.tool_name,
            },
        },
    ]

    state = AgentState(
        question=question,
        analysis=analysis,
        plan=plan,
        tool_result=tool_result,
        trace=trace,
    )

    return AgentRunResult(
        plan=state.plan,
        tool_result=state.tool_result,
        trace=state.trace,
    )
