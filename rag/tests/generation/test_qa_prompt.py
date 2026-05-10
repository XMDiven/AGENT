from src.generation.qa_prompt import get_qa_prompt


def test_qa_prompt_requires_numbered_citations_without_source_paths() -> None:
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

    prompt_text = "\n".join(str(message.content) for message in messages)

    assert "Use only citation markers like [1] or [2]" in prompt_text
    assert "Do not include file paths" in prompt_text
    assert "Do not include source, section_path, or page_content labels" in prompt_text
