"""
Pydantic schemas for document metadata and chunking.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    chunk_id: str
    document_name: str
    page_number: int
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentMetadata(BaseModel):
    file_name: str
    file_type: str
    total_pages: int
    total_chunks: int
    file_size_bytes: int
    created_at: str
