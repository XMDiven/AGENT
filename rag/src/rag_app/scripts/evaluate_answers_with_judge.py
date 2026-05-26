from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from rag_app.config import config
from rag_app.evaluation.answer_judge import judge_answer
from rag_app.infrastructure.llm_client import get_client
from rag_app.scripts.evaluate_retrieval import RetrievalEvalCase, load_case
from rag_app.services.ask_service import ask_question


def build_error_detail(error: Exception) -> dict[str, str]:
    return {
        "error_type": type(error).__name__,
        "error": str(error),
    }


def normalize_sources(sources: Any) -> list[dict[str, Any]]:
    if isinstance(sources, list):
        return [
            source
            for source in sources
            if isinstance(source, dict)
        ]

    return []


def evaluate_case(
    case: RetrievalEvalCase,
    llm: BaseChatModel,
) -> dict[str, Any]:
    try:
        result = ask_question(case.question)
    except Exception as error:
        return {
            "id": case.id,
            "question": case.question,
            "answer": "",
            "sources": [],
            "judge": None,
            "passed": False,
            "failures": ["answer generation failed"],
            "answer_error": build_error_detail(error),
        }

    answer = str(result.get("answer", ""))
    sources = normalize_sources(result.get("sources", []))

    try:
        judge_result = judge_answer(
            question=case.question,
            answer=answer,
            sources=sources,
            llm=llm,
        )
    except Exception as error:
        return {
            "id": case.id,
            "question": case.question,
            "answer": answer,
            "sources": sources,
            "judge": None,
            "passed": False,
            "failures": ["judge failed"],
            "judge_error": build_error_detail(error),
        }

    return {
        "id": case.id,
        "question": case.question,
        "answer": answer,
        "sources": sources,
        "judge": judge_result.model_dump(),
        "passed": judge_result.overall_pass,
        "failures": [],
    }


def save_report(report: dict[str, Any]) -> None:
    output_dir = config.PROJECT_ROOT / "experiments" / "judge_runs"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{report['run_id']}.json"
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"judge report saved to: {output_path}")


def run_evaluation() -> dict[str, Any]:
    cases = load_case()
    llm = get_client()
    results = [
        evaluate_case(case, llm)
        for case in cases
    ]

    passed_count = sum(result["passed"] for result in results)
    total_count = len(results)

    return {
        "run_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "prompt_version": config.QA_PROMPT_VERSION,
        "total": total_count,
        "passed": passed_count,
        "failed": total_count - passed_count,
        "cases": results,
    }


def main() -> None:
    report = run_evaluation()
    save_report(report)


if __name__ == "__main__":
    main()
