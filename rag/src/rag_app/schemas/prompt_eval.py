from pydantic import BaseModel, Field


class PromptEvalRunRequest(BaseModel):
    prompt_version: str = "qa_prompt_v2"
    case_limit: int | None = Field(default=None, ge=1)


class PromptEvalRunResponse(BaseModel):
    run_id: str
    prompt_version: str
    status: str
    total: int
    passed: int
    failed: int
    report_url: str
