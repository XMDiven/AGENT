from typing import Any

from fastapi import APIRouter, HTTPException

from rag_app.schemas.prompt_eval import (
    PromptEvalRunRequest,
    PromptEvalRunResponse,
)
from rag_app.services import prompt_eval_service

router = APIRouter(prefix="/prompt-evals", tags=["prompt-evals"])


@router.get("/reports")
def list_prompt_eval_reports() -> list[dict[str, Any]]:
    return prompt_eval_service.list_reports()


@router.get("/reports/{run_id}")
def get_prompt_eval_report(run_id: str) -> dict[str, Any]:
    try:
        return prompt_eval_service.load_report(run_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/comparison/latest")
def get_latest_prompt_comparison() -> dict[str, Any]:
    try:
        return prompt_eval_service.get_latest_comparison()
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/run", response_model=PromptEvalRunResponse)
def run_prompt_eval(
    request: PromptEvalRunRequest,
) -> PromptEvalRunResponse:
    try:
        custom_cases = (
            [case.model_dump() for case in request.cases]
            if request.cases is not None
            else None
        )

        result = prompt_eval_service.run_prompt_eval(
            prompt_version=request.prompt_version,
            case_limit=request.case_limit,
            cases=custom_cases,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return PromptEvalRunResponse(**result)
