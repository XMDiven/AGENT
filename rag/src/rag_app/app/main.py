from fastapi import FastAPI

from rag_app.app.routers.ask import router as ask_router
from rag_app.app.routers.documents import router as document_router
from rag_app.app.routers.health import router as health_router
from rag_app.app.routers.prompt_eval import router as prompt_eval_router

app = FastAPI()


app.include_router(ask_router)
app.include_router(health_router)
app.include_router(document_router)
app.include_router(prompt_eval_router)
