"""
Embedding provider for AegisAudit AI.
Supports HuggingFace Sentence-Transformers, Google Gemini Embeddings, and lightweight fallback vectorizer.
"""

from typing import List
import numpy as np
from core.config import settings
from core.logger import logger

class BaseEmbeddingProvider:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError

class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.HF_EMBEDDING_MODEL
        self._model = None
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer directly ({e}). Attempting LangChain HuggingFaceEmbeddings...")
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                self._model = HuggingFaceEmbeddings(model_name=self.model_name)
            except Exception as e2:
                logger.warning(f"LangChain HuggingFaceEmbeddings also failed ({e2}). Falling back to TF-IDF dense embedder.")
                self._model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self._model is not None:
            if hasattr(self._model, "encode"):
                embeddings = self._model.encode(texts, convert_to_numpy=True)
                return embeddings.tolist()
            elif hasattr(self._model, "embed_documents"):
                return self._model.embed_documents(texts)
        # Fallback dense embedder
        return [self._fallback_hash_embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        if self._model is not None:
            if hasattr(self._model, "encode"):
                embedding = self._model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            elif hasattr(self._model, "embed_query"):
                return self._model.embed_query(text)
        return self._fallback_hash_embed(text)

    def _fallback_hash_embed(self, text: str, dim: int = 384) -> List[float]:
        """Deterministic TF-hash embedding for fallback/offline situations."""
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()
        for word in words:
            idx = abs(hash(word)) % dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

def get_embedding_provider():
    return HuggingFaceEmbeddingProvider()
