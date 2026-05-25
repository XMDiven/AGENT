from __future__ import annotations

import sys

from langchain_core.documents import Document

from rag_app.config import config
from rag_app.infrastructure.vector_store import get_vector_store

SearchResult = tuple[Document, float]


def build_snippet(document: Document, limit: int = 300) -> str:
    text = document.page_content.replace("\n", " ").strip()

    if len(text) <= limit:
        return text

    return f"{text[:limit]}..."


def print_result(index: int, document: Document, score: float) -> None:
    metadata = document.metadata

    print(f"[{index}]")
    print(f"score: {score}")
    print(f"source: {metadata.get('source', 'unknown')}")
    print(f"section_path: {metadata.get('section_path', 'unknown')}")
    print(f"snippet: {build_snippet(document)}")
    print()


def debug_retrieval(question: str) -> list[SearchResult]:
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score(
        question,
        k=config.RETRIEVAL_TOP_K,
    )

    print(f"question: {question}")
    print(f"top_k: {config.RETRIEVAL_TOP_K}")
    print(f"retrieved_count: {len(results)}")
    print()

    for index, (document, score) in enumerate(results, start=1):
        print_result(index, document, score)

    return results


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m rag_app.scripts.debug_retrieval "your question"')
        raise SystemExit(1)

    question = " ".join(sys.argv[1:]).strip()
    debug_retrieval(question)


if "__main__" == __name__:
    main()
