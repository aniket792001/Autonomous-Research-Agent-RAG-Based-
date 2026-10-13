"""
SQLAlchemy Session and Connection Management for AegisAudit AI.
Supports SQLite (default) and PostgreSQL via DATABASE_URL.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.db_models import Base
from core.config import settings
from core.logger import logger

# Database connection URL (defaults to SQLite in data/db/)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{settings.DB_DIR}/aegisaudit_orm.db")

# SQLite specific connect args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes tables in database."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully with URL: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def get_db():
    """FastAPI request-scoped dependency providing a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auto-initialize on import
init_db()
