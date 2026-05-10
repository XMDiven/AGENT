from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.health import router as health_router
app = FastAPI()


app.include_router(ask_router)
app.include_router(health_router)