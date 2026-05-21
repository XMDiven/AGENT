from agent_app.executor import execute_plan
from agent_app.planner import AgentPlan
from agent_app.tools import ToolDefinition, get_tool


def test_execute_plan_runs_retrieval_tool(monkeypatch) -> None:
    plan = AgentPlan(
        tool=get_tool("retrieval_tool"),
        reason="question requires knowledge retrieval",
    )

    expected = {
        "answer": "RAG answer",
        "sources": [],
        "trace": [],
    }

    monkeypatch.setattr(
        "agent_app.executor.run_retrieval_tool",
        lambda question: expected,
    )

    result = execute_plan(
        plan,
        tool_input={"question": "What is RAG?"},
    )

    assert result.tool_name == "retrieval_tool"
    assert result.status == "success"
    assert result.output == expected


def test_execute_plan_runs_fallback_tool() -> None:
    plan = AgentPlan(
        tool=get_tool("fallback_tool"),
        reason="question does not require retrieval",
    )

    result = execute_plan(plan, tool_input={})

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

    result = execute_plan(plan, tool_input={})

    assert result.tool_name == "unknown_tool"
    assert result.status == "failed"
    assert result.output == {
        "error": "Unsupported tool: unknown_tool",
    }
