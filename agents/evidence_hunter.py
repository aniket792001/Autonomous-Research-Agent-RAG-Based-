"""
Evidence Hunter Agent for AegisAudit AI.
Enhanced in Phase 4 with Hybrid Search (BM25 + Dense Vectors) and Agentic Self-Reflection.
"""

from typing import List, Tuple
from models.audit_schema import ClauseRequirement, Citation
from models.document_schema import DocumentChunk
from rag.vector_store import AuditVectorStore
from rag.hybrid_search import HybridRetriever
from core.logger import logger
from core.config import settings

class EvidenceHunterAgent:
    def __init__(self, vector_store: AuditVectorStore):
        self.vector_store = vector_store
        self.hybrid_retriever = HybridRetriever(vector_store)

    def gather_evidence(self, clause: ClauseRequirement, top_k: int = None) -> Tuple[str, List[Citation]]:
        """
        Retrieves relevant policy passages using Hybrid RAG (BM25 + Dense) with Self-Reflection query expansion.
        """
        k = top_k or settings.EVIDENCE_TOP_K
        primary_query = f"{clause.clause_id} {clause.title} {clause.description}"
        
        # 1. Primary Hybrid Search
        results: List[Tuple[DocumentChunk, float]] = self.hybrid_retriever.hybrid_search(primary_query, top_k=k)
        
        # 2. Agentic Self-Reflection & Query Expansion
        # If fewer than 2 results or low relevance, expand with conceptual keywords
        if len(results) < 2:
            alt_query = f"{clause.category} policy standard requirement procedure {clause.title}"
            logger.info(f"EvidenceHunterAgent: Low initial recall for {clause.clause_id}. Triggering reflection query: '{alt_query}'")
            extra_results = self.hybrid_retriever.hybrid_search(alt_query, top_k=2)
            # Merge and deduplicate
            seen_ids = {c.chunk_id for c, _ in results}
            for chunk, score in extra_results:
                if chunk.chunk_id not in seen_ids:
                    results.append((chunk, score))
                    seen_ids.add(chunk.chunk_id)

        if not results:
            logger.info(f"EvidenceHunterAgent: No corresponding evidence found for clause {clause.clause_id}")
            return "No corresponding policy statements or controls found in the document.", []

        evidence_snippets = []
        citations: List[Citation] = []
        seen_pages = set()

        for chunk, score in results:
            evidence_snippets.append(f"[Page {chunk.page_number}]: {chunk.content}")
            if (chunk.document_name, chunk.page_number) not in seen_pages:
                seen_pages.add((chunk.document_name, chunk.page_number))
                citations.append(
                    Citation(
                        document_name=chunk.document_name,
                        page_number=chunk.page_number,
                        matched_snippet=chunk.content[:200] + ("..." if len(chunk.content) > 200 else "")
                    )
                )

        combined_evidence = "\n\n".join(evidence_snippets)
        logger.info(f"EvidenceHunterAgent: Retrieved {len(citations)} citations for {clause.clause_id}")
        return combined_evidence, citations
