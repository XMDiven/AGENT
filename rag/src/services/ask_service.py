from langchain_core.documents import Document
from src.generation.answer_generator import generate_answer

from src.generation.context_formatter import format_context
from src.infrastructure.llm_client import get_client
from src.retrieval.retriever import get_retriever
from src.generation.qa_prompt import get_qa_prompt

from config import config
def build_sources(documents : list[Document]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []

    for doc in documents:
        sources.append(
            {
                "source": doc.metadata.get("source", "unknown"),
                "section_path": doc.metadata.get("section_path", "unknown"),
                "snippet": doc.page_content[:config.CHUNK_SIZE],
            }
        )

    return sources
def ask_question(question: str) -> dict[str, str | list[dict[str, str]]]:
    retriever = get_retriever()
    documents = retriever.invoke(question)
    if not documents:
        return {
            "answer": config.FALLBACK_ANSWER,
            "sources": [],
        }

    context = format_context(documents)
    llm = get_client()
    prompt = get_qa_prompt()
    answers = generate_answer(
        question=question,
        context=context,
        prompt=prompt,
        llm=llm,

    )
    return {
        "answer": answers,
        "sources": build_sources(documents),
    }
