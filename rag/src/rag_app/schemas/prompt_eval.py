from pydantic import BaseModel, Field


class PromptEvalCaseRequest(BaseModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)


class PromptEvalRunRequest(BaseModel):
    prompt_version: str = "qa_prompt_v2"
    case_limit: int | None = Field(default=None, ge=1)
    cases: list[PromptEvalCaseRequest] | None = Field(
        default=None,
        min_length=1,
        max_length=10,
    )


class PromptEvalRunResponse(BaseModel):
    run_id: str
    prompt_version: str
    status: str
    total: int
    passed: int
    failed: int
    report_url: str
