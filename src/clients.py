import os

import dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient

from  src import config
dotenv.load_dotenv()



def get_client() -> ChatOpenAI:

    client = ChatOpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        model=os.getenv("LLM_MODEL_ID"),
    )
    return client
def get_embeddings()-> OllamaEmbeddings:
    return OllamaEmbeddings(
        base_url=os.getenv("EMBEDDING_BASE_URL"),
        model=os.getenv("EMBEDDING_MODEL"),
    )
def get_vector_store() -> QdrantVectorStore:
    client = QdrantClient(url=os.getenv("QDRANT_URL"))
    return QdrantVectorStore(
        client=client,
        collection_name=config.COLLECTION_NAME,
        embedding=get_embeddings(),
    )
