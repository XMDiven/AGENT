import pytest

from rag_app.config import config
from rag_app.generation.qa_prompt import get_qa_prompt


def format_prompt_text() -> str:
    prompt = get_qa_prompt()
    messages = prompt.format_messages(
        question="What is RAG?",
        context=(
            "[1]\n"
            "source:data/raw/rag.pdf\n"
            "section_path:page_1\n"
            "page_content:RAG combines retrieval and generation."
        ),
    )

    return "\n".join(str(message.content) for message in messages)


def test_qa_prompt_v1_requires_numbered_citations_without_source_paths(
    monkeypatch,
) -> None:
    monkeypatch.setattr(config, "QA_PROMPT_VERSION", "qa_prompt_v1")

    prompt_text = format_prompt_text()

    assert "Answer in Chinese using only the provided Context" in prompt_text
    assert "Use only citation markers like [1] or [2]" in prompt_text
    assert "Do not include file paths" in prompt_text
    assert "Do not include source, section_path, or page_content labels" in prompt_text


def test_qa_prompt_v2_uses_structured_answer_format(monkeypatch) -> None:
    monkeypatch.setattr(config, "QA_PROMPT_VERSION", "qa_prompt_v2")

    prompt_text = format_prompt_text()

    assert "Use the following exact structure:" in prompt_text
    assert "Direct answer:" in prompt_text
    assert "Key evidence:" in prompt_text
    assert "Limitations:" in prompt_text
    assert "Each bullet must include a citation marker like [1] or [2]" in prompt_text
    assert "Do not include file paths" in prompt_text


def test_qa_prompt_rejects_unknown_prompt_version(monkeypatch) -> None:
    monkeypatch.setattr(config, "QA_PROMPT_VERSION", "unknown_prompt")

    with pytest.raises(ValueError, match="Unsupported QA_PROMPT_VERSION"):
        get_qa_prompt()
