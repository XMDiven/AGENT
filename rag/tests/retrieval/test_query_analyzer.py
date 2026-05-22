from rag_app.retrieval.query_analyzer import analyze_query


def test_analyze_query_classifies_empty_question() -> None:
    result = analyze_query("   ")

    assert result.original_question == "   "
    assert result.normalized_question == ""
    assert result.needs_retrieval is False
    assert result.reason == "empty question"
    assert result.question_type == "empty"


def test_analyze_query_classifies_general_question() -> None:
    result = analyze_query("Qdrant 是什么？")

    assert result.original_question == "Qdrant 是什么？"
    assert result.normalized_question == "Qdrant 是什么？"
    assert result.needs_retrieval is True
    assert result.reason == "normal knowledge question, use retrieval"
    assert result.question_type == "general"


def test_analyze_query_classifies_comparison_question() -> None:
    result = analyze_query("LangChain 和 LlamaIndex 分别适合做什么？")

    assert result.original_question == "LangChain 和 LlamaIndex 分别适合做什么？"
    assert result.normalized_question == "LangChain 和 LlamaIndex 分别适合做什么？"
    assert result.needs_retrieval is True
    assert result.reason == "comparison question, use retrieval"
    assert result.question_type == "comparison"


def test_analyze_query_classifies_summary_question() -> None:
    result = analyze_query("请总结 LangChain 的用途")

    assert result.original_question == "请总结 LangChain 的用途"
    assert result.normalized_question == "请总结 LangChain 的用途"
    assert result.needs_retrieval is True
    assert result.reason == "summary question, use retrieval"
    assert result.question_type == "summary"
