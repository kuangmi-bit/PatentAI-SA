"""
Pydantic models for request/response schemas
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============== Enums ==============

class TaskStatus(str, Enum):
    """Task execution status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    QUEUED = "queued"
    PARSING = "parsing"
    EXTRACTING = "extracting"
    EMBEDDING = "embedding"
    SEARCHING = "searching"
    RERANKING = "reranking"
    REPORTING = "reporting"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class RiskLevel(str, Enum):
    """Patent infringement risk level"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============== Base Models ==============

class PatentInfo(BaseModel):
    """Patent basic information"""
    title: str = Field(description="Patent title")
    application_no: Optional[str] = Field(None, description="Application number")
    publication_no: Optional[str] = Field(None, description="Publication number")
    ipc: Optional[str] = Field(None, description="IPC classification")
    applicant: Optional[str] = Field(None, description="Applicant name")
    inventors: Optional[List[str]] = Field(None, description="Inventor names")
    abstract: Optional[str] = Field(None, description="Patent abstract")
    claims: Optional[List[str]] = Field(None, description="Patent claims")
    description: Optional[str] = Field(None, description="Patent description")
    extraction_quality: Optional[int] = Field(None, description="Extraction quality score", ge=0, le=100)


class ScoreDetail(BaseModel):
    """Detailed score breakdown for a dimension"""
    dimension: str = Field(description="Scoring dimension name")
    score: float = Field(ge=0, le=100, description="Score for this dimension")
    weight: float = Field(ge=0, le=1, description="Weight of this dimension")
    weighted_score: float = Field(ge=0, le=100, description="Weighted contribution")
    reason: str = Field(description="Reasoning for this score")


class HighlightSegment(BaseModel):
    """Highlighted text segment in patent content"""
    text: str = Field(description="Highlighted text content")
    start_pos: int = Field(description="Start position in original text")
    end_pos: int = Field(description="End position in original text")
    field_type: str = Field(description="Field type: claims, abstract, description")
    similarity_to_target: float = Field(ge=0, le=100, description="Similarity to target patent segment")


class SimilarityResult(BaseModel):
    """Similarity analysis result for a single patent"""
    rank: int = Field(description="Similarity rank")
    patent_id: str = Field(description="Patent ID in database")
    title: str = Field(description="Patent title")
    application_no: Optional[str] = Field(None, description="Application number")
    similarity_score: float = Field(ge=0, le=100, description="Similarity score (0-100)")
    risk_level: RiskLevel = Field(description="Infringement risk level")
    matched_features: List[str] = Field(default=[], description="Matched technical features")
    # Detailed analysis
    score_details: Optional[List[ScoreDetail]] = Field(None, description="Detailed score breakdown")
    highlights: Optional[List[HighlightSegment]] = Field(None, description="Highlighted similar segments")
    analysis_summary: Optional[str] = Field(None, description="Overall analysis summary")
    # Patent content for display
    abstract: Optional[str] = Field(None, description="Patent abstract")
    claims: Optional[List[str]] = Field(None, description="Patent claims")
    ipc: Optional[str] = Field(None, description="IPC classification")


class TaskStage(BaseModel):
    """Task execution stage"""
    name: str = Field(description="Stage name")
    label: str = Field(description="Stage display label")
    status: str = Field(description="Stage status: pending, running, completed, failed")
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    detail: Optional[str] = Field(None, description="Stage detail message")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")


# ============== Request Models ==============

class CreateTaskRequest(BaseModel):
    """Create analysis task request"""
    name: str = Field(min_length=1, max_length=200, description="Task name")
    library_id: str = Field(description="Target patent library ID")
    config: Optional[Dict[str, Any]] = Field(
        default={},
        description="Analysis configuration"
    )


class UpdateTaskRequest(BaseModel):
    """Update task request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[TaskStatus] = None
    library_id: Optional[str] = Field(None, description="关联的专利库ID")


class SubmitTaskRequest(BaseModel):
    """Submit task with target patent info"""
    target_patent_id: Optional[str] = Field(None, description="Existing patent ID (optional)")
    target_patent_info: Optional[PatentInfo] = Field(None, description="Target patent info (if not in library)")
    target_patent_file_id: Optional[str] = Field(None, description="Uploaded file ID for target patent")


# ============== Response Models ==============

class TaskResponse(BaseModel):
    """Task response"""
    id: str = Field(description="Task ID")
    name: str = Field(description="Task name")
    status: TaskStatus = Field(description="Task status")
    progress: int = Field(ge=0, le=100, description="Overall progress")
    created_at: datetime = Field(description="Creation time")
    updated_at: datetime = Field(description="Last update time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    owner_id: Optional[str] = Field(None, description="Owner user ID")
    target_patent: Optional[PatentInfo] = Field(None, description="Target patent info")
    library_id: Optional[str] = Field(None, description="Library ID")
    library_name: Optional[str] = Field(None, description="Library name")
    stages: List[TaskStage] = Field(default=[], description="Execution stages")
    result: Optional[Dict[str, Any]] = Field(None, description="Analysis result")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class TaskListResponse(BaseModel):
    """Task list response"""
    total: int = Field(description="Total count")
    items: List[TaskResponse] = Field(description="Task list")


class AnalysisResultResponse(BaseModel):
    """Detailed analysis result response"""
    task_id: str = Field(description="Task ID")
    target_patent: PatentInfo = Field(description="Target patent")
    total_compared: int = Field(description="Total patents compared")
    successful_compared: int = Field(description="Successfully compared count")
    failed_compared: int = Field(description="Failed count")
    top_results: List[SimilarityResult] = Field(description="Top similarity results")
    generated_at: datetime = Field(description="Result generation time")


class LibraryCreate(BaseModel):
    """Create library request"""
    name: str = Field(min_length=1, max_length=255, description="Library name")
    description: Optional[str] = Field(None, description="Library description")


class LibraryUpdate(BaseModel):
    """Update library request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Library name")
    description: Optional[str] = Field(None, description="Library description")


class LibraryResponse(BaseModel):
    """Patent library response"""
    id: str = Field(description="Library ID")
    name: str = Field(description="Library name")
    description: Optional[str] = Field(None, description="Library description")
    patent_count: int = Field(default=0, description="Number of patents")
    size_mb: float = Field(default=0.0, description="Storage size in MB")
    created_at: datetime = Field(description="Creation time")
    updated_at: datetime = Field(description="Last update time")


class UploadResponse(BaseModel):
    """File upload response"""
    file_id: str = Field(description="File ID")
    file_name: str = Field(description="Original file name")
    file_size: int = Field(description="File size in bytes")
    file_path: str = Field(description="Stored file path")
    uploaded_at: datetime = Field(description="Upload time")


class ParsePatentResponse(BaseModel):
    """Patent parsing response"""
    file_id: str = Field(description="File ID")
    patent_info: PatentInfo = Field(description="Parsed patent information")
    quality_score: int = Field(ge=0, le=100, description="Parsing quality score")
    parsing_time: float = Field(description="Parsing time in seconds")


class SavePatentRequest(BaseModel):
    """Save patent to library request"""
    file_id: str = Field(description="Uploaded file ID")
    library_id: str = Field(description="Target library ID")
    patent_info: PatentInfo = Field(description="Patent information")
    quality_score: int = Field(ge=0, le=100, description="Parsing quality score")


class PatentResponse(BaseModel):
    """Patent document response"""
    id: str = Field(description="Patent ID")
    library_id: str = Field(description="Library ID")
    title: str = Field(description="Patent title")
    application_no: Optional[str] = Field(None, description="Application number")
    publication_no: Optional[str] = Field(None, description="Publication number")
    ipc: Optional[str] = Field(None, description="IPC classification")
    applicant: Optional[str] = Field(None, description="Applicant name")
    inventors: List[str] = Field(default=[], description="Inventor names")
    abstract: Optional[str] = Field(None, description="Patent abstract")
    quality_score: Optional[int] = Field(None, description="Parsing quality score")
    created_at: datetime = Field(description="Creation time")


# ============== Batch Import ==============

class BatchImportRequest(BaseModel):
    """Batch import request"""
    patents: List[Dict[str, Any]] = Field(description="List of patent data")
    generate_embeddings: bool = Field(default=True, description="Generate embeddings asynchronously")


class BatchImportResponse(BaseModel):
    """Batch import response"""
    total: int = Field(description="Total patents processed")
    success: int = Field(description="Successfully imported")
    failed: int = Field(description="Failed to import")
    errors: List[str] = Field(default=[], description="Error messages")
    patent_ids: List[str] = Field(default=[], description="Imported patent IDs")


# ============== Batch Import V2 ==============

class BatchImportStatusResponse(BaseModel):
    """批量导入状态响应"""
    import_id: str = Field(description="导入任务ID")
    status: str = Field(description="状态: running/completed/failed")
    message: str = Field(description="状态消息")
    total_files: int = Field(description="总文件数")
    processed_files: int = Field(description="已处理文件数")
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    errors: Optional[List[Dict[str, str]]] = Field(None, description="错误列表")


# ============== Health Check ==============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(description="Current timestamp")
