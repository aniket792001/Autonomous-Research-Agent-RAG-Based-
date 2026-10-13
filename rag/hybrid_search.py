"""
Hybrid Search Engine for AegisAudit AI (Phase 4).
Combines Sparse BM25 Keyword Matching (for regulatory codes & clause IDs)
with Dense Semantic Vectors via Reciprocal Rank Fusion (RRF).
"""

import re
import math
from typing import List, Tuple, Dict, Any
from models.document_schema import DocumentChunk
from rag.vector_store import AuditVectorStore
from core.logger import logger

class BM25Retriever:
    """Lightweight in-memory BM25 index over document chunks."""
    def __init__(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        self.doc_len = [len(self._tokenize(c.content)) for c in chunks]
        self.avg_doc_len = sum(self.doc_len) / max(1, len(chunks))
        self.doc_freqs: Dict[str, int] = {}
        self.inverted_index: Dict[str, List[int]] = {}
        self.k1 = 1.5
        self.b = 0.75
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        # Keeps alphanumeric tokens and hyphens for codes like "A.9.2.1" or "ISO-27001"
        return [w.lower() for w in re.findall(r'[a-zA-Z0-9_\.\-]+', text)]

    def _build_index(self):
        for idx, chunk in enumerate(self.chunks):
            tokens = set(self._tokenize(chunk.content))
            for t in tokens:
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1
                if t not in self.inverted_index:
                    self.inverted_index[t] = []
                self.inverted_index[t].append(idx)

    def score(self, query: str) -> List[float]:
        q_tokens = self._tokenize(query)
        scores = [0.0] * len(self.chunks)
        num_docs = max(1, len(self.chunks))

        for t in q_tokens:
            if t not in self.doc_freqs:
                continue
            df = self.doc_freqs[t]
            # IDF calculation
            idf = math.log(1 + (num_docs - df + 0.5) / (df + 0.5))

            for doc_idx in self.inverted_index.get(t, []):
                content_tokens = self._tokenize(self.chunks[doc_idx].content)
                tf = content_tokens.count(t)
                dl = self.doc_len[doc_idx]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (dl / max(1.0, self.avg_doc_len)))
                scores[doc_idx] += idf * (numerator / denominator)

        return scores


class HybridRetriever:
    """
    Blends Dense Vector Search + Sparse BM25 via Reciprocal Rank Fusion (RRF).
    """
    def __init__(self, vector_store: AuditVectorStore):
        self.vector_store = vector_store
        self.bm25 = BM25Retriever(vector_store.chunks) if vector_store.chunks else None

    def hybrid_search(
        self,
        query: str,
        top_k: int = 4,
        dense_weight: float = 0.6
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Executes hybrid retrieval returning ranked (DocumentChunk, hybrid_score) pairs.
        """
        if not self.vector_store.chunks:
            return []

        # 1. Dense Semantic Search
        dense_results = self.vector_store.search(query, top_k=top_k * 2)
        dense_rank_map = {chunk.chunk_id: rank + 1 for rank, (chunk, _) in enumerate(dense_results)}

        # 2. Sparse BM25 Search
        bm25_rank_map = {}
        if self.bm25:
            bm25_scores = self.bm25.score(query)
            bm25_sorted_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k * 2]
            for rank, idx in enumerate(bm25_sorted_indices):
                if bm25_scores[idx] > 0:
                    bm25_rank_map[self.vector_store.chunks[idx].chunk_id] = rank + 1

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_k = 60
        combined_scores: Dict[str, float] = {}
        chunk_lookup = {c.chunk_id: c for c, _ in dense_results}
        for c in self.vector_store.chunks:
            chunk_lookup[c.chunk_id] = c

        all_candidate_ids = set(dense_rank_map.keys()).union(set(bm25_rank_map.keys()))
        for cid in all_candidate_ids:
            dense_rank = dense_rank_map.get(cid, 100)
            bm25_rank = bm25_rank_map.get(cid, 100)

            score = (dense_weight * (1.0 / (rrf_k + dense_rank))) + ((1.0 - dense_weight) * (1.0 / (rrf_k + bm25_rank)))
            combined_scores[cid] = score

        # Sort descending by fused score
        sorted_cids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = [(chunk_lookup[cid], score) for cid, score in sorted_cids if cid in chunk_lookup]

        logger.info(f"HybridRetriever: Retrieved {len(results)} chunks for query: '{query[:40]}...'")
        return results
