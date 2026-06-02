from agent_app.tools.question_decompose import (
    has_decomposition_signal,
    run_question_decompose_tool,
)


def test_has_decomposition_signal_for_explicit_multi_part_question() -> None:
    assert has_decomposition_signal("LangChain 和 LlamaIndex 分别适合做什么？")


def test_has_decomposition_signal_for_english_comparison_question() -> None:
    assert has_decomposition_signal("Compare LangChain vs LlamaIndex.")


def test_has_decomposition_signal_returns_false_for_single_question() -> None:
    assert not has_decomposition_signal("What is LangChain used for?")


def test_run_question_decompose_tool_splits_explicit_multi_part_question() -> None:
    result = run_question_decompose_tool(
        "LangChain 和 LlamaIndex 分别适合做什么？"
    )

    assert result == {
        "sub_questions": [
            "LangChain 适合做什么？",
            "LlamaIndex 适合做什么？",
        ],
        "reason": "question contains explicit multi-part intent",
        "decomposition_strategy": "comparison",
    }


def test_run_question_decompose_tool_returns_empty_result_for_empty_question() -> None:
    result = run_question_decompose_tool("   ")

    assert result == {
        "sub_questions": [],
        "reason": "empty question",
        "decomposition_strategy": "none",
    }


def test_run_question_decompose_tool_keeps_question_when_split_is_unsafe() -> None:
    result = run_question_decompose_tool("Compare LangChain vs LlamaIndex.")

    assert result == {
        "sub_questions": ["Compare LangChain vs LlamaIndex."],
        "reason": "question contains comparison intent but no safe split pattern",
        "decomposition_strategy": "comparison",
    }
