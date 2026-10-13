"""
Intelligent Text Splitter for AegisAudit AI.
Splits text into contextually overlapping chunks while strictly preserving page numbers and source citations.
"""

from typing import List, Dict, Any
from models.document_schema import DocumentChunk
from core.config import settings

class AuditTextSplitter:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def split_pages(self, pages: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        Takes raw page objects and outputs chunks with exact page numbering.
        """
        chunks: List[DocumentChunk] = []
        chunk_counter = 1

        for page_data in pages:
            page_num = page_data["page"]
            source = page_data["source"]
            text = page_data["text"]

            if not text:
                continue

            words = text.split()
            if not words:
                continue

            # Approximate word count for chunking (roughly 1.3 tokens per word)
            step = max(1, self.chunk_size // 5)
            overlap_words = max(1, self.chunk_overlap // 5)

            start = 0
            while start < len(words):
                end = min(start + step, len(words))
                chunk_words = words[start:end]
                chunk_str = " ".join(chunk_words)

                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{source}_p{page_num}_c{chunk_counter}",
                        document_name=source,
                        page_number=page_num,
                        content=chunk_str,
                        metadata={
                            "source": source,
                            "page": page_num,
                            "char_count": len(chunk_str)
                        }
                    )
                )
                chunk_counter += 1
                if end >= len(words):
                    break
                start += (step - overlap_words)

        return chunks
