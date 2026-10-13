"""
Vector Store for AegisAudit AI.
Provides persistent indexing, disk serialization, metadata tracking, and similarity search.
"""

import pickle
from pathlib import Path
from typing import List, Tuple
import numpy as np
from models.document_schema import DocumentChunk
from rag.embeddings import BaseEmbeddingProvider, get_embedding_provider
from core.config import settings
from core.logger import logger

class AuditVectorStore:
    def __init__(self, embedding_provider: BaseEmbeddingProvider = None):
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.chunks: List[DocumentChunk] = []
        self.vectors: np.ndarray = np.empty((0, 384), dtype=np.float32)
        self.faiss_index = None

    def add_chunks(self, chunks: List[DocumentChunk]):
        """Embeds and indexes document chunks."""
        if not chunks:
            return

        texts = [c.content for c in chunks]
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.embedding_provider.embed_documents(texts)
        new_vecs = np.array(embeddings, dtype=np.float32)

        # Normalize for cosine similarity
        norms = np.linalg.norm(new_vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        new_vecs = new_vecs / norms

        if self.vectors.shape[0] == 0:
            self.vectors = new_vecs
        else:
            self.vectors = np.vstack([self.vectors, new_vecs])

        self.chunks.extend(chunks)

        # Build or update FAISS index if available
        try:
            import faiss
            dim = self.vectors.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(self.vectors)
            logger.info(f"FAISS index built successfully with {self.faiss_index.ntotal} vectors.")
        except Exception as e:
            logger.info(f"FAISS not used ({e}); using NumPy cosine similarity.")

    def search(self, query: str, top_k: int = 4) -> List[Tuple[DocumentChunk, float]]:
        """
        Searches the index for chunks closest to the query.
        Returns list of (DocumentChunk, score) tuples.
        """
        if not self.chunks or self.vectors.shape[0] == 0:
            return []

        query_vec = np.array(self.embedding_provider.embed_query(query), dtype=np.float32)
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec /= norm

        if self.faiss_index is not None:
            q_arr = np.expand_dims(query_vec, axis=0)
            scores, indices = self.faiss_index.search(q_arr, min(top_k, len(self.chunks)))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks) and idx >= 0:
                    results.append((self.chunks[idx], float(score)))
            return results

        # NumPy cosine similarity fallback
        sims = np.dot(self.vectors, query_vec)
        top_indices = np.argsort(sims)[::-1][:top_k]
        return [(self.chunks[idx], float(sims[idx])) for idx in top_indices]

    def save(self, file_path: Path):
        """Serializes the vector store and metadata to disk."""
        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "chunks": self.chunks,
            "vectors": self.vectors
        }
        with open(path_obj, "wb") as f:
            pickle.dump(payload, f)
        logger.info(f"Saved vector store with {len(self.chunks)} chunks to {path_obj}")

    @classmethod
    def load(cls, file_path: Path, embedding_provider: BaseEmbeddingProvider = None) -> "AuditVectorStore":
        """Loads a serialized vector store from disk."""
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Vector store not found: {file_path}")

        store = cls(embedding_provider=embedding_provider)
        with open(path_obj, "rb") as f:
            payload = pickle.load(f)

        store.chunks = payload["chunks"]
        store.vectors = payload["vectors"]

        try:
            import faiss
            if store.vectors.shape[0] > 0:
                dim = store.vectors.shape[1]
                store.faiss_index = faiss.IndexFlatIP(dim)
                store.faiss_index.add(store.vectors)
        except Exception:
            pass

        logger.info(f"Loaded vector store with {len(store.chunks)} chunks from {path_obj}")
        return store
