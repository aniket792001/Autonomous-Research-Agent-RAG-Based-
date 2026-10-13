"""
Core configuration and settings for AegisAudit AI.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    # App Information
    APP_NAME: str = "AegisAudit AI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Autonomous Regulatory & Compliance Intelligence Platform"

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    HF_MODEL_NAME: str = os.getenv("HF_MODEL_NAME", "google/flan-t5-base")
    HF_EMBEDDING_MODEL: str = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Storage Paths
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
    CACHE_DIR: Path = BASE_DIR / os.getenv("CACHE_DIR", "data/cache")
    DB_DIR: Path = BASE_DIR / os.getenv("DB_DIR", "data/db")

    # Agent Tunings
    MAX_CLAUSES_PER_AUDIT: int = int(os.getenv("MAX_CLAUSES_PER_AUDIT", "25"))
    EVIDENCE_TOP_K: int = int(os.getenv("EVIDENCE_TOP_K", "4"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    @classmethod
    def ensure_directories(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.DB_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
