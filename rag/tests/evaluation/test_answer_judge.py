import pytest
from pydantic import ValidationError

from rag_app.evaluation.answer_judge import (
    format_evidence,
    parse_judge_result,
    strip_json_markdown,
)
from rag_app.evaluation.judge_schema import AnswerJudgeResult


def test_format_evidence_includes_source_section_and_snippet() -> None:
    evidence = format_evidence(
        [
            {
                "source": "data/raw/qdrant-docs.md",
                "section_path": "overview",
                "snippet": "Qdrant is a vector database.",
            }
        ]
    )

    assert "[1]" in evidence
    assert "data/raw/qdrant-docs.md" in evidence
    assert "overview" in evidence
    assert "Qdrant is a vector database." in evidence


def test_format_evidence_returns_placeholder_when_sources_are_empty() -> None:
    assert format_evidence([]) == "No retrieved evidence."


def test_strip_json_markdown_removes_fenced_code_block() -> None:
    raw_output = """
```json
{"overall_pass": true}
```
"""

    assert strip_json_markdown(raw_output) == '{"overall_pass": true}'


def test_parse_judge_result_parses_valid_json() -> None:
    result = parse_judge_result(
        """
{
  "relevance_score": 5,
  "completeness_score": 4,
  "groundedness_score": 5,
  "format_score": 4,
  "overall_pass": true,
  "feedback": "The answer is relevant and grounded."
}
"""
    )

    assert result.relevance_score == 5
    assert result.overall_pass is True


def test_answer_judge_result_rejects_score_outside_valid_range() -> None:
    with pytest.raises(ValidationError):
        AnswerJudgeResult(
            relevance_score=6,
            completeness_score=4,
            groundedness_score=4,
            format_score=4,
            overall_pass=True,
            feedback="invalid score",
        )


def test_answer_judge_result_overrides_pass_when_any_score_is_low() -> None:
    result = AnswerJudgeResult(
        relevance_score=5,
        completeness_score=3,
        groundedness_score=5,
        format_score=5,
        overall_pass=True,
        feedback="completeness is weak",
    )

    assert result.overall_pass is False
