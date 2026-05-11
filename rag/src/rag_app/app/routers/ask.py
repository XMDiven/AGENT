
from fastapi import APIRouter

from rag_app.schemas.answer_schema import AnswerResponse
from rag_app.schemas.ask_schema import AskRequest
from rag_app.services.ask_service import ask_question

router = APIRouter()

@router.post("/ask", response_model=AnswerResponse)
async def ask(request : AskRequest) -> AnswerResponse:
    result = ask_question(request.question)
    return AnswerResponse(**result)

