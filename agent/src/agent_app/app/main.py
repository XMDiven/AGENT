from fastapi import FastAPI

from agent_app.app.routers.run import router

app = FastAPI()
app.include_router(router)
