
from fastapi import APIRouter

from src.schemas.answer_schema import AnswerResponse
from src.schemas.ask_schema import AskRequest
from src.services.ask_service import ask_question

router = APIRouter()

@router.post("/ask", response_model=AnswerResponse)
async def ask(request : AskRequest) -> AnswerResponse:
    result = ask_question(request.question)
    return AnswerResponse(**result)

