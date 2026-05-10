from langchain_core.documents import Document

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from config import config
from src.ingestion.metadata_builder import build_markdown_metadata


def chunk_markdown(documents : list[Document]) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ],
        strip_headers=False,
    )

    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )

    chunks : list[Document] = []
    for doc in documents:
        header_docs = header_splitter.split_text(doc.page_content)
        for header_doc in header_docs:


            merged_metadata = build_markdown_metadata(
                document_metadata=doc.metadata,
                header_metadata=header_doc.metadata,
            )
            sub_docs = char_splitter.create_documents(
                texts=[header_doc.page_content],
                metadatas=[merged_metadata],
            )
            chunks.extend(sub_docs)

    return chunks

