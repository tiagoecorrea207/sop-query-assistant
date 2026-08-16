from sqlalchemy import (
    create_engine, Column, String, Text,
    DateTime, Integer, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user:pass@localhost:5432/sopdb"
)

engine       = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()


class DocumentChunk(Base):
    """Mirrors the pgvector collection — used for metadata queries."""
    __tablename__ = "document_chunks"

    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename  = Column(String(256), nullable=False)
    doc_type  = Column(String(32), nullable=False)   # sop | audit_criteria | web
    chunk_idx = Column(Integer, nullable=False)
    content   = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    """Logs every query for audit trail and evaluation."""
    __tablename__ = "query_logs"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question       = Column(Text, nullable=False)
    answer         = Column(Text, nullable=True)
    response_type  = Column(String(32), nullable=True)  # answer|not_found|out_of_context
    sources        = Column(JSON, default=list)
    tokens_used    = Column(Integer, default=0)
    created_at     = Column(DateTime, default=datetime.utcnow)


def init_db():
    with engine.connect() as conn:
        conn.execute(__import__('sqlalchemy').text(
            "CREATE EXTENSION IF NOT EXISTS vector"
        ))
        conn.commit()
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
