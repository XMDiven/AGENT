import os
import dotenv


from langchain_ollama import OllamaEmbeddings


dotenv.load_dotenv()
def get_embeddings()-> OllamaEmbeddings:
    return OllamaEmbeddings(
        base_url=os.getenv("EMBEDDING_BASE_URL"),
        model=os.getenv("EMBEDDING_MODEL"),
    )
