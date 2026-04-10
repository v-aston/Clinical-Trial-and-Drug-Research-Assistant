from sqlalchemy import Column, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.session import Base

EMBEDDING_DIM = 384

class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(Text, primary_key=True)
    source_type = Column(Text, nullable=False, index=True)
    external_id = Column(Text, nullable=True, index=True)
    title = Column(Text, nullable=False)
    source_url = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Text, primary_key=True)
    document_id = Column(Text, ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    section = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("SourceDocument", back_populates="chunks")