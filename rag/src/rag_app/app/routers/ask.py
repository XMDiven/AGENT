import json
from collections.abc import Iterator
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from rag_app.schemas.answer_schema import AnswerResponse
from rag_app.schemas.ask_schema import AskRequest
from rag_app.services.ask_service import ask_question, stream_ask_question

router = APIRouter()


def encode_stream_event(event: dict[str, Any]) -> str:
    return json.dumps(event, ensure_ascii=False) + "\n"


def stream_response_events(question: str) -> Iterator[str]:
    for event in stream_ask_question(question):
        yield encode_stream_event(event)


@router.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest) -> AnswerResponse:
    result = ask_question(request.question)
    return AnswerResponse(**result)


@router.post("/ask/stream")
async def ask_stream(request: AskRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_response_events(request.question),
        media_type="application/x-ndjson",
    )
