from pydantic import BaseModel, Field


class KnowledgeUploadResponseDTO(BaseModel):
    message: str
    document_id: str
    job_title: str
    chunks_stored: int

class KnowledgeAddDTO(BaseModel):
    job_title: str = Field(min_length=1)
    jd_text: str = Field(min_length=1)

class KnowledgeAddResponseDTO(BaseModel):
    message: str
    document_id: str
    job_title: str
    chunks_stored: int

class KnowledgeSearchDTO(BaseModel):
    query: str = Field(min_length=1)
    job_title: str = Field(min_length=1)
    
class KnowledgeSearchResultDTO(BaseModel):
    document_id: str
    job_title: str
    score: float
    text: str

class KnowledgeSearchResponseDTO(BaseModel):
    query: str
    results: list[KnowledgeSearchResultDTO]