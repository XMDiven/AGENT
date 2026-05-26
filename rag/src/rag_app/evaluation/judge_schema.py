from typing import Self

from pydantic import BaseModel, Field, model_validator


PASSING_SCORE_THRESHOLD = 4


class AnswerJudgeResult(BaseModel):
    relevance_score: int = Field(ge=1, le=5)
    completeness_score: int = Field(ge=1, le=5)
    groundedness_score: int = Field(ge=1, le=5)
    format_score: int = Field(ge=1, le=5)
    overall_pass: bool
    feedback: str

    def scores_pass(self) -> bool:
        return all(
            score >= PASSING_SCORE_THRESHOLD
            for score in (
                self.relevance_score,
                self.completeness_score,
                self.groundedness_score,
                self.format_score,
            )
        )

    @model_validator(mode="after")
    def enforce_overall_pass_rule(self) -> Self:
        self.overall_pass = self.scores_pass()
        return self
