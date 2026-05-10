
import os
from pathlib import Path

import dotenv

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"

dotenv.load_dotenv(PROJECT_ROOT / ".env")
CHUNK_SIZE: int = 800
CHUNK_OVERLAP: int = 100
RETRIEVAL_TOP_K: int = 5

COLLECTION_NAME: str | None = os.getenv("QDRANT_COLLECTION")




FALLBACK_ANSWER: str = (
    "我无法仅根据当前检索到的上下文可靠回答这个问题。"
)

DEFAULT_SYSTEM_PROMPT: str = """
You are a RAG assistant.
Answer the user's question only based on the provided context.
If the context is not enough, say you do not know.
Keep the answer concise and accurate.
""".strip()
