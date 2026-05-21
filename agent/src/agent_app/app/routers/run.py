from dataclasses import asdict

from fastapi import APIRouter

from agent_app.schemas.run import AgentRunRequest, AgentRunResponse
from agent_app.service import run_agent

router = APIRouter()


@router.post("/agent/run", response_model=AgentRunResponse)
async def run_agent_endpoint(request: AgentRunRequest) -> AgentRunResponse:
    result = run_agent(request.question)

    return AgentRunResponse(**asdict(result))
