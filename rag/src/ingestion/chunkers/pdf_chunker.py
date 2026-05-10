from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import config
def chunk_pdf(documents : list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks: list[Document] = []
    for document in documents:
        page = document.metadata.get("page" , 0)
        metadata = {
            **document.metadata,
            "doc_type" : "pdf",
            "section_path": f"page_{page + 1}",
        }

        sub_doc = splitter.create_documents(
            texts=[document.page_content],
            metadatas=[metadata],
        )

        chunks.extend(sub_doc)

    return chunks