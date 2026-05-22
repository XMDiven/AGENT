from agent_app.service import run_agent


def test_run_agent_uses_retrieval_tool(monkeypatch) -> None:
    expected = {
        "answer": "RAG answer",
        "sources": [],
        "trace": [],
    }

    monkeypatch.setattr(
        "agent_app.executor.run_retrieval_tool",
        lambda question: expected,
    )

    result = run_agent("What is RAG?")

    assert result.plan.tool.name == "retrieval_tool"
    assert result.tool_result.tool_name == "retrieval_tool"
    assert result.tool_result.status == "success"
    assert result.tool_result.output == expected

    assert result.trace == [
        {
            "step": "analyze_question",
            "status": "completed",
            "detail": {
                "needs_retrieval": True,
                "question_type": "general",
                "reason": "normal knowledge question, use retrieval",
            },
        },
        {
            "step": "plan_tool",
            "status": "completed",
            "detail": {
                "tool_name": "retrieval_tool",
                "reason": "question requires knowledge retrieval",
            },
        },
        {
            "step": "execute_tool",
            "status": "success",
            "detail": {
                "tool_name": "retrieval_tool",
            },
        },
    ]


def test_run_agent_uses_fallback_tool_when_retrieval_is_not_needed() -> None:
    result = run_agent("")

    assert result.plan.tool.name == "fallback_tool"
    assert result.tool_result.tool_name == "fallback_tool"
    assert result.tool_result.status == "success"
    assert result.tool_result.output == {
        "answer": "No retrieval is needed for this question.",
        "sources": [],
    }
    assert result.trace == [
        {
            "step": "analyze_question",
            "status": "completed",
            "detail": {
                "needs_retrieval": False,
                "question_type": "empty",
                "reason": "empty question",
            },
        },
        {
            "step": "plan_tool",
            "status": "completed",
            "detail": {
                "tool_name": "fallback_tool",
                "reason": "question does not require retrieval",
            },
        },
        {
            "step": "execute_tool",
            "status": "success",
            "detail": {
                "tool_name": "fallback_tool",
            },
        },
    ]


def test_run_agent_uses_summary_tool_for_summary_question() -> None:
    result = run_agent("请总结 LangChain 的用途")

    assert result.plan.tool.name == "summary_tool"
    assert result.tool_result.tool_name == "summary_tool"
    assert result.tool_result.status == "success"
    assert result.tool_result.output == {
        "summary": "请总结 LangChain 的用途",
    }
    assert result.trace == [
        {
            "step": "analyze_question",
            "status": "completed",
            "detail": {
                "needs_retrieval": True,
                "question_type": "summary",
                "reason": "summary question, use retrieval",
            },
        },
        {
            "step": "plan_tool",
            "status": "completed",
            "detail": {
                "tool_name": "summary_tool",
                "reason": "question asks for summarization",
            },
        },
        {
            "step": "execute_tool",
            "status": "success",
            "detail": {
                "tool_name": "summary_tool",
            },
        },
    ]


def test_run_agent_marks_trace_failed_when_retrieval_tool_fails(
    monkeypatch,
) -> None:
    def raise_error(question: str) -> None:
        raise RuntimeError("rag unavailable")

    monkeypatch.setattr(
        "agent_app.executor.run_retrieval_tool",
        raise_error,
    )

    result = run_agent("What is RAG?")

    assert result.tool_result.status == "failed"
    assert result.tool_result.output == {
        "error_type": "RuntimeError",
        "error": "rag unavailable",
    }
    assert result.trace[-1] == {
        "step": "execute_tool",
        "status": "failed",
        "detail": {
            "tool_name": "retrieval_tool",
        },
    }
