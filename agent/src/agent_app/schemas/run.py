from typing import Any

from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    question: str


class AgentRunResponse(BaseModel):
    plan: dict[str, Any]
    tool_result: dict[str, Any]
    trace: list[dict[str, Any]]
