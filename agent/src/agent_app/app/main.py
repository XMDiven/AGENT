from fastapi import FastAPI

from agent_app.app.routers.health import router as health_router
from agent_app.app.routers.run import router as run_router
from agent_app.app.routers.tools import router as tools_router

app = FastAPI()
app.include_router(health_router)
app.include_router(run_router)
app.include_router(tools_router)
