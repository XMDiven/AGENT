from collections.abc import Iterator
from typing import Any

from langchain_core.documents import Document

from rag_app.config import config
from rag_app.generation.answer_generator import generate_answer, stream_answer
from rag_app.generation.context_formatter import format_context
from rag_app.generation.qa_prompt import get_qa_prompt
from rag_app.infrastructure.llm_client import get_client
from rag_app.retrieval.query_analyzer import analyze_query
from rag_app.retrieval.retriever import get_retriever
from rag_app.retrieval.retrieval_planner import plan_retrieval


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

    retrieval_plan = plan_retrieval(analysis)

    trace.append(
        build_trace_item(
            step="retrieval_planning",
            status="completed",
            detail={
                "question_type": analysis.question_type,
                "retrieval_strategy": retrieval_plan.retrieval_strategy,
                "retrieval_query": retrieval_plan.retrieval_query,
                "top_k": retrieval_plan.top_k,
                "reason": retrieval_plan.reason,
            },
        )
    )

    if not analysis.needs_retrieval:
        trace.append(
            build_trace_item(
                step="retrieval",
                status="skipped",
                detail={
                    "retrieval_strategy": retrieval_plan.retrieval_strategy,
                    "retrieval_query": retrieval_plan.retrieval_query,
                    "top_k": retrieval_plan.top_k,
                    "reason": retrieval_plan.reason,
                },
            )
        )

        return {
            "answer": config.FALLBACK_ANSWER,
            "sources": [],
            "trace": trace,
        }

    retriever = get_retriever(top_k=retrieval_plan.top_k)
    documents = retriever.invoke(retrieval_plan.retrieval_query)

    documents = apply_retrieval_strategy(
        documents=documents,
        retrieval_strategy=retrieval_plan.retrieval_strategy,
    )

    trace.append(
        build_trace_item(
            step="retrieval",
            detail={
                "retrieval_strategy": retrieval_plan.retrieval_strategy,
                "retrieval_query": retrieval_plan.retrieval_query,
                "top_k": retrieval_plan.top_k,
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

    max_attempts = config.MAX_GENERATION_RETRY + 1
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            context = format_context(documents)
            llm = get_client()
            prompt = get_qa_prompt()
            answer = generate_answer(
                question=analysis.normalized_question,
                context=context,
                prompt=prompt,
                llm=llm,
            )

            trace.append(
                build_trace_item(
                    step="generate_answer",
                    status="completed",
                    detail={"attempt": attempt},
                )
            )

            return {
                "answer": answer,
                "sources": build_sources(documents),
                "trace": trace,
            }

        except Exception as exc:
            last_error = exc
            if attempt < max_attempts:
                trace.append(
                    build_trace_item(
                        step="generate_answer",
                        status="retrying",
                        detail={
                            "attempt": attempt,
                            "error_type": type(exc).__name__,
                        },
                    )
                )

    if last_error is not None:
        trace.append(
            build_trace_item(
                step="generate_answer",
                status="failed",
                detail={
                    "attempts": max_attempts,
                    "error_type": type(last_error).__name__,
                },
            )
        )

    return {
        "answer": config.FALLBACK_ANSWER,
        "sources": build_sources(documents),
        "trace": trace,
    }


def stream_ask_question(question: str) -> Iterator[dict[str, Any]]:
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

    retrieval_plan = plan_retrieval(analysis)

    trace.append(
        build_trace_item(
            step="retrieval_planning",
            status="completed",
            detail={
                "question_type": analysis.question_type,
                "retrieval_strategy": retrieval_plan.retrieval_strategy,
                "retrieval_query": retrieval_plan.retrieval_query,
                "top_k": retrieval_plan.top_k,
                "reason": retrieval_plan.reason,
            },
        )
    )

    if not analysis.needs_retrieval:
        trace.append(
            build_trace_item(
                step="retrieval",
                status="skipped",
                detail={
                    "retrieval_strategy": retrieval_plan.retrieval_strategy,
                    "retrieval_query": retrieval_plan.retrieval_query,
                    "top_k": retrieval_plan.top_k,
                    "reason": retrieval_plan.reason,
                },
            )
        )

        yield {"type": "answer_delta", "content": config.FALLBACK_ANSWER}
        yield {"type": "sources", "sources": []}
        yield {"type": "trace", "trace": trace}
        yield {"type": "done"}
        return

    retriever = get_retriever(top_k=retrieval_plan.top_k)
    documents = retriever.invoke(retrieval_plan.retrieval_query)

    documents = apply_retrieval_strategy(
        documents=documents,
        retrieval_strategy=retrieval_plan.retrieval_strategy,
    )

    trace.append(
        build_trace_item(
            step="retrieval",
            detail={
                "retrieval_strategy": retrieval_plan.retrieval_strategy,
                "retrieval_query": retrieval_plan.retrieval_query,
                "top_k": retrieval_plan.top_k,
                "document_count": len(documents),
                "retrieved_sources": build_retrieved_sources(documents),
            },
        )
    )

    if not documents:
        yield {"type": "answer_delta", "content": config.FALLBACK_ANSWER}
        yield {"type": "sources", "sources": []}
        yield {"type": "trace", "trace": trace}
        yield {"type": "done"}
        return

    try:
        context = format_context(documents)
        llm = get_client()
        prompt = get_qa_prompt()

        for chunk in stream_answer(
            question=analysis.normalized_question,
            context=context,
            prompt=prompt,
            llm=llm,
        ):
            yield {
                "type": "answer_delta",
                "content": chunk,
            }

        trace.append(
            build_trace_item(
                step="generate_answer",
                status="completed",
                detail={"streaming": True},
            )
        )

        yield {"type": "sources", "sources": build_sources(documents)}
        yield {"type": "trace", "trace": trace}
        yield {"type": "done"}
        return

    except Exception as exc:
        trace.append(
            build_trace_item(
                step="generate_answer",
                status="failed",
                detail={
                    "streaming": True,
                    "error_type": type(exc).__name__,
                },
            )
        )

        yield {
            "type": "error",
            "error_type": type(exc).__name__,
            "message": config.FALLBACK_ANSWER,
        }
        yield {"type": "sources", "sources": build_sources(documents)}
        yield {"type": "trace", "trace": trace}
        yield {"type": "done"}
        return
