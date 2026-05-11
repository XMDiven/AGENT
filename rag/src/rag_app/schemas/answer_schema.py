from typing import Any

from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    source: str
    section_path: str
    snippet: str


class TraceItem(BaseModel):
    step: str
    status: str
    detail: dict[str, Any] = Field(default_factory=dict)


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    trace: list[TraceItem]
