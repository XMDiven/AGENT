from typing import Any

from fastapi import APIRouter, HTTPException

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
