from pydantic import BaseModel
class SourceItem(BaseModel):
    source: str
    section_path: str
    snippet: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
