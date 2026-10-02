from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from pgvector.sqlalchemy import Vector
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"))
    chunk_text = Column(Text, nullable=False)
    
    # 384 dimensions is typical for all-MiniLM-L6-v2, adjust if using larger models
    embedding = Column(Vector(384))
    
    document = relationship("Document", back_populates="chunks")

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"))
    overall_similarity = Column(Float)
    originality = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    matches = relationship("Match", back_populates="analysis", cascade="all, delete-orphan")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"))
    text_segment = Column(Text)
    matched_text = Column(Text)
    similarity_score = Column(Float)
    match_type = Column(String)  # Exact, Fuzzy, Semantic
    source_name = Column(String)
    
    analysis = relationship("Analysis", back_populates="matches")
