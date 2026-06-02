from agent_app.orchestration.executor import execute_plan
from agent_app.orchestration.planner import AgentPlan
from agent_app.tools.registry import ToolDefinition, get_tool


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
        "agent_app.orchestration.executor.run_retrieval_tool",
        lambda question: expected,
    )

    result = execute_plan(
        plan,
        tool_input={"question": "What is RAG?"},
    )

    assert result.tool_name == "retrieval_tool"
    assert result.status == "success"
    assert result.output == expected
    assert result.attempts == [
        {
            "attempt": 1,
            "status": "success",
        }
    ]


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
    assert result.attempts == [
        {
            "attempt": 1,
            "status": "success",
        }
    ]


def test_execute_plan_runs_summary_tool() -> None:
    plan = AgentPlan(
        tool=get_tool("summary_tool"),
        reason="question asks for summarization",
    )

    result = execute_plan(
        plan,
        tool_input={"text": "  LangChain   helps build LLM apps.  "},
    )

    assert result.tool_name == "summary_tool"
    assert result.status == "success"
    assert result.output == {
        "summary": "LangChain helps build LLM apps.",
    }
    assert result.attempts == [
        {
            "attempt": 1,
            "status": "success",
        }
    ]


def test_execute_plan_runs_question_decompose_tool() -> None:
    plan = AgentPlan(
        tool=get_tool("question_decompose_tool"),
        reason="question contains comparison or multi-part intent",
    )

    result = execute_plan(
        plan,
        tool_input={
            "question": "LangChain 和 LlamaIndex 分别适合做什么？",
        },
    )

    assert result.tool_name == "question_decompose_tool"
    assert result.status == "success"
    assert result.output == {
        "sub_questions": [
            "LangChain 适合做什么？",
            "LlamaIndex 适合做什么？",
        ],
        "reason": "question contains explicit multi-part intent",
        "decomposition_strategy": "comparison",
    }
    assert result.attempts == [
        {
            "attempt": 1,
            "status": "success",
        }
    ]


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
    assert result.attempts == [
        {
            "attempt": 1,
            "status": "failed",
            "error": "Unsupported tool: unknown_tool",
        }
    ]


def test_execute_plan_retries_retrieval_tool_until_success(monkeypatch) -> None:
    plan = AgentPlan(
        tool=get_tool("retrieval_tool"),
        reason="question requires knowledge retrieval",
    )
    expected = {
        "answer": "RAG answer",
        "sources": [],
        "trace": [],
    }
    calls = {"count": 0}

    def flaky_retrieval_tool(question: str) -> dict:
        calls["count"] += 1

        if calls["count"] == 1:
            raise RuntimeError("temporary rag error")

        return expected

    monkeypatch.setattr(
        "agent_app.orchestration.executor.run_retrieval_tool",
        flaky_retrieval_tool,
    )

    result = execute_plan(
        plan,
        tool_input={"question": "What is RAG?"},
        max_attempts=3,
    )

    assert result.tool_name == "retrieval_tool"
    assert result.status == "success"
    assert result.output == expected
    assert result.attempts == [
        {
            "attempt": 1,
            "status": "failed",
            "error_type": "RuntimeError",
            "error": "temporary rag error",
        },
        {
            "attempt": 2,
            "status": "success",
        },
    ]
    assert calls["count"] == 2


def test_execute_plan_returns_failed_result_when_retrieval_tool_fails(
    monkeypatch,
) -> None:
    plan = AgentPlan(
        tool=get_tool("retrieval_tool"),
        reason="question requires knowledge retrieval",
    )

    def raise_error(question: str) -> None:
        raise RuntimeError("rag unavailable")

    monkeypatch.setattr(
        "agent_app.orchestration.executor.run_retrieval_tool",
        raise_error,
    )

    result = execute_plan(
        plan,
        tool_input={"question": "What is RAG?"},
    )

    assert result.tool_name == "retrieval_tool"
    assert result.status == "failed"
    assert result.output == {
        "error_type": "RuntimeError",
        "error": "rag unavailable",
    }
    assert result.attempts == [
        {
            "attempt": 1,
            "status": "failed",
            "error_type": "RuntimeError",
            "error": "rag unavailable",
        },
        {
            "attempt": 2,
            "status": "failed",
            "error_type": "RuntimeError",
            "error": "rag unavailable",
        },
        {
            "attempt": 3,
            "status": "failed",
            "error_type": "RuntimeError",
            "error": "rag unavailable",
        },
    ]
