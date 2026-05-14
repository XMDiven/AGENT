from typing import Any

from langchain_core.documents import Document

from rag_app.config import config
from rag_app.generation.answer_generator import generate_answer
from rag_app.generation.context_formatter import format_context
from rag_app.generation.qa_prompt import get_qa_prompt
from rag_app.infrastructure.llm_client import get_client
from rag_app.retrieval.query_analyzer import analyze_query
from rag_app.retrieval.retriever import get_retriever


def interleave_documents_by_source(documents: list[Document]) -> list[Document]:
    documents_by_source: dict[str, list[Document]] = {}
    source_order: list[str] = []

    for document in documents:
        source = str(document.metadata.get("source", "unknown"))

        if source not in documents_by_source:
            documents_by_source[source] = []
            source_order.append(source)

        documents_by_source[source].append(document)

    reordered_documents: list[Document] = []

    while len(reordered_documents) < len(documents):
        added_document = False

        for source in source_order:
            source_documents = documents_by_source[source]

            if source_documents:
                reordered_documents.append(source_documents.pop(0))
                added_document = True

        if not added_document:
            break

    return reordered_documents


def apply_retrieval_strategy(
    documents: list[Document],
    retrieval_strategy: str,
) -> list[Document]:
    if retrieval_strategy == "skip_retrieval":
        return []

    if retrieval_strategy == "standard_retrieval":
        return documents

    if retrieval_strategy == "comparison_retrieval":
        return interleave_documents_by_source(documents)

    return documents


def build_retrieved_sources(documents: list[Document]) -> list[str]:
    sources: list[str] = []

    for document in documents:
        source = str(document.metadata.get("source", "unknown"))
        if source not in sources:
            sources.append(source)
    return sources


def build_trace_item(
    step: str,
    status: str = "completed",
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "step": step,
        "status": status,
        "detail": detail or {},
    }


def plan_retrieval(question_type: str) -> dict[str, str]:
    if question_type == "empty":
        return {
            "retrieval_strategy": "skip_retrieval",
            "reason": "empty questions do not need retrieval",
        }

    if question_type == "comparison":
        return {
            "retrieval_strategy": "comparison_retrieval",
            "reason": "comparison questions may need evidence from multiple sources",
        }

    return {
        "retrieval_strategy": "standard_retrieval",
        "reason": "general knowledge questions use standard retrieval",
    }


def build_sources(documents: list[Document]) -> list[dict[str, str]]:
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


def ask_question(question: str) -> dict[str, Any]:
    trace: list[dict[str, Any]] = []
    analysis = analyze_query(question)

    trace.append(
        build_trace_item(
            step="query_analysis",
            status="completed",
            detail={
                "normalized_question": analysis.normalized_question,
                "needs_retrieval": analysis.needs_retrieval,
                "reason": analysis.reason,
                "question_type": analysis.question_type,
            },
        )
    )

    retrieval_plan = plan_retrieval(analysis.question_type)

    trace.append(
        build_trace_item(
            step="retrieval_planning",
            status="completed",
            detail={
                "question_type": analysis.question_type,
                **retrieval_plan,
            },
        )
    )

    if not analysis.needs_retrieval:
        trace.append(
            build_trace_item(
                step="retrieval",
                status="skipped",
                detail={
                    "retrieval_strategy": retrieval_plan["retrieval_strategy"],
                    "reason": analysis.reason,
                },
            )
        )

        return {
            "answer": config.FALLBACK_ANSWER,
            "sources": [],
            "trace": trace,
        }

    retriever = get_retriever()
    documents = retriever.invoke(analysis.normalized_question)

    documents = apply_retrieval_strategy(
        documents=documents,
        retrieval_strategy=retrieval_plan["retrieval_strategy"],
    )

    trace.append(
        build_trace_item(
            step="retrieval",
            detail={
                "retrieval_strategy": retrieval_plan["retrieval_strategy"],
                "top_k": config.RETRIEVAL_TOP_K,
                "document_count": len(documents),
                "retrieved_sources": build_retrieved_sources(documents),
            },
        )
    )

    if not documents:
        return {
            "answer": config.FALLBACK_ANSWER,
            "sources": [],
            "trace": trace,
        }

    context = format_context(documents)
    llm = get_client()
    prompt = get_qa_prompt()
    answer = generate_answer(
        question=analysis.normalized_question,
        context=context,
        prompt=prompt,
        llm=llm,
    )

    trace.append(build_trace_item(step="generate_answer"))

    return {
        "answer": answer,
        "sources": build_sources(documents),
        "trace": trace,
    }
