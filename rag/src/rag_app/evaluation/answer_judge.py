from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from rag_app.evaluation.judge_prompt import get_answer_judge_prompt
from rag_app.evaluation.judge_schema import AnswerJudgeResult


def format_evidence(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "No retrieved evidence."

    evidence_items: list[str] = []

    for index, source in enumerate(sources, start=1):
        evidence_items.append(
            "\n".join(
                [
                    f"[{index}]",
                    f"source: {source.get('source', 'unknown')}",
                    f"section_path: {source.get('section_path', 'unknown')}",
                    f"snippet: {source.get('snippet', '')}",
                ]
            )
        )

    return "\n\n".join(evidence_items)


def strip_json_markdown(text: str) -> str:
    stripped = text.strip()

    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()


def parse_judge_result(raw_output: str) -> AnswerJudgeResult:
    return AnswerJudgeResult.model_validate_json(
        strip_json_markdown(raw_output)
    )


def judge_answer(
    question: str,
    answer: str,
    sources: list[dict[str, Any]],
    llm: BaseChatModel,
) -> AnswerJudgeResult:
    judge_prompt = get_answer_judge_prompt()
    chain = judge_prompt | llm | StrOutputParser()

    raw_output = chain.invoke(
        {
            "question": question,
            "answer": answer,
            "evidence": format_evidence(sources),
        }
    )

    return parse_judge_result(raw_output)
