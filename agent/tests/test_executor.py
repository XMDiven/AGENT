from agent_app.executor import execute_plan
from agent_app.planner import AgentPlan
from agent_app.tools import ToolDefinition, get_tool


def test_execute_plan_returns_not_implemented_for_retrieval_tool() -> None:
    plan = AgentPlan(
        tool=get_tool("retrieval_tool"),
        reason="question requires knowledge retrieval",
    )

    result = execute_plan(plan)

    assert result.tool_name == "retrieval_tool"
    assert result.status == "not_implemented"
    assert result.output == {
        "reason": "retrieval_tool is registered but not wired to RAG yet",
    }


def test_execute_plan_runs_fallback_tool() -> None:
    plan = AgentPlan(
        tool=get_tool("fallback_tool"),
        reason="question does not require retrieval",
    )

    result = execute_plan(plan)

    assert result.tool_name == "fallback_tool"
    assert result.status == "success"
    assert result.output == {
        "answer": "No retrieval is needed for this question.",
        "sources": [],
    }


def test_execute_plan_returns_failed_result_for_unsupported_tool() -> None:
    plan = AgentPlan(
        tool=ToolDefinition(
            name="unknown_tool",
            description="Unknown tool.",
        ),
        reason="unsupported test case",
    )

    result = execute_plan(plan)

    assert result.tool_name == "unknown_tool"
    assert result.status == "failed"
    assert result.output == {
        "error": "Unsupported tool: unknown_tool",
    }