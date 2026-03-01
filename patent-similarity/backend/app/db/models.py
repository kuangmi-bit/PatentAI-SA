"""
SQLAlchemy models for patent database
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Float, DateTime, JSON, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class LibraryModel(Base):
    """Patent library model"""
    __tablename__ = "libraries"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    patent_count: Mapped[int] = mapped_column(Integer, default=0)
    size_mb: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patents: Mapped[List["PatentModel"]] = relationship("PatentModel", back_populates="library", lazy="selectin")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "patent_count": self.patent_count,
            "size_mb": self.size_mb,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PatentModel(Base):
    """Patent document model"""
    __tablename__ = "patents"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    library_id: Mapped[str] = mapped_column(String(50), ForeignKey("libraries.id"), nullable=False)
    
    # Patent metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    application_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    publication_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ipc: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    applicant: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    inventors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Patent content
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    claims: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # File info
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, default=0)  # File size in bytes
    
    # Embedding (stored as JSON for flexibility)
    embedding: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    embedding_dimensions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Extraction quality
    extraction_quality: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    library: Mapped["LibraryModel"] = relationship("LibraryModel", back_populates="patents")
    
    def to_dict(self, include_embedding: bool = False) -> dict:
        result = {
            "id": self.id,
            "library_id": self.library_id,
            "title": self.title,
            "application_no": self.application_no,
            "publication_no": self.publication_no,
            "ipc": self.ipc,
            "applicant": self.applicant,
            "inventors": self.inventors or [],
            "abstract": self.abstract,
            "claims": self.claims or [],
            "description": self.description,
            "file_name": self.file_name,
            "extraction_quality": self.extraction_quality,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_embedding and self.embedding:
            result["embedding"] = self.embedding
        return result


class TargetPatentModel(Base):
    """Target patent for analysis task (not in any library)"""
    __tablename__ = "target_patents"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(50), ForeignKey("tasks.id"), nullable=False, unique=True)
    
    # Patent metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    application_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    publication_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ipc: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    applicant: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    inventors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Patent content
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    claims: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # File info
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    
    # Embedding (optional, for advanced usage)
    embedding: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    embedding_dimensions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Extraction quality
    extraction_quality: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_embedding: bool = False) -> dict:
        result = {
            "id": self.id,
            "task_id": self.task_id,
            "title": self.title,
            "application_no": self.application_no,
            "publication_no": self.publication_no,
            "ipc": self.ipc,
            "applicant": self.applicant,
            "inventors": self.inventors or [],
            "abstract": self.abstract,
            "claims": self.claims or [],
            "description": self.description,
            "file_name": self.file_name,
            "extraction_quality": self.extraction_quality,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_embedding and self.embedding:
            result["embedding"] = self.embedding
        return result


class TaskModel(Base):
    """Analysis task model"""
    __tablename__ = "tasks"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    
    # Task configuration
    library_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("libraries.id"), nullable=True)
    target_patent_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("patents.id"), nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Task stages (stored as JSON)
    stages: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Result
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "library_id": self.library_id,
            "target_patent_id": self.target_patent_id,
            "owner_id": self.owner_id,
            "stages": self.stages or [],
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class SimilarityResultModel(Base):
    """Similarity analysis result model"""
    __tablename__ = "similarity_results"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(50), ForeignKey("tasks.id"), nullable=False)
    
    # Target patent
    target_patent_id: Mapped[str] = mapped_column(String(50), ForeignKey("patents.id"), nullable=False)
    
    # Comparison patent
    comparison_patent_id: Mapped[str] = mapped_column(String(50), ForeignKey("patents.id"), nullable=False)
    
    # Similarity scores
    similarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    technical_field_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    technical_problem_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    technical_solution_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Risk assessment
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    
    # Matched features
    matched_features: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Analysis text
    analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "target_patent_id": self.target_patent_id,
            "comparison_patent_id": self.comparison_patent_id,
            "similarity_score": self.similarity_score,
            "technical_field_score": self.technical_field_score,
            "technical_problem_score": self.technical_problem_score,
            "technical_solution_score": self.technical_solution_score,
            "risk_level": self.risk_level,
            "matched_features": self.matched_features or [],
            "analysis": self.analysis,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
