from pydantic import BaseModel


class DocumentIngestRequest(BaseModel):
    filename: str


class DocumentIngestResponse(BaseModel):
    path: str
    document_count: int
    chunk_count: int
    stored_count: int
