from fastapi import APIRouter

from agent_app.schemas.run import AgentToolResponse
from agent_app.tools.registry import list_tools

router = APIRouter()


@router.get("/agent/tools", response_model=list[AgentToolResponse])
async def list_agent_tools() -> list[AgentToolResponse]:
    return [
        AgentToolResponse(
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
        )
        for tool in list_tools()
    ]
