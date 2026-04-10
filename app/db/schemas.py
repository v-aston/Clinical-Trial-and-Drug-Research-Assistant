from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal, List

class IngestRequest(BaseModel):
    source_type: Literal["clinicaltrials", "pubmed", "pdf"]
    query: Optional[str] = None
    urls: Optional[List[HttpUrl]] = None
    max_documents: int = Field(default=5, ge=1, le=50)

class IngestResponse(BaseModel):
    status: str
    source_type: str
    query: str
    documents_fetched: int
    documents_inserted: int
    chunks_created: int
    embeddings_created: int

class CitationOut(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    source_type: str
    source_url: Optional[str] = None
    chunk_index: int
    snippet: str
    distance: float

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)

class QueryResponse(BaseModel):
    answer: str
    citations: List[CitationOut]
    retrieved_chunks: int
    cached: bool = False