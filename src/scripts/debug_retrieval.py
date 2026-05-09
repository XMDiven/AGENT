from __future__ import  annotations

import sys

from langchain_core.documents import Document

from src.retrieval.retriever import get_retriever

def build_snippet(document: Document, limit: int = 300) -> str:
    text = document.page_content.replace("\n", " ").strip()

    if len(text) <= limit:
        return text

    return f"{text[:limit]}..."

def print_document(index: int, document: Document) -> None:
    metadata = document.metadata

    print(f"[{index}]")
    print(f"source: {metadata.get('source', 'unknown')}")
    print(f"section_path: {metadata.get('section_path', 'unknown')}")
    print(f"snippet: {build_snippet(document)}")
    print()



def debug_retrieval(question : str):
    retriever = get_retriever()
    documents = retriever.invoke(question)

    print(f"question: {question}")
    print(f"retrieved_count: {len(documents)}")
    print()
    for index, document in enumerate(documents, start=1):
        print_document(index, document)

    return documents
def main():
    if len(sys.argv) < 2:
        print('Usage: python -m src.scripts.debug_retrieval "your question"')
        raise SystemExit(1)
    question = " ".join(sys.argv[1:]).strip()
    debug_retrieval(question)

if "__main__" == __name__:
    main()